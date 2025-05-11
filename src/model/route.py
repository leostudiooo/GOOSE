from pydantic import BaseModel


class Route(BaseModel):
    """路线信息"""

    route_name: str
    rule_id: str
    plan_id: str
    route_rule: str
    max_time: int
    min_time: int
    route_distance_km: float
    rule_end_time: str
    rule_start_time: str
