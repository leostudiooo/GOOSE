import logging
import shutil
from pathlib import Path
from typing import Tuple

from src.infrastructure import (
    APIClient,
    FileHandler,
    JSONModelStorage,
    YAMLModelStorage,
)
from src.model import Exercise, Headers, Route, Track, User, RouteGroup
from src.service.record_service import RecordService

logger = logging.getLogger(__name__)


class Service:
    """
    主要业务逻辑服务类
    
    此类包含了各种供 CLI 和 GUI 使用的业务方法，负责协调各个模型和服务的交互。
    """

    def __init__(self, config_dir: Path, default_tracks_dir: Path):
        """
        初始化服务
        
        Args:
            config_dir: 配置文件目录
            default_tracks_dir: 默认轨迹文件目录
        """
        sys_config_path = config_dir / "system.yaml"
        user_config_path = config_dir / "user.yaml"
        user_example_path = config_dir / "user_example.yaml"
        route_info_path = config_dir / "route_info.yaml"
        self.default_tracks_dir = default_tracks_dir
        self.route_group_storage = YAMLModelStorage(route_info_path, RouteGroup)
        self.headers_storage = YAMLModelStorage(sys_config_path, Headers)

        # 如果用户配置文件不存在，复制示例配置
        self._initialize_user_config(user_config_path, user_example_path)
        self.user_storage = YAMLModelStorage(user_config_path, User)

    def _initialize_user_config(self, user_config_path: Path, user_example_path: Path) -> None:
        """
        初始化用户配置文件
        
        如果用户配置文件不存在且示例配置存在，则复制示例配置。
        
        Args:
            user_config_path: 用户配置文件路径
            user_example_path: 示例配置文件路径
        """
        if not user_config_path.exists() and user_example_path.exists():
            logger.info(f"用户配置文件不存在，从 {user_example_path} 复制示例配置")
            shutil.copy(user_example_path, user_config_path)

    def get_headers(self) -> Headers:
        """
        从系统配置文件读取请求头信息
        
        Returns:
            Headers对象，包含所有请求头信息
        """
        return self.headers_storage.load()

    def save_headers(self, headers: Headers) -> None:
        """
        保存请求头信息到系统配置文件
        
        Args:
            headers: 要保存的Headers对象
        """
        self.headers_storage.save(headers)

    def get_user(self) -> User:
        """
        从用户配置文件读取用户信息
        
        Returns:
            User对象，包含用户配置
        """
        return self.user_storage.load()

    def save_user(self, user: User) -> None:
        """
        保存用户信息到用户配置文件
        
        Args:
            user: 要保存的User对象
        """
        self.user_storage.save(user)

    def get_route_names(self) -> list[str]:
        """
        获取所有路线组中路线名称列表
        
        Returns:
            路线名称列表
        """
        route_group = self.route_group_storage.load()
        return route_group.get_route_names()

    def validate(self) -> None:
        """
        验证系统配置文件和用户配置文件
        
        确保所有相关资源路径有效且数据合法，同时验证 tenant 和 token。
        任一环节验证失败将会抛出 AppError 的子异常。
        
        Raises:
            FileHandlerError: 当图片文件路径无效时
            APIResponseError: 当tenant或token验证失败时
            InvalidTokenError: 当token格式不正确时
        """
        user, headers = self._load_user_and_headers()
        
        self._validate_image_paths(user)
        self._validate_credentials(user, headers)

    def _validate_image_paths(self, user: User) -> None:
        """
        验证用户的开始和结束图片路径
        
        Args:
            user: 用户对象
            
        Raises:
            FileHandlerError: 当图片文件路径无效时
        """
        FileHandler(Path(user.start_image)).check_path()
        FileHandler(Path(user.finish_image)).check_path()

    def _validate_credentials(self, user: User, headers: Headers) -> None:
        """
        验证用户凭据（tenant和token）
        
        Args:
            user: 用户对象
            headers: 请求头对象
            
        Raises:
            APIResponseError: 当tenant或token验证失败时
        """
        client = self._make_client(user, headers)
        client.check_tenant()
        client.check_token()

    def upload(self) -> None:
        """
        加载并验证各种模型，执行上传操作
        
        上传出现错误时将抛出 AppError 的子异常。
        
        Raises:
            APIClientError: 当API请求失败时
            FileHandlerError: 当文件操作失败时
            ModelValidationError: 当模型验证失败时
        """
        user, headers, route, track = self._make_models()
        exercise = Exercise.get_from(user.date_time, track)

        client = self._make_client(user, headers)
        record_service = RecordService(client, exercise, route, user)
        record_service.upload()

    @staticmethod
    def _make_client(user: User, headers: Headers) -> APIClient:
        """
        创建API客户端实例
        
        Args:
            user: 用户对象，包含token
            headers: 请求头对象，包含各种请求头信息
            
        Returns:
            配置好的APIClient实例
        """
        return APIClient(
            headers.user_agent,
            headers.miniapp_version,
            headers.referer,
            headers.tenant,
            user.token,
        )

    def _load_user_and_headers(self) -> Tuple[User, Headers]:
        """
        加载用户配置和系统配置
        
        Returns:
            包含User和Headers对象的元组
        """
        user = self.user_storage.load()
        headers = self.headers_storage.load()
        user.validate_token()
        return user, headers

    def _load_route(self, user: User) -> Route:
        """
        根据用户配置加载路线信息
        
        Args:
            user: 用户对象，包含选择的路线名称
            
        Returns:
            路线对象
            
        Raises:
            RouteNotFoundError: 当路线不存在时
        """
        route_group = self.route_group_storage.load()
        return route_group.get_route(user.route)

    def _load_track(self, user: User, route: Route) -> Track:
        """
        加载轨迹数据
        
        根据用户配置决定使用自定义轨迹还是默认轨迹。
        
        Args:
            user: 用户对象，包含自定义轨迹配置
            route: 路线对象，用于获取默认轨迹文件名
            
        Returns:
            轨迹对象
            
        Raises:
            FileHandlerError: 当轨迹文件不存在或无法读取时
            ModelValidationError: 当轨迹数据格式不正确时
        """
        if user.custom_track_path == "":
            track_path = self.default_tracks_dir / f"{route.route_name}.json"
            logger.warning(f"未启用自定义轨迹, 将使用默认的轨迹文件 '{track_path}'")
        else:
            track_path = Path(user.custom_track_path)
        return JSONModelStorage(track_path, Track).load()

    def _make_models(self) -> Tuple[User, Headers, Route, Track]:
        """
        加载并验证所有必需的模型
        
        Returns:
            包含User、Headers、Route和Track对象的元组
            
        Raises:
            InvalidTokenError: 当token验证失败时
            RouteNotFoundError: 当路线不存在时
            FileHandlerError: 当文件操作失败时
            ModelValidationError: 当模型验证失败时
        """
        user, headers = self._load_user_and_headers()
        route = self._load_route(user)
        track = self._load_track(user, route)
        
        return user, headers, route, track
