# services/transaction_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Provides functions to query and update transaction records.
# In DEMO_MODE all data lives in the demo_data module (in-memory list).
# ─────────────────────────────────────────────────────────────────────────────

from data.demo_data import TRANSACTIONS

# Define the valid transaction stages in the correct progression order.
# A transaction must move forward through these stages in sequence.
VALID_STAGES: list[str] = [
    "offer_created",       # Buyer makes an offer
    "offer_accepted",      # Farmer accepts the offer
    "produce_dispatched",  # Farmer ships the produce
    "payment_pending",     # Produce received, payment awaited
    "payment_received",    # Payment confirmed by farmer
    "completed",           # Deal fully closed
]


def get_transactions(
    farmer_id: str | None = None,
    buyer_id:  str | None = None,
) -> list[dict]:
    """
    Return all transactions, optionally filtered by farmer or buyer.

    Parameters
    ----------
    farmer_id : Filter to transactions involving this farmer (e.g. 'F001')
    buyer_id  : Filter to transactions involving this buyer  (e.g. 'B002')

    Returns
    -------
    List of transaction dicts. Returns all if no filters provided.

    Example
    -------
    >>> txns = get_transactions(farmer_id='F001')
    >>> len(txns) >= 1
    True
    """
    results = TRANSACTIONS  # start with all transactions

    if farmer_id:
        results = [t for t in results if t.get("farmer_id") == farmer_id]

    if buyer_id:
        results = [t for t in results if t.get("buyer_id") == buyer_id]

    return results


def get_transaction_by_id(txn_id: str) -> dict | None:
    """
    Find a single transaction by its ID.

    Parameters
    ----------
    txn_id : Transaction ID string (e.g. 'T001')

    Returns
    -------
    The transaction dict, or None if not found.

    The returned dict also contains a 'timeline' key — a list of
    stage history entries with human-readable labels and timestamps.

    Example
    -------
    >>> txn = get_transaction_by_id('T001')
    >>> txn['current_stage']
    'produce_dispatched'
    """
    for txn in TRANSACTIONS:
        if txn.get("id") == txn_id:
            # Build a timeline with human-readable stage labels
            timeline = []
            for entry in txn.get("stage_history", []):
                stage = entry["stage"]
                timeline.append({
                    "stage":     stage,
                    "label":     _stage_label(stage),
                    "timestamp": entry["timestamp"],
                    # Mark whether this stage is already completed
                    "completed": True,
                })
            # Append the pending stages (not yet reached)
            reached_stages = {e["stage"] for e in txn.get("stage_history", [])}
            for stage in VALID_STAGES:
                if stage not in reached_stages:
                    timeline.append({
                        "stage":     stage,
                        "label":     _stage_label(stage),
                        "timestamp": None,
                        "completed": False,
                    })

            result = txn.copy()
            result["timeline"] = timeline
            return result

    return None


def update_transaction_stage(txn_id: str, new_stage: str) -> dict:
    """
    Advance a transaction to a new stage.

    Rules:
    - The new_stage must be a valid stage string.
    - The new_stage must come AFTER the current stage in VALID_STAGES order.
      (You can't go backwards in a transaction.)

    Parameters
    ----------
    txn_id    : Transaction ID (e.g. 'T001')
    new_stage : Target stage string (e.g. 'payment_pending')

    Returns
    -------
    Updated transaction dict on success.
    Dict with 'error' key on failure.

    Example
    -------
    >>> result = update_transaction_stage('T001', 'payment_pending')
    >>> result.get('error') is None
    True  (if T001 is currently at 'produce_dispatched')
    """
    from datetime import date

    # Validate the stage name
    if new_stage not in VALID_STAGES:
        return {
            "error": (
                f"Invalid stage '{new_stage}'. "
                f"Valid stages: {', '.join(VALID_STAGES)}"
            )
        }

    # Find the transaction
    for txn in TRANSACTIONS:
        if txn.get("id") == txn_id:
            current = txn.get("current_stage", "")

            # Make sure we're moving FORWARD in the stage sequence
            current_index = VALID_STAGES.index(current) if current in VALID_STAGES else -1
            new_index     = VALID_STAGES.index(new_stage)

            if new_index <= current_index:
                return {
                    "error": (
                        f"Cannot move from '{current}' to '{new_stage}'. "
                        f"Stage must move forward in the pipeline."
                    )
                }

            # Apply the stage update
            txn["current_stage"] = new_stage
            txn.setdefault("stage_history", []).append({
                "stage":     new_stage,
                "timestamp": date.today().isoformat(),
            })

            return txn

    return {"error": f"Transaction '{txn_id}' not found."}


def _stage_label(stage: str) -> str:
    """Convert a stage key to a user-friendly display label."""
    labels = {
        "offer_created":     "Offer Created",
        "offer_accepted":    "Offer Accepted",
        "produce_dispatched":"Produce Dispatched",
        "payment_pending":   "Payment Pending",
        "payment_received":  "Payment Received",
        "completed":         "Deal Completed",
    }
    return labels.get(stage, stage.replace("_", " ").title())
