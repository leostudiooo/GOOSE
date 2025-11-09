from pydantic import BaseModel


class Route(BaseModel):
    """
    运动路线信息模型

    包含路线的基本信息、规则和时间限制等。
    """

    route_name: str  # 路线名称
    rule_id: str  # 规则ID
    plan_id: str  # 计划ID
    route_rule: str  # 路线规则（如校区名称）
    max_time: int  # 最大允许时间（分钟）
    min_time: int  # 最小要求时间（分钟）
    route_distance_km: float  # 路线距离（公里）
    rule_end_time: str  # 规则结束时间
    rule_start_time: str  # 规则开始时间
