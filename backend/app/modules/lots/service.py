import uuid

from sqlalchemy.orm import Session

from app.models import Lot, Offer


def calculate_farmer_earnings(db: Session, lot_id: str, farmer_id: str) -> dict:
    """
    Calculate estimated earnings for an existing farmer produce lot.
    """
    try:
        u = uuid.UUID(lot_id)
        lot = db.query(Lot).filter(Lot.id == u).first()
    except ValueError:
        lot = db.query(Lot).filter(Lot.public_id == lot_id).first()

    if not lot:
        raise ValueError("Lot doesn't exist")

    if str(lot.owner_id) != str(farmer_id):
        raise ValueError("Farmer doesn't own the lot")

    if lot.quantity is None or lot.quantity <= 0:
        raise ValueError("Invalid/zero quantity")

    if lot.market_reference_price is None:
        raise ValueError("Lot has no market/reference price")

    if lot.market_reference_price <= 0:
        raise ValueError("Invalid/zero price")

    market_value = float(lot.quantity) * float(lot.market_reference_price)

    offers = db.query(Offer).filter(Offer.lot_id == lot.id).all()

    if not offers:
        raise ValueError("Lot has no buyer offers")

    best_offer_value = 0.0
    for o in offers:
        if o.quantity is not None and o.price_per_unit is not None:
            if o.quantity > 0 and o.price_per_unit > 0:
                val = float(o.quantity) * float(o.price_per_unit)
                if val > best_offer_value:
                    best_offer_value = val

    if best_offer_value == 0.0:
        raise ValueError("Lot has no buyer offers")

    potential_additional_earnings = best_offer_value - market_value

    return {
        "market_value": market_value,
        "best_offer_value": best_offer_value,
        "potential_additional_earnings": potential_additional_earnings,
    }
