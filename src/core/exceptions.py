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
        return str(self)


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

    def code_explanation(self) -> str:
        return self.explanations.get(self.response_code, "")

    def explain(self) -> str:
        explanation = self.code_explanation()
        explanation = f". {explanation}" if explanation != "" else ""
        return f"{self}{explanation}"


class APIClientError(AppError):
    def __init__(self, desc: str):
        self.desc = desc
        super().__init__(f"{desc}时出现异常")

    def explain(self) -> str:
        cause = self._get_cause()
        cause = "未知" if cause == "" else f"是{cause}"
        return f"{self}, 原因{cause}"


class TrackError(AppError):
    def __init__(self, file_name: str):
        super().__init__(f"从文件 '{file_name}' 中读取轨迹数据时出现异常")

    def explain(self) -> str:
        cause = self._get_cause()
        cause = "未知" if cause == "" else f"是{cause}"
        return f"{self}, 原因{cause}"


class ConfigError(AppError):
    def __init__(self, file_name: str):
        super().__init__(f"读取配置文件 '{file_name}' 时出现异常")

    def explain(self) -> str:
        cause = self._get_cause()
        cause = "未知" if cause == "" else f"是{cause}"
        return f"{self}, 原因{cause}"


class RouteInfoError(AppError):
    def __init__(self, file_name: str):
        super().__init__(f"从文件 '{file_name}' 中读取路线信息时出现异常")

    def explain(self) -> str:
        cause = self._get_cause()
        cause = "未知" if cause == "" else f"是{cause}"
        return f"{self}, 原因{cause}"
