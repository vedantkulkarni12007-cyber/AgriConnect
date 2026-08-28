# services/trend_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Calculates price trend indicators for crops.
# Uses simple statistical logic – no ML/AI – to classify trends as
# RISING, FALLING, or STABLE based on a percentage change threshold.
# ─────────────────────────────────────────────────────────────────────────────

from services.price_service import get_price_history, get_all_prices


# Threshold (%) beyond which price movement is labelled as directional
TREND_THRESHOLD_PERCENT = 3.0


def calculate_trend(prices_list: list[dict]) -> dict:
    """
    Analyse a list of price records and return trend indicators.

    The trend is calculated by comparing today's price against the
    7-day moving average of modal prices.

    Parameters
    ----------
    prices_list : List of price dicts (must have 'modal_price' key).
                  Should be sorted oldest → newest (index 0 = oldest).

    Returns
    -------
    dict with:
      - current_price     : latest modal price (INR/quintal)
      - moving_average    : 7-day average (float, rounded to 2 dp)
      - percentage_change : ((current - MA) / MA) * 100, rounded to 2 dp
      - trend             : 'RISING' | 'FALLING' | 'STABLE'
      - explanation       : Human-readable sentence describing the trend

    Returns an empty dict if fewer than 2 records are provided.
    """
    if not prices_list or len(prices_list) < 2:
        return {}

    # Extract just the modal price values
    modal_prices = [record["modal_price"] for record in prices_list]

    # Latest price is the last item in the sorted list
    current_price = modal_prices[-1]

    # 7-day moving average: use the last 7 prices (or all if fewer)
    window = modal_prices[-7:]
    moving_average = round(sum(window) / len(window), 2)

    # Percentage change: how much does current price differ from the MA?
    if moving_average == 0:
        percentage_change = 0.0
    else:
        percentage_change = round(
            ((current_price - moving_average) / moving_average) * 100, 2
        )

    # Classify the trend using the threshold
    if percentage_change > TREND_THRESHOLD_PERCENT:
        trend = "RISING"
        explanation = (
            f"Price is ₹{current_price}/quintal, which is {percentage_change:.1f}% "
            f"above the 7-day average of ₹{moving_average}/quintal. "
            f"Prices are trending upward — consider holding stock if storage is available."
        )
    elif percentage_change < -TREND_THRESHOLD_PERCENT:
        trend = "FALLING"
        explanation = (
            f"Price is ₹{current_price}/quintal, which is {abs(percentage_change):.1f}% "
            f"below the 7-day average of ₹{moving_average}/quintal. "
            f"Prices are declining — consider selling soon to avoid further losses."
        )
    else:
        trend = "STABLE"
        explanation = (
            f"Price is ₹{current_price}/quintal, close to the 7-day average of "
            f"₹{moving_average}/quintal (change: {percentage_change:+.1f}%). "
            f"Market is stable — monitor for 2–3 more days before deciding."
        )

    return {
        "current_price":     current_price,
        "moving_average":    moving_average,
        "percentage_change": percentage_change,
        "trend":             trend,
        "explanation":       explanation,
    }


def get_trend_for_crop(crop: str, market: str | None = None) -> dict:
    """
    Compute the trend for a specific crop, optionally in a specific market.

    If no market is specified, trends are averaged across ALL markets.

    Parameters
    ----------
    crop   : Crop name (e.g. 'Onion')
    market : Optional market name (e.g. 'Nashik')

    Returns
    -------
    A trend dict (same structure as calculate_trend output) with
    extra fields: crop, market (or 'All Markets')
    """
    crop_norm = crop.strip().title()

    if market:
        # Single market trend
        market_norm = market.strip().title()
        history = get_price_history(crop_norm, market_norm, days=15)

        if not history:
            return {
                "error": f"No price data found for {crop_norm} in {market_norm}."
            }

        result = calculate_trend(history)
        result["crop"]   = crop_norm
        result["market"] = market_norm
        return result

    else:
        # Multi-market: compute a synthetic average series across all markets
        # Step 1: Get today's latest prices across all markets for this crop
        all_latest = get_all_prices(crop=crop_norm)

        if not all_latest:
            return {"error": f"No price data found for crop: {crop_norm}"}

        # Step 2: Build a day-by-day average price series
        # We'll collect history from all markets and average per day
        from data.demo_data import PRICES, MARKETS

        if crop_norm not in PRICES:
            return {"error": f"Crop '{crop_norm}' not in demo data."}

        # Collect all 15-day series for this crop
        all_series: list[list[dict]] = [
            PRICES[crop_norm][mkt]
            for mkt in MARKETS
            if mkt in PRICES[crop_norm]
        ]

        if not all_series:
            return {"error": f"No market data for {crop_norm}."}

        # Average modal_price per day across all markets
        num_days = len(all_series[0])
        avg_series = []
        for day_i in range(num_days):
            day_prices = [series[day_i]["modal_price"] for series in all_series]
            avg_modal  = round(sum(day_prices) / len(day_prices))
            avg_series.append({
                "modal_price": avg_modal,
                "date": all_series[0][day_i]["date"],
            })

        result = calculate_trend(avg_series)
        result["crop"]   = crop_norm
        result["market"] = "All Markets"
        return result


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS  (commented examples – run manually to verify logic)
# ─────────────────────────────────────────────────────────────────────────────
#
# TEST 1: RISING trend
# prices = [{"modal_price": 1000}] * 7 + [{"modal_price": 1050}]
#   → 7-day avg ≈ 1006.25, current = 1050
#   → change = ((1050 - 1006.25) / 1006.25) * 100 ≈ +4.35%  → RISING ✓
# result = calculate_trend(prices)
# assert result["trend"] == "RISING"
#
# TEST 2: FALLING trend
# prices = [{"modal_price": 2000}] * 7 + [{"modal_price": 1900}]
#   → 7-day avg ≈ 1987.5, current = 1900
#   → change = ((1900 - 1987.5) / 1987.5) * 100 ≈ -4.4%  → FALLING ✓
# result = calculate_trend(prices)
# assert result["trend"] == "FALLING"
#
# TEST 3: STABLE trend
# prices = [{"modal_price": 5000}] * 8
#   → 7-day avg = 5000, current = 5000
#   → change = 0%  → STABLE ✓
# result = calculate_trend(prices)
# assert result["trend"] == "STABLE"
# assert result["percentage_change"] == 0.0
