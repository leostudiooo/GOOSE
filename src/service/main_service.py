import logging
from pathlib import Path

from src.infrastructure import (
    APIClient,
    FileHandler,
    YAMLModelStorage,
)
from src.model import Exercise, Headers, Track, User, RouteGroup, Route
from src.service.record_service import RecordService

logger = logging.getLogger(__name__)


class Service:
    """此类包含了各种供 CLI 和 GUI 使用的业务方法"""

    def __init__(self):
        self._default_tracks_path = Path("resources/default_tracks/")
        self._route_group_storage = YAMLModelStorage(Path("config/"), RouteGroup)
        self._headers_storage = YAMLModelStorage(Path("config/"), Headers)
        self._user_storage = YAMLModelStorage(Path("config/"), User)
        self._track_storage = YAMLModelStorage(self._default_tracks_path, Track)

    def get_headers(self) -> Headers:
        """从系统配置文件读取请求头信息"""
        return self._headers_storage.load("headers")

    def save_headers(self, headers: Headers):
        """保存请求头信息到系统配置文件"""
        self._headers_storage.save("headers", headers)

    def get_user(self) -> User:
        """从用户配置文件读取用户信息"""
        try:
            return self._user_storage.load("user")
        except:
            logger.warning("无法加载用户配置")
            return User.get_default()

    def save_user(self, user: User):
        """保存用户信息到用户配置文件"""
        self._user_storage.save("user", user)

    def get_route_names(self) -> list[str]:
        """获取所有路线组中路线名称列表"""
        route_group = self._route_group_storage.load("route_group")
        return route_group.get_route_names()

    def validate(self):
        """
        验证系统配置文件和用户配置文件，并确保所有相关资源路径有效且数据合法, 同时验证 tenant 和 token.

        任何一个环节验证失败将会抛出 AppError 的子异常.
        """
        user = self._user_storage.load("user")
        headers = self._headers_storage.load("headers")

        # TODO: 检查路径
        FileHandler(Path(user.start_image)).check_path()
        FileHandler(Path(user.finish_image)).check_path()

        client = self._construct_client(user, headers)
        client.check_tenant()
        client.check_token()

    def upload(self):
        """
        加载并验证各种模型, 执行上传操作. 上传出现错误时将抛出 AppError 的子异常
        """
        user = self._user_storage.load("user")
        headers = self._headers_storage.load("headers")
        route_group = self._route_group_storage.load("route_group")

        user.validate_token()
        route = route_group.get_route(user.route)
        track = self._load_track(route, user)
        exercise = Exercise.get_from(user.date_time, track)

        client = self._construct_client(user, headers)
        record_service = RecordService(client, exercise, route, user)
        record_service.upload()

    def _load_track(self, route: Route, user: User) -> Track:
        if user.custom_track_path == "":
            logger.warning(f"未启用自定义轨迹, 将使用默认的轨迹文件")
            track = self._track_storage.set_file_dir(self._default_tracks_path).load(route.route_name)
        else:
            track_path = Path(user.custom_track_path)
            track = self._track_storage.set_file_dir(track_path.parent).load(track_path.name.rstrip(".yaml"))
        return track

    @staticmethod
    def _construct_client(user: User, headers: Headers):
        return APIClient(headers.user_agent, headers.miniapp_version, headers.referer, headers.tenant, user.token)
