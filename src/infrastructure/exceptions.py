from pathlib import Path

from pydantic import ValidationError

from src.infrastructure.constants import (
    API_ERROR_INVALID_TENANT,
    API_ERROR_INVALID_TOKEN,
)


class AppError(Exception):
    """
    应用程序基础异常类

    所有应用程序自定义异常的基类，提供异常链追踪和友好的错误说明。
    """

    def __init__(self, *args: object):
        super().__init__(*args)

    def _get_cause(self) -> str:
        """
        获取异常原因的说明

        Returns:
            异常原因的字符串描述
        """
        if isinstance(self.__cause__, AppError):
            return self.__cause__.explain()

        if isinstance(self.__cause__, Exception):
            return f"{type(self.__cause__).__name__} -> {self.__cause__}"

        return ""

    def _desc_with_type(self) -> str:
        return f"{self}({type(self).__name__})"

    def explain(self) -> str:
        """
        获取详细的错误说明

        Returns:
            包含错误信息和原因的完整说明
        """
        cause = self._get_cause()
        return f"{self._desc_with_type()}" + ("" if cause == "" else f"\n 由于: {cause}")


class ServiceError(AppError):
    def __init__(self, desc: str):
        """
        业务操作异常

        Args:
            desc: 错误操作的描述
        """
        self.desc = desc
        super().__init__(f"{desc}失败")


class RouteNotFoundError(AppError):
    """
    路线未找到异常

    当尝试查找不存在的路线时抛出。
    """

    def __init__(self, route_name: str, valid_route_names: list[str]):
        """
        初始化路线未找到异常

        Args:
            route_name: 查找的路线名称
            valid_route_names: 所有有效的路线名称列表
        """
        self.valid_route_names = valid_route_names
        super().__init__(f"找不到名为 '{route_name}' 的路线")

    def explain(self) -> str:
        """
        获取详细的错误说明，包括可用路线列表

        Returns:
            包含所有可用路线的错误说明
        """
        valid_route_names = [f"'{route_name}'" for route_name in self.valid_route_names]
        valid_route_names = ", ".join(valid_route_names)
        return f"{self._desc_with_type()}, " + (f"可用的路线包括 {valid_route_names}" if valid_route_names != "" else "无任何可用路线")


class APIResponseError(AppError):
    """
    API响应错误异常

    当API返回错误响应码时抛出，提供错误码的中文解释。
    """

    explanations = {
        API_ERROR_INVALID_TENANT: "tenant可能有误或已经过期",
        API_ERROR_INVALID_TOKEN: "token可能有误或已经过期",
    }

    def __init__(self, api_name: str, response_code: int, response_msg: str):
        """
        初始化API响应错误异常

        Args:
            api_name: API名称或路径
            response_code: 响应错误码
            response_msg: 响应错误消息
        """
        self.response_code = response_code
        msg = f", 附加信息为 '{response_msg}'" if response_msg != "" else ""
        super().__init__(f"API '{api_name}' 的响应异常. 响应中的错误码为 {response_code}{msg}")

    def explain(self) -> str:
        """
        获取详细的错误说明，包括错误码的中文解释

        Returns:
            包含错误码解释的错误说明
        """
        explanation = self.explanations.get(self.response_code, "")
        explanation = f". {explanation}" if explanation != "" else ""
        return f"{self._desc_with_type()}{explanation}"


class APIClientError(AppError):
    """
    API客户端错误异常

    当API请求过程中发生异常时抛出（如网络错误、超时等）。
    """

    def __init__(self, desc: str):
        """
        初始化API客户端错误异常

        Args:
            desc: 错误操作的描述
        """
        self.desc = desc
        super().__init__(f"{desc}时出现异常")


class ModelValidationError(AppError):
    """
    模型验证错误异常

    当Pydantic模型验证失败时抛出，包含详细的验证错误信息。
    """

    def __init__(self, msg: str, error: ValidationError):
        """
        初始化模型验证错误异常

        Args:
            msg: 错误消息前缀
            error: Pydantic的ValidationError对象
        """
        errors = [f"{''.join(map(str, error['loc']))}: {error['msg']}" for error in error.errors()]
        errors = "\n".join(errors)
        super().__init__(f"{msg}:\n{errors}")

    def explain(self) -> str:
        """
        获取错误说明

        Returns:
            完整的验证错误信息
        """
        return self._desc_with_type()


class ModelStorageError(AppError):
    """
    模型存储错误异常

    当模型文件保存或加载过程中发生错误时抛出，包含相关文件路径和错误信息。
    """
    """
    模型存储错误异常

    当模型文件保存或加载过程中发生错误时抛出，包含相关文件路径和错误信息。
    """
    def __init__(self, file_path: Path, msg: str):
        super().__init__(msg)
        self.file_path = file_path


class InvalidTokenError(AppError):
    """
    无效Token错误异常

    当用户token格式不正确或内容无效时抛出。
    """

    def __init__(self, token: str, msg: str = ""):
        """
        初始化无效Token错误异常

        Args:
            token: 无效的token字符串
            msg: 详细的错误说明
        """
        self.token = token
        super().__init__(f"无效的token. {msg}")
