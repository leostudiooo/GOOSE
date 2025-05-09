#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Open SEU Exercise CLI: 东南大学体育锻炼助手命令行版本
Copyright (c) 2025 Leo Li

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import yaml
import logging
import traceback
import requests
import threading
import argparse
import time
from datetime import datetime
import questionary
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown
from main import main
from src.config_manager import validate_conf_main

# 设置富文本控制台
console = Console()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)],
)

logger = logging.getLogger("seu_exercise")


def load_config(file_path="config.yaml"):
    """加载配置文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None


def save_config(config, file_path="config.yaml"):
    """保存配置文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True)
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        return False


def check_config():
    """检查配置"""
    with console.status("[bold blue]正在检查配置...", spinner="dots"):
        try:
            result = validate_conf_main()
            if result:
                console.print("[bold green]✓ 配置检查通过！[/bold green]")
            else:
                console.print("[bold red]✗ 配置检查未通过，请检查配置文件！[/bold red]")
            return result
        except Exception as e:
            console.print(f"[bold red]✗ 配置检查出错: {e}[/bold red]")
            return False


def interactive_config():
    """交互式配置"""
    config = load_config()
    if not config:
        config = {"basic": {}}

    basic = config.get("basic", {})

    # 显示当前配置
    if basic:
        console.print(
            Panel(
                "\n".join(
                    [
                        f"[cyan]{k}[/cyan]: [yellow]{v}[/yellow]"
                        for k, v in basic.items()
                    ]
                ),
                title="当前配置",
                expand=False,
            )
        )

    # 询问是否更新配置
    if basic and not questionary.confirm("是否更新配置?").ask():
        return config

    # 交互式收集配置信息
    console.print("\n[bold blue]请输入配置信息[/bold blue] (按Enter保留当前值)")

    # Token
    token = questionary.text("Token:", default=basic.get("token", "")).ask()
    if token:
        basic["token"] = token

    # 学号
    student_id = questionary.text("学号:", default=basic.get("student_id", "")).ask()
    if student_id:
        basic["student_id"] = student_id

    # 日期 (提供当前日期作为默认值)
    current_date = datetime.now().strftime("%Y-%m-%d")
    date_str = questionary.text(
        "日期 (YYYY-MM-DD):", default=basic.get("date", current_date)
    ).ask()
    if date_str:
        basic["date"] = date_str

    # 开始时间
    current_time = datetime.now().strftime("%H:%M:%S")
    start_time = questionary.text(
        "开始时间 (HH:MM:SS):", default=basic.get("start_time", current_time)
    ).ask()
    if start_time:
        basic["start_time"] = start_time

    # 结束时间
    finish_time = questionary.text(
        "结束时间 (HH:MM:SS):", default=basic.get("finish_time", current_time)
    ).ask()
    if finish_time:
        basic["finish_time"] = finish_time

    # 距离
    distance = questionary.text(
        "距离 (公里):", default=str(basic.get("distance", ""))
    ).ask()
    if distance:
        basic["distance"] = distance

    # 开始图片
    start_image = questionary.text(
        "开始图片路径:", default=basic.get("start_image", "")
    ).ask()
    if start_image:
        basic["start_image"] = start_image

    # 结束图片
    finish_image = questionary.text(
        "结束图片路径:", default=basic.get("finish_image", "")
    ).ask()
    if finish_image:
        basic["finish_image"] = finish_image

    config["basic"] = basic

    # 保存配置
    if save_config(config):
        console.print("[bold green]✓ 配置已保存！[/bold green]")

    return config


class CustomLogHandler(logging.Handler):
    """自定义日志处理器，将日志输出到rich控制台"""

    def emit(self, record):
        msg = self.format(record)
        level = record.levelno

        if level >= logging.ERROR:
            console.print(f"[bold red]{msg}[/bold red]")
        elif level >= logging.WARNING:
            console.print(f"[bold yellow]{msg}[/bold yellow]")
        elif level >= logging.INFO:
            console.print(f"[bold green]{msg}[/bold green]")
        else:
            console.print(msg)


def upload_record():
    """运行主程序"""
    # 配置日志
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 添加自定义处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    log_handler = CustomLogHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # 显示运行信息
    console.print("\n[bold blue]正在运行主程序...[/bold blue]")

    try:
        # 运行主程序
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]运行中...[/bold blue]"),
            transient=True,
        ) as progress:
            task = progress.add_task("运行", total=None)

            # 创建一个事件来跟踪完成状态
            done_event = threading.Event()
            result_container = {"success": False, "error": None}

            def run_thread():
                try:
                    result = main(config_name="config.yaml")
                    result_container["success"] = result
                except requests.exceptions.SSLError:
                    result_container["error"] = (
                        "连接错误。请使用个人手机流量连接，使用校园网会出现证书问题。"
                    )
                except Exception as e:
                    result_container["error"] = str(e)
                    logger.error(traceback.format_exc())
                finally:
                    done_event.set()

            # 启动线程
            thread = threading.Thread(target=run_thread)
            thread.daemon = True
            thread.start()

            # 等待完成或用户中断
            while not done_event.is_set():
                progress.update(task, advance=0.1)
                time.sleep(0.1)
                if not thread.is_alive():
                    break

        # 显示结果
        if result_container["success"]:
            console.print("[bold green]✓ 运行成功完成！[/bold green]")
            return True
        elif result_container["error"]:
            console.print(
                f"[bold red]✗ 运行出错: {result_container['error']}[/bold red]"
            )
        else:
            console.print("[bold red]✗ 运行失败！[/bold red]")

        return False
    except KeyboardInterrupt:
        console.print("\n[bold yellow]已取消运行[/bold yellow]")
        return False


def print_welcome():
    gpl_md = """
This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. See the GNU General Public License for details.

本程序不作任何品质保证。这是自由软件，您可以在某些条件下重新发布它。请参阅 GNU 通用公共许可证以获取详细信息。

<https://www.gnu.org/licenses/gpl-3.0.html>
    """

    console.print(
        "[bold blue]Open SEU Exercise CLI v0.1.1 Copyright (c) 2025 Leo Li[/bold blue]\n"
    )
    console.print(Markdown(gpl_md))
    console.print()


def main_menu():
    """主菜单"""
    print_welcome()

    while True:
        choice = questionary.select(
            "请选择操作",
            choices=["配置参数", "检查配置", "上传锻炼记录", "退出"],
            use_arrow_keys=True,
        ).ask()

        if choice == "配置参数":
            interactive_config()
        elif choice == "检查配置":
            check_config()
        elif choice == "上传锻炼记录":
            upload_record()
        elif choice == "退出":
            console.print("[bold blue]Bye![/bold blue]")
            break

def update_config_from_args(config_args):
    """根据命令行参数更新配置"""
    if not config_args or config_args[0] is True:
        # 如果只是-c但没有参数值，进入交互式配置
        return interactive_config()

    # 加载现有配置
    config = load_config()
    if not config:
        config = {"basic": {}}

    basic = config.get("basic", {})
    updated = False

    # 有效的基础配置项列表
    valid_basic_keys = [
        'token', 'student_id', 'date', 'start_time', 'finish_time', 
        'distance', 'start_image', 'finish_image', 'calorie'
    ]

    # 处理每个配置参数
    for arg in config_args:
        if arg is True:
            continue

        if "=" in arg:
            key, value = arg.split("=", 1)
            if key and value:
                # 检查键是否为有效配置项
                if key in valid_basic_keys:
                    basic[key] = value
                    console.print(
                        f"[green]已设置[/green] [cyan]{key}[/cyan] = [yellow]{value}[/yellow]"
                    )
                    updated = True
                else:
                    console.print(
                        f"[yellow]警告: 忽略无效的配置项 '{key}'，有效配置项包括: {', '.join(valid_basic_keys)}[/yellow]"
                    )
        else:
            console.print(
                f"[yellow]警告: 忽略无效的配置参数 '{arg}'，正确格式为 key=value[/yellow]"
            )

    # 如果有更新，保存配置
    if updated:
        config["basic"] = basic
        if save_config(config):
            console.print("[bold green]✓ 配置已保存！[/bold green]")
            
        # 验证更新后的配置
        from src.config_manager import validate_config
        valid = validate_config("config.yaml")
        if not valid:
            console.print("[bold yellow]⚠️ 警告: 配置已保存，但验证未通过。请检查配置项。[/bold yellow]")
            console.print("[bold yellow]建议运行 './cli.py check' 查看详细错误信息。[/bold yellow]")
        else:
            console.print("[bold green]✓ 配置已验证通过！[/bold green]")
            
        return config

    return None

def parse_args():
    """解析命令行参数，支持中文子命令和自然语言交互"""
    parser = argparse.ArgumentParser(description="东南大学体育锻炼助手")
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 上传/运行命令 - 同时支持中英文
    run_parser = subparsers.add_parser("run", aliases=["上传", "提交", "直接上传"], help="运行并提交锻炼记录")
    run_parser.add_argument(
        "--yes", "-y", "--对的", "--确认",
        action="store_true", 
        dest="confirm",
        help="确认提交，无需询问"
    )
    run_parser.add_argument(
        "-s", "--skip-check", "--no-check", "--不用验证", "--不检查",
        action="store_true", 
        dest="skip_check",
        help="跳过验证，直接提交"
    )
    run_parser.add_argument(
        "--config", "--set", "--配置", "-c", "--设置",
        action="append",
        dest="config_params",
        help="配置参数，格式为 key=value，如 --config date=2024-03-07"
    )
    
    # 配置命令 - 同时支持中英文
    config_parser = subparsers.add_parser("config", aliases=["配置", "设置"], help="配置参数")
    config_parser.add_argument(
        "params", 
        nargs="*", 
        help="配置参数，格式为 key=value，如 date=2012-07-12"
    )
    config_parser.add_argument(
        "-i", "--interactive", "--交互", 
        action="store_true", 
        help="进入交互式配置模式"
    )
    
    # 检查配置命令 - 同时支持中英文
    subparsers.add_parser("check", aliases=["检查", "验证", "对吗", "对吗？"], help="检查配置")
    
    # 保留旧式参数以向后兼容
    parser.add_argument(
        "-c", "--config", "--配置",
        action="append", 
        nargs="?", 
        const=True, 
        help="配置参数，可使用 key=value 格式直接设置配置，如-c date=2025-04-12"
    )
    parser.add_argument(
        "-r", "--run", 
        action="store_true", 
        help="运行程序并提交锻炼记录"
    )
    parser.add_argument(
        "-v", "--check", "--validate", "--验证", "--检查", "--对吗", "--对吗？",
        action="store_true", 
        help="检查配置"
    )
    parser.add_argument(
        "-s", "--skip-check", "--no-check", "--skip-validation", "--不用验证", "--不检查",
        action="store_true", 
        help="跳过验证，直接提交 (与 -r 一起使用)"
    )
    parser.add_argument(
        "-y", "--yes", "-Y", "--对的", "--确认",
        action="store_true", 
        help="确认提交，无需询问 (与 -r 一起使用)"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()

    try:
        # 根据命令行参数执行操作
        # 新式子命令处理
        if hasattr(args, 'command') and args.command:
            if args.command in ["config", "配置", "设置"]:
                if args.params:
                    # 处理配置参数
                    update_config_from_args(args.params)
                else:
                    # 无参数或指定交互式则进入交互配置
                    interactive_config()
                    
            elif args.command in ["check", "检查", "验证"]:
                check_config()
                
            elif args.command in ["run", "上传", "提交", "直接上传"]:
                
                # 如果有配置，先进行处理 
                if hasattr(args, 'config_params') and args.config_params:
                    update_config_from_args(args.config_params)
                
                # 确认是否提交锻炼记录
                if args.confirm or questionary.confirm("是否提交锻炼记录?").ask():
                    console.print("[bold blue]正在提交锻炼记录...[/bold blue]")
                else:
                    console.print("[bold yellow]已取消提交锻炼记录[/bold yellow]")
                    exit(0)
                    
                # 运行程序，根据参数决定是否跳过验证
                if not args.skip_check:
                    if not check_config():
                        exit(1)
                else:
                    console.print(
                        "[bold yellow]跳过配置验证，直接提交锻炼记录[/bold yellow]"
                    )
                upload_record()
        
        # 旧式参数兼容
        elif args.config is not None:
            # 处理单个或多个配置参数
            config = update_config_from_args(args.config)
            # 如果没有通过命令行更新配置，且没有其他参数，则进入交互式配置
            if config is None and not any([args.run, args.check]):
                interactive_config()
                
        elif args.check:
            check_config()
            
        elif args.run:
            # 确认是否提交锻炼记录
            if args.yes or questionary.confirm("是否提交锻炼记录?").ask():
                console.print("[bold blue]正在提交锻炼记录...[/bold blue]")
            else:
                console.print("[bold yellow]已取消提交锻炼记录[/bold yellow]")
                exit(0)
                
            # 运行程序，根据参数决定是否跳过验证
            if not args.skip_validation:
                if not check_config():
                    console.print(
                        "[bold red]✗ 配置检查未通过，请检查配置文件！[/bold red]"
                    )
                    exit(1)
            else:
                console.print(
                    "[bold yellow]跳过配置验证，直接提交锻炼记录[/bold yellow]"
                )
            upload_record()
            
        else:
            # 如果没有参数，显示交互式菜单
            main_menu()
            
    except KeyboardInterrupt:
        console.print("\n[bold yellow]操作已取消[/bold yellow]")
        exit(0)
    except Exception as e:
        console.print(f"[bold red]发生错误: {str(e)}[/bold red]")
        logger.error(traceback.format_exc())
        exit(1)