from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container

from ConfigSelector import ConfigSelector
from UserConfigPanel import UserConfigPanel
from ActionPanel import ActionPanel

class GOOSEApp(App):
    """GOOSE 配置管理与上传应用"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    """
    
    def compose(self) -> ComposeResult:
        """创建主界面布局"""
        yield Header(show_clock=True)
        yield ConfigSelector()
        yield Container(
            UserConfigPanel(),
            id="config_panels"
        )
        yield ActionPanel()
        yield Footer()