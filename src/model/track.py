import json
import logging
import math

from pydantic import BaseModel, computed_field

from src.core.exceptions import TrackError
from src.core.file_tools import read_json


logger = logging.getLogger(__name__)


class TrackPoint(BaseModel):
    """ 单个经纬度点 """
    lat: float
    lng: float
    sortNum: int

    class Config:
        extra = "forbid"  # 禁止传入多余字段

    @staticmethod
    def distance_km(p1: "TrackPoint", p2: "TrackPoint") -> float:
        """使用Haversine公式计算地球上两经纬度点之间的球面距离(km)"""
        rad_lat1 = math.radians(p1.lat)
        rad_lat2 = math.radians(p2.lat)
        l1 = rad_lat1 - rad_lat2
        l2 = math.radians(p1.lng) - math.radians(p2.lng)
        d = 2 * math.asin(
            math.sqrt(
                math.pow(math.sin(l1 / 2), 2)
                + math.cos(rad_lat1)
                * math.cos(rad_lat2)
                * math.pow(math.sin(l2 / 2), 2)
            )
        )
        d *= 6378.13649  # 地球半径(km)
        return d


class Track(BaseModel):
    """轨迹数据的封装类"""

    track: list[TrackPoint]

    class Config:
        extra = "forbid"

    @classmethod
    def from_json(cls, file_path: str) -> "Track":
        try:
            return cls.model_validate_json(read_json(file_path))
        except Exception as e:
            raise TrackError(file_path) from e

    @computed_field
    @property
    def distance_km(self) -> float:
        distance = 0.0
        for p1, p2 in zip(self.track[:-1], self.track[1:]):
            distance += TrackPoint.distance_km(p1, p2)

        return distance

    def dump_json(self) -> str:
        return json.dumps(self.model_dump()["track"])
