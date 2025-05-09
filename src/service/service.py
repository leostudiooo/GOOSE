import logging
from pathlib import Path

from src.client.api_client import APIClient
from src.model.exercise_record import ExerciseRecord
from src.model.route_info import RouteInfo
from src.model.system_config import SystemConfig
from src.model.track import Track
from src.model.user_config import UserConfig

logger = logging.getLogger(__name__)


class Service:
    def __init__(self):
        logger.info("正在读取配置文件")
        project_root = str(Path(__file__).parent.parent.parent)
        self.user_config_path = f"{project_root}/config/user.yaml"
        self.user_config = UserConfig.from_yaml(self.user_config_path)
        self.sys_config = SystemConfig.from_yaml(f"{project_root}/config/system.yaml")
        if self.user_config.custom_track == "":
            self.user_config.custom_track = (
                f"{project_root}/resources/default_tracks/{self.user_config.route}.json"
            )
        self.track = Track.from_json(self.user_config.custom_track)
        self.route_info = RouteInfo.from_json(
            f"{project_root}/resources/route_info/{self.user_config.route}.json"
        )

        self.client = APIClient(self.sys_config, self.user_config.token)

    def set_user_config(self, user_config: UserConfig):
        self.user_config = user_config
        self.client.set_token(self.user_config.token)

    def save_user_config(self):
        raise NotImplementedError("待实现")

    def do_upload(self) -> bool:
        logger.info("准备上传数据")
        self.client.check_tenant()
        self.client.check_token()
        record = ExerciseRecord(
            self.route_info,
            self.user_config,
            self.track,
            self.client.upload_start_image(self.user_config.start_image),
            self.client.upload_finish_image(self.user_config.finish_image),
        )
        record.set_id(self.client.upload_start_record(record.get_start_record()))
        is_success = self.client.upload_finish_record(record.get_finish_record())

        return is_success
