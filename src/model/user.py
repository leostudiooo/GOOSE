import base64
import json
from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel, Field, field_validator

from src.infrastructure.constants import TOKEN_PARTS_COUNT, TOKEN_USERID_FIELD
from src.infrastructure.exceptions import InvalidTokenError


class CustomTrack(BaseModel):
    """
    自定义轨迹配置模型
    
    用于配置是否使用自定义轨迹以及轨迹文件路径。
    """
    enable: bool = False  # 是否启用自定义轨迹
    file_path: str = ""  # 自定义轨迹文件路径


class User(BaseModel):
    """
    用户配置模型
    
    包含用户的认证信息、运动偏好和图片配置等。
    """
    token: str  # 用户认证令牌
    date_time: datetime  # 运动时间
    start_image: str  # 开始运动图片路径
    finish_image: str  # 结束运动图片路径
    route: str  # 选择的路线名称
    custom_track: Union[str, CustomTrack] = Field(default_factory=CustomTrack)  # 自定义轨迹配置

    @field_validator("custom_track", mode="before")
    @classmethod
    def validate_custom_track(cls, v: Any) -> Union[str, CustomTrack]:
        """
        验证并转换custom_track字段
        
        处理字符串类型的custom_track，转换为CustomTrack对象。
        空字符串转换为禁用状态，非空字符串转换为启用状态。
        
        Args:
            v: custom_track的原始值
            
        Returns:
            CustomTrack对象或原始值
        """
        # 处理字符串类型的custom_track, 转换为CustomTrack对象
        if isinstance(v, str):
            if v:
                return CustomTrack(enable=True, file_path=v)
            return CustomTrack()
        return v

    def validate_token(self) -> None:
        """
        验证 token 的格式和内容。
        
        该方法检查 token 是否由点分隔的三个部分组成, 
        对来自Base64的第二部分 (有效载荷) 进行解码, 并验证其是否包含必填的“userid”字段。

        :raises
        InvalidTokenError：如果 token 没有三个部分、无法解码, 或者不包含“userid”字段。
        """

        splits = self.token.split(".")
        if len(splits) != TOKEN_PARTS_COUNT:
            msg = f"token 必须包含三个部分, 形如 'part1.part2.part3'"
            raise InvalidTokenError(self.token, msg)
        try:
            decoded_token = base64.urlsafe_b64decode(splits[1] + '=' * (-len(splits[1]) % 4)) # 处理 base64 URL 编码
            params = json.loads(decoded_token)
        except Exception as e:
            raise InvalidTokenError(self.token, "此token无法被解码") from e
        if TOKEN_USERID_FIELD not in params:
            raise InvalidTokenError(self.token, f"此token中没有{TOKEN_USERID_FIELD}字段")
        
        return params

    @property
    def student_id(self) -> str:
        """
        从token中提取学生ID
        
        Returns:
            学生ID字符串
            
        Raises:
            InvalidTokenError: 当token无效时
        """
        params = self.validate_token()
        user_id = params[TOKEN_USERID_FIELD]

        return user_id

    @property
    def custom_track_path(self) -> str:
        """
        获取自定义轨迹文件路径
        
        如果未启用自定义轨迹则返回空字符串。
        提供向下兼容旧配置格式的支持。
        
        Returns:
            自定义轨迹文件路径，或空字符串
        """
        if isinstance(self.custom_track, str):
            # 向下兼容旧配置
            return self.custom_track
        return self.custom_track.file_path if self.custom_track.enable else ""
