
from pydantic import BaseModel


class MatchRequest(BaseModel):
    lot_id: str

class ComponentScores(BaseModel):
    crop: int
    grade: int
    quantity: int
    distance: int
    price: int
    time: int
    verification: int

class MatchResponse(BaseModel):
    id: str
    lot_id: str
    buyer_id: str
    buyer_name: str
    final_score: int
    component_scores: dict
    explanation: dict
    ruleset_version: str
