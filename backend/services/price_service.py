# services/price_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Provides functions to query and filter price data.
# In DEMO_MODE these functions work entirely on the in-memory demo dataset.
# ─────────────────────────────────────────────────────────────────────────────

from data.demo_data import PRICES, CROPS, MARKETS


def get_all_prices(crop: str | None = None, market: str | None = None) -> list[dict]:
    """
    Return the LATEST price record for every (crop, market) combination.

    Parameters
    ----------
    crop   : Optional filter – e.g. 'Onion'. Case-insensitive.
    market : Optional filter – e.g. 'Nashik'. Case-insensitive.

    Returns
    -------
    A flat list of price dicts, each containing:
      crop, market, modal_price, min_price, max_price, volume, date
    """
    results = []

    # Normalise filters to lowercase for comparison
    crop_filter   = crop.strip().title()   if crop   else None
    market_filter = market.strip().title() if market else None

    for crop_name, markets_data in PRICES.items():
        # Skip this crop if a crop filter is active and doesn't match
        if crop_filter and crop_name != crop_filter:
            continue

        for market_name, price_series in markets_data.items():
            # Skip this market if a market filter is active and doesn't match
            if market_filter and market_name != market_filter:
                continue

            if price_series:
                # price_series[-1] is today's (most recent) record
                latest = price_series[-1].copy()
                latest["crop"]   = crop_name
                latest["market"] = market_name
                results.append(latest)

    return results


def get_price_history(crop: str, market: str, days: int = 15) -> list[dict]:
    """
    Return historical price records for a specific crop in a specific market.

    Parameters
    ----------
    crop   : Crop name (e.g. 'Tomato')
    market : Market name (e.g. 'Pune')
    days   : How many days of history to return (default 15, max 15 in demo)

    Returns
    -------
    List of price dicts sorted oldest → newest, tagged with crop and market.
    Empty list if the crop/market combination is not found.
    """
    crop_norm   = crop.strip().title()
    market_norm = market.strip().title()

    try:
        series = PRICES[crop_norm][market_norm]
    except KeyError:
        # Crop or market not found in demo data
        return []

    # Slice to the requested number of days from the end of the list
    history = series[-days:]

    # Attach crop and market labels to each record
    return [
        {**record, "crop": crop_norm, "market": market_norm}
        for record in history
    ]


def get_best_price(crop: str) -> dict:
    """
    Find the market offering the HIGHEST modal price for a given crop today.

    Parameters
    ----------
    crop : Crop name (e.g. 'Wheat')

    Returns
    -------
    A dict with: crop, best_market, modal_price, min_price, max_price, date
    Returns an empty dict if crop not found.

    Example
    -------
    >>> get_best_price('Onion')
    {'crop': 'Onion', 'best_market': 'Mumbai', 'modal_price': 1495, ...}
    """
    crop_norm = crop.strip().title()

    if crop_norm not in PRICES:
        return {}

    best_market = None
    best_price  = -1
    best_record = {}

    for market_name, price_series in PRICES[crop_norm].items():
        if price_series:
            today_record = price_series[-1]   # latest day
            if today_record["modal_price"] > best_price:
                best_price  = today_record["modal_price"]
                best_market = market_name
                best_record = today_record.copy()

    if best_market:
        best_record["crop"]        = crop_norm
        best_record["best_market"] = best_market
        return best_record

    return {}
