import base64
import json
from datetime import datetime

from pydantic import BaseModel, computed_field


class User(BaseModel):
    token: str
    date_time: datetime
    duration: int
    start_image: str
    finish_image: str
    route: str
    custom_track: str

    @computed_field
    @property
    def student_id(self) -> str:
        splits = self.token.split(".")
        if len(splits) != 3:
            raise ValueError("无效的token")
        try:
            decoded_token = base64.b64decode(splits[1] + "==")
            user_id = json.loads(decoded_token)["userid"]
        except Exception as e:
            raise ValueError("无效的token") from e

        return user_id
