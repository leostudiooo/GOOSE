from textual.widgets import Select
from textual.containers import Horizontal
from textual.app import ComposeResult

class ConfigSelector(Horizontal):
    """配置类型选择器"""
    
    def compose(self) -> ComposeResult:
        yield Select(
            [("user", "用户配置"),],
            value="user",
            id="config_selector"
        )
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """切换显示的配置面板"""
        self.app.query_one(f"#{event.value}_config").display = True
        for panel_id in ["user_config", "system_config", "route_config"]:
            if panel_id != f"{event.value}_config":
                self.app.query_one(f"#{panel_id}").display = False