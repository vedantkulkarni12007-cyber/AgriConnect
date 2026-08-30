import pytest
import uuid
from decimal import Decimal
from app.modules.lots.service import calculate_farmer_earnings
from app.models import Lot, Offer, User

@pytest.fixture
def mock_farmer_id(db_session, ensure_test_users):
    farmer = db_session.query(User).filter(User.email == "ramesh@demo.com").first()
    return str(farmer.id)

@pytest.fixture
def mock_buyer_id(db_session, ensure_test_users):
    buyer = db_session.query(User).filter(User.email == "buyer@demo.com").first()
    return str(buyer.id)

def test_calculate_farmer_earnings_success(db_session, mock_farmer_id, mock_buyer_id):
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        public_id=f"KL-LOT-{uuid.uuid4().hex[:10]}",
        owner_id=uuid.UUID(mock_farmer_id),
        crop_name="Wheat",
        grade="A",
        quantity=Decimal("100"),
        market_reference_price=Decimal("2800"),
        location_text="Test Loc"
    )
    db_session.add(lot)
    
    offer1 = Offer(
        id=uuid.uuid4(),
        lot_id=lot_id,
        buyer_id=uuid.UUID(mock_buyer_id),
        owner_id=uuid.UUID(mock_farmer_id),
        quantity=Decimal("100"),
        price_per_unit=Decimal("3100"),
    )
    offer2 = Offer(
        id=uuid.uuid4(),
        lot_id=lot_id,
        buyer_id=uuid.UUID(mock_buyer_id),
        owner_id=uuid.UUID(mock_farmer_id),
        quantity=Decimal("50"),
        price_per_unit=Decimal("3000"),
    )
    db_session.add(offer1)
    db_session.add(offer2)
    db_session.commit()
    
    result = calculate_farmer_earnings(db_session, str(lot_id), mock_farmer_id)
    assert result["market_value"] == 280000.0
    assert result["best_offer_value"] == 310000.0
    assert result["potential_additional_earnings"] == 30000.0

def test_calculate_farmer_earnings_no_offer(db_session, mock_farmer_id):
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        public_id=f"KL-LOT-{uuid.uuid4().hex[:10]}",
        owner_id=uuid.UUID(mock_farmer_id),
        crop_name="Wheat",
        grade="A",
        quantity=Decimal("100"),
        market_reference_price=Decimal("2800"),
        location_text="Test Loc"
    )
    db_session.add(lot)
    db_session.commit()
    
    with pytest.raises(ValueError, match="Lot has no buyer offers"):
        calculate_farmer_earnings(db_session, str(lot_id), mock_farmer_id)

def test_calculate_farmer_earnings_missing_market_price(db_session, mock_farmer_id):
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        public_id=f"KL-LOT-{uuid.uuid4().hex[:10]}",
        owner_id=uuid.UUID(mock_farmer_id),
        crop_name="Wheat",
        grade="A",
        quantity=Decimal("100"),
        market_reference_price=None,
        location_text="Test Loc"
    )
    db_session.add(lot)
    db_session.commit()
    
    with pytest.raises(ValueError, match="Lot has no market/reference price"):
        calculate_farmer_earnings(db_session, str(lot_id), mock_farmer_id)

def test_calculate_farmer_earnings_invalid_quantity(db_session, mock_farmer_id):
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        public_id=f"KL-LOT-{uuid.uuid4().hex[:10]}",
        owner_id=uuid.UUID(mock_farmer_id),
        crop_name="Wheat",
        grade="A",
        quantity=Decimal("100"),
        market_reference_price=Decimal("2800"),
        location_text="Test Loc"
    )
    db_session.add(lot)
    db_session.commit()
    
    lot.quantity = Decimal("0")
    with pytest.raises(ValueError, match="Invalid/zero quantity"):
        calculate_farmer_earnings(db_session, str(lot_id), mock_farmer_id)
        
def test_calculate_farmer_earnings_wrong_farmer(db_session, mock_farmer_id):
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        public_id=f"KL-LOT-{uuid.uuid4().hex[:10]}",
        owner_id=uuid.UUID(mock_farmer_id),
        crop_name="Wheat",
        grade="A",
        quantity=Decimal("100"),
        market_reference_price=Decimal("2800"),
        location_text="Test Loc"
    )
    db_session.add(lot)
    db_session.commit()
    
    other_farmer_id = str(uuid.uuid4())
    with pytest.raises(ValueError, match="Farmer doesn't own the lot"):
        calculate_farmer_earnings(db_session, str(lot_id), other_farmer_id)

def test_calculate_farmer_earnings_lot_not_exist(db_session):
    with pytest.raises(ValueError, match="Lot doesn't exist"):
        calculate_farmer_earnings(db_session, str(uuid.uuid4()), str(uuid.uuid4()))

def test_calculate_farmer_earnings_invalid_price(db_session, mock_farmer_id):
    lot_id = uuid.uuid4()
    lot = Lot(
        id=lot_id,
        public_id=f"KL-LOT-{uuid.uuid4().hex[:10]}",
        owner_id=uuid.UUID(mock_farmer_id),
        crop_name="Wheat",
        grade="A",
        quantity=Decimal("100"),
        market_reference_price=Decimal("0"),
        location_text="Test Loc"
    )
    db_session.add(lot)
    db_session.commit()
    
    with pytest.raises(ValueError, match="Invalid/zero price"):
        calculate_farmer_earnings(db_session, str(lot_id), mock_farmer_id)
