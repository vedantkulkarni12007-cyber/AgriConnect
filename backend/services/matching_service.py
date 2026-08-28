# services/matching_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Rule-based buyer matching engine.
# No AI or ML — matches are scored using a transparent point system
# that farmers can understand and trust.
#
# Scoring breakdown (max 100 points):
#   40 pts – Crop match
#   25 pts – Grade match (A=25, B=15, C=5)
#   20 pts – Quantity compatibility (lot quantity within buyer's min/max)
#   15 pts – Distance / proximity
# ─────────────────────────────────────────────────────────────────────────────

from data.demo_data import BUYERS

# ── District adjacency map ────────────────────────────────────────────────────
# Lists neighbouring districts for proximity scoring.
# If the lot's district and buyer's district are the same → 15 pts
# If adjacent → 10 pts
# If same state but not adjacent → 5 pts
ADJACENT_DISTRICTS: dict[str, list[str]] = {
    "Nashik":     ["Ahmednagar", "Pune", "Aurangabad"],
    "Lasalgaon":  ["Nashik", "Ahmednagar"],   # Lasalgaon is a city in Nashik district
    "Ahmednagar": ["Nashik", "Pune", "Solapur", "Aurangabad"],
    "Pune":       ["Nashik", "Ahmednagar", "Solapur"],
    "Solapur":    ["Ahmednagar", "Pune", "Aurangabad"],
    "Aurangabad": ["Nashik", "Ahmednagar", "Solapur", "Nagpur"],
    "Nagpur":     ["Aurangabad"],
    "Mumbai":     ["Pune"],
}


def _score_crop(lot_crop: str, buyer_crops: list[str]) -> tuple[int, str | None]:
    """
    Award 40 points if the lot's crop is in the buyer's interest list.

    Returns (points, reason_string | None)
    """
    if lot_crop in buyer_crops:
        return 40, f"Buyer purchases {lot_crop}"
    return 0, None


def _score_grade(lot_grade: str, buyer_preferred_grade: str) -> tuple[int, str | None]:
    """
    Award grade-match points based on lot grade vs buyer's preferred grade.

    Grade A = 25 pts (premium)
    Grade B = 15 pts (standard)
    Grade C = 5  pts (acceptable)
    """
    grade_points = {"A": 25, "B": 15, "C": 5}
    grade = lot_grade.upper() if lot_grade else "C"
    points = grade_points.get(grade, 0)

    if grade == buyer_preferred_grade.upper():
        reason = f"Grade {grade} matches buyer preference"
    elif grade == "A":
        reason = f"Grade A produce (premium quality)"
    elif grade == "B":
        reason = f"Grade B produce (standard quality)"
    else:
        reason = f"Grade C produce (basic quality)"

    return points, reason


def _score_quantity(lot_qty: float, buyer_min: float, buyer_max: float) -> tuple[int, str | None]:
    """
    Award 20 points if the lot's quantity is within the buyer's acceptable range.
    Award 10 points if quantity is below minimum (buyer may still negotiate).
    Award 5  points if quantity is above maximum (buyer may partially purchase).
    """
    if buyer_min <= lot_qty <= buyer_max:
        return 20, f"Quantity {lot_qty}t fits buyer range ({buyer_min}–{buyer_max}t)"
    elif lot_qty < buyer_min:
        return 10, f"Quantity {lot_qty}t slightly below minimum {buyer_min}t (negotiable)"
    else:
        return 5, f"Quantity {lot_qty}t exceeds max {buyer_max}t (partial purchase possible)"


def _score_distance(
    lot_district: str,
    buyer_district: str,
    lot_state: str,
    buyer_state: str,
) -> tuple[int, str | None]:
    """
    Award proximity points based on geographic closeness.

    15 pts – Same district
    10 pts – Adjacent district
     5 pts – Same state, different region
     0 pts – Different state
    """
    lot_d   = lot_district.title()
    buyer_d = buyer_district.title()

    if lot_d == buyer_d:
        return 15, f"Same district ({lot_d}) – minimal transport cost"

    adjacent = ADJACENT_DISTRICTS.get(lot_d, [])
    if buyer_d in adjacent:
        return 10, f"Adjacent district – reasonable transport distance"

    if lot_state == buyer_state:
        return 5, f"Same state ({lot_state}) – intra-state transport"

    return 0, None


def _label_from_score(score: int) -> str:
    """
    Convert a numeric score to a human-readable match label.

    ≥ 75 → Excellent
    ≥ 50 → Good
    < 50 → Fair
    """
    if score >= 75:
        return "Excellent"
    elif score >= 50:
        return "Good"
    else:
        return "Fair"


def match_buyers(lot: dict) -> list[dict]:
    """
    Score all buyers against a lot and return a ranked list of matches.

    Parameters
    ----------
    lot : dict containing at minimum:
          crop, quantity, unit, grade, location, district, state

    Returns
    -------
    List of match dicts, sorted by score descending. Each dict contains:
      - buyer       : full buyer record
      - score       : int (0-100)
      - match_label : 'Excellent' | 'Good' | 'Fair'
      - match_reasons : list of human-readable reason strings
    """
    lot_crop     = lot.get("crop", "")
    lot_qty      = float(lot.get("quantity", 0))
    lot_grade    = lot.get("grade", "C")
    lot_district = lot.get("district", lot.get("location", ""))
    lot_state    = lot.get("state", "Maharashtra")

    matches = []

    for buyer in BUYERS:
        total_score   = 0
        match_reasons = []

        # ── 1. Crop match (40 pts) ────────────────────────────────────────────
        pts, reason = _score_crop(lot_crop, buyer["crops_interested"])
        total_score += pts
        if reason:
            match_reasons.append(reason)

        # If the crop doesn't match at all, skip this buyer to avoid noise
        if pts == 0:
            continue

        # ── 2. Grade match (25 pts) ───────────────────────────────────────────
        pts, reason = _score_grade(lot_grade, buyer.get("preferred_grade", "B"))
        total_score += pts
        if reason:
            match_reasons.append(reason)

        # ── 3. Quantity compatibility (20 pts) ────────────────────────────────
        pts, reason = _score_quantity(
            lot_qty,
            buyer.get("min_quantity", 0),
            buyer.get("max_quantity", 9999),
        )
        total_score += pts
        if reason:
            match_reasons.append(reason)

        # ── 4. Distance / proximity (15 pts) ─────────────────────────────────
        pts, reason = _score_distance(
            lot_district,
            buyer.get("district", buyer.get("location", "")),
            lot_state,
            buyer.get("state", "Maharashtra"),
        )
        total_score += pts
        if reason:
            match_reasons.append(reason)

        # ── Compose the match result ──────────────────────────────────────────
        matches.append({
            "buyer":         buyer,
            "score":         total_score,
            "match_label":   _label_from_score(total_score),
            "match_reasons": match_reasons,
        })

    # Sort by score descending – best match first
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches
