import logging
from typing import Optional

from textual.app import App


class NotificationManager(logging.Handler):
    """
    通知管理器，从日志中提取信息并发送通知
    作为日志处理器，它会监听所有日志消息并根据级别发送相应的通知
    """

    # 日志级别到通知严重性的映射
    LEVEL_TO_SEVERITY = {
        logging.DEBUG: "information",
        logging.INFO: "information",
        logging.WARNING: "warning",
        logging.ERROR: "error",
        logging.CRITICAL: "error",
    }

    def __init__(self, app: Optional[App] = None):
        """初始化通知管理器"""
        super().__init__()
        self.app = app
        self.setLevel(logging.WARNING)  # 只处理INFO及以上级别的日志

    def set_app(self, app: App) -> None:
        """设置应用程序实例"""
        self.app = app

    def emit(self, record: logging.LogRecord) -> None:
        """处理日志记录并发送通知"""
        if self.app is None:
            return

        try:
            severity = self.LEVEL_TO_SEVERITY.get(record.levelno, "information")
            message = self.format(record)

            # 使用异常类型作为标识，避免重复通知相同内容
            if hasattr(record, "exc_info") and record.exc_info:
                exc_type, exc_value, _ = record.exc_info
                if exc_value:
                    message = str(exc_value)

            # 调用app的notify方法发送通知
            self.app.notify(message, severity=severity, markup=False)
        except Exception:
            self.handleError(record)
