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
