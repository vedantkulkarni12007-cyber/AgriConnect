from app.modules.matching.service import (
    calculate_crop_score, calculate_grade_score, calculate_quantity_score,
    calculate_distance_score, calculate_price_score, calculate_verification_score
)

def test_crop_score_match():
    s,_ = calculate_crop_score("Onion", ["Onion","Tomato"], {"crop":30})
    assert s==30

def test_crop_score_no_match():
    s,_ = calculate_crop_score("Onion", ["Tomato"], {"crop":30})
    assert s==0

def test_grade():
    s,_ = calculate_grade_score("A","A", {"grade":15})
    assert s==15
    s,_ = calculate_grade_score("B","A", {"grade":15})
    assert s in (10,15)

def test_quantity():
    s,_ = calculate_quantity_score(100, 50, 500, {"quantity":15})
    assert s==15
    s,_ = calculate_quantity_score(10, 50, 500, {"quantity":15})
    assert s<15

def test_distance():
    s,_ = calculate_distance_score(19.9975,73.7898,19.9975,73.7898, {"distance":15})
    assert s==15
    s,_ = calculate_distance_score(19.9975,73.7898,18.5204,73.8567, {"distance":15})
    assert 0 <= s <= 15

def test_verification():
    s,_ = calculate_verification_score(True, {"verification":10})
    assert s==10
    s,_ = calculate_verification_score(False, {"verification":10})
    assert s==0
