from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input


class DateTimeInput(Horizontal):
    """日期时间输入组件"""

    def __init__(self, id_prefix="dt"):
        super().__init__(id=f"{id_prefix}_container", classes="date-time-input")
        self.id_prefix = id_prefix

    def compose(self) -> ComposeResult:
        yield Input(
            id=f"{self.id_prefix}_date", placeholder="日期 (YYYY-MM-DD)", classes="date-input"
        )
        yield Input(
            id=f"{self.id_prefix}_time", placeholder="时间 (HH:MM:SS)", classes="time-input"
        )
        yield Button("现在", id=f"{self.id_prefix}_now", variant="primary", classes="now-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理'现在'按钮点击"""
        if event.button.id == f"{self.id_prefix}_now":
            now = datetime.now()
            self.set_value(now)

    def set_value(self, dt):
        """设置日期时间值"""
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return

        self.query_one(f"#{self.id_prefix}_date").value = dt.strftime("%Y-%m-%d")
        self.query_one(f"#{self.id_prefix}_time").value = dt.strftime("%H:%M:%S")

    def get_value(self):
        """获取日期时间值"""
        date_str = self.query_one(f"#{self.id_prefix}_date").value
        time_str = self.query_one(f"#{self.id_prefix}_time").value

        if not date_str or not time_str:
            return None

        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
