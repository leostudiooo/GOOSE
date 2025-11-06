from pathlib import Path

from pydantic import ValidationError


class AppError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)

    def _get_cause(self) -> str:
        if isinstance(self.__cause__, AppError):
            return self.__cause__.explain()

        if isinstance(self.__cause__, Exception):
            return str(self.__cause__)

        return ""

    def explain(self) -> str:
        cause = self._get_cause()
        return str(self) if cause == "" else f"{self}, 原因是{cause}"


class RouteNotFoundError(AppError):
    def __init__(self, route_name: str, valid_route_names: list[str]):
        self.valid_route_names = valid_route_names
        super().__init__(f"找不到名为 '{route_name}' 的路线")

    def explain(self) -> str:
        valid_route_names = [f"'{route_name}'" for route_name in self.valid_route_names]
        valid_route_names = ", ".join(valid_route_names)
        return f"{self}, 可用的路线包括 {valid_route_names}"


class APIResponseError(AppError):
    explanations = {
        -6: "tenant可能有误或已经过期",
        40005: "token可能有误或已经过期",
    }

    def __init__(self, api_name: str, response_code: int, response_msg: str):
        self.response_code = response_code
        msg = f", 附加信息为 '{response_msg}'" if response_msg != "" else ""
        super().__init__(
            f"API '{api_name}' 的响应异常. 响应中的错误码为 {response_code}{msg}"
        )

    def explain(self) -> str:
        explanation = self.explanations.get(self.response_code, "")
        explanation = f". {explanation}" if explanation != "" else ""
        return f"{self}{explanation}"


class APIClientError(AppError):
    def __init__(self, desc: str):
        self.desc = desc
        super().__init__(f"{desc}时出现异常")


class ModelValidationError(AppError):
    def __init__(self, msg: str, error: ValidationError):
        errors = [
            f"{''.join(map(str, error['loc']))}: {error['msg']}"
            for error in error.errors()
        ]
        errors = "\n".join(errors)
        super().__init__(f"{msg}:\n{errors}")

    def explain(self) -> str:
        return str(self)


class ModelStorageError(AppError):
    def __init__(self, file_path: Path, msg: str):
        super().__init__(msg)
        self.file_path = file_path


class InvalidTokenError(AppError):
    def __init__(self, token: str, msg: str = ""):
        self.token = token
        super().__init__(f"无效的token. {msg}")

    def explain(self) -> str:
        cause = self._get_cause()
        return str(self) if cause == "" else f"{self}, 详细信息: {cause}"
