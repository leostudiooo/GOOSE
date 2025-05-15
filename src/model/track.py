import json
import math
from datetime import datetime

from pydantic import BaseModel


class TrackMetadata(BaseModel):
    totalDistance: float
    formattedDistance: str
    totalTime: int
    formattedTime: str
    sampleTimeInterval: int
    pointCount: int
    createdAt: datetime


class TrackPoint(BaseModel):
    """单个经纬度点"""

    lat: float
    lng: float
    sortNum: int

    def distance_with(self, other: "TrackPoint") -> float:
        """使用Haversine公式计算地球上两经纬度点之间的球面距离(km)"""
        rad_lat1 = math.radians(self.lat)
        rad_lat2 = math.radians(other.lat)
        l1 = rad_lat1 - rad_lat2
        l2 = math.radians(self.lng) - math.radians(other.lng)
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
    metadata: TrackMetadata

    def get_distance_km(self) -> float:
        distance = 0.0
        for p1, p2 in zip(self.track[:-1], self.track[1:]):
            distance += p1.distance_with(p2)

        return distance

    def get_track_str(self) -> str:
        return json.dumps(self.model_dump()["track"])

    def get_duration_sec(self) -> int:
        return self.metadata.totalTime
