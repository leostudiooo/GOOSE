import math

from pydantic import BaseModel


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
