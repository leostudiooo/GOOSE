from pydantic import BaseModel, Field

from src.core.exceptions import RouteInfoError
from src.core.file_tools import read_json


class RouteInfo(BaseModel):
    """ 路线信息"""
    route_name: str = Field(..., alias="routeName")
    rule_id: str = Field(..., alias="ruleId")
    plan_id: str = Field(..., alias="planId")
    route_rule: str = Field(..., alias="routeRule")
    max_time: int = Field(..., alias="maxTime")
    min_time: int = Field(..., alias="minTime")
    route_distance_km: float = Field(..., alias="orouteKilometre")
    rule_end_time: str = Field(..., alias="ruleEndTime")
    rule_start_time: str = Field(..., alias="ruleStartTime")

    class Config:
        validate_by_name = True

    @classmethod
    def from_json(cls, file_path: str) -> "RouteInfo":
        try:
            return cls.model_validate_json(read_json(file_path))
        except Exception as e:
            raise RouteInfoError(file_path) from e
