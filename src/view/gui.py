import yaml
import logging
import traceback
import requests
import threading
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
from main import main
from src.config_manager import validate_conf_main

# 设置 customtkinter 外观
ctk.set_appearance_mode("System")  # 系统主题
ctk.set_default_color_theme("blue")  # 蓝色主题


# 自定义日志处理器，将日志输出到文本控件
class TextboxLogger(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record)

        # 在主线程中更新UI
        self.textbox.after(0, self._append_log, msg)

    def _append_log(self, msg):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", msg + "\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")  # 滚动到最新日志


# 配置检查线程
class ConfigCheckThread(threading.Thread):
    def __init__(self, callback, error_callback):
        super().__init__()
        self.callback = callback
        self.error_callback = error_callback

    def run(self):
        try:
            result = validate_conf_main()
            if self.callback:
                self.callback(result)
        except Exception as e:
            if self.error_callback:
                self.error_callback(str(e))


# 主线程用于运行主程序
class MainThread(threading.Thread):
    def __init__(self, config_name, log_callback, result_callback, error_callback):
        super().__init__()
        self.config_name = config_name
        self.log_callback = log_callback
        self.result_callback = result_callback
        self.error_callback = error_callback

    def run(self):
        # 创建一个自定义日志处理器
        class ThreadLogHandler(logging.Handler):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback

            def emit(self, record):
                msg = self.format(record)
                if self.callback:
                    self.callback(msg)

        try:
            # 设置日志
            logger = logging.getLogger()
            log_handler = ThreadLogHandler(self.log_callback)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            log_handler.setFormatter(formatter)
            logger.handlers = []
            logger.addHandler(log_handler)

            # 调用主程序
            result = main(config_name=self.config_name)
            if self.result_callback:
                self.result_callback(result)
        except requests.exceptions.SSLError:
            if self.error_callback:
                self.error_callback("连接错误。请使用个人手机流量连接，使用校园网会出现证书问题。")
        except Exception as e:
            tb = traceback.format_exc()
            if self.log_callback:
                self.log_callback(tb)
                self.log_callback("主程序中出现未捕获的异常！")
            if self.error_callback:
                self.error_callback(str(e))
            if self.result_callback:
                self.result_callback(False)


# 主应用GUI
class AppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_logger()
        self.load_config()

    def setup_logger(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler = TextboxLogger(self.log_display)
        log_handler.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(log_handler)

    def initUI(self):
        self.title("体育锻炼")
        self.geometry("900x600")

        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # 左侧表单区域
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 存储表单字段
        self.fields = {}

        # 标题
        title_label = ctk.CTkLabel(form_frame, text="配置信息", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)

        # 表单字段
        self.create_field(form_frame, 'token', 'Token:')
        self.create_field(form_frame, 'student_id', '学号:')
        self.create_file_field(form_frame, 'start_image', '开始图片:')
        self.create_file_field(form_frame, 'finish_image', '结束图片:')

        # 日期字段
        date_frame = ctk.CTkFrame(form_frame)
        date_frame.pack(fill="x", padx=10, pady=5)

        date_label = ctk.CTkLabel(date_frame, text="日期:")
        date_label.pack(side="left", padx=5)

        # 简化日期输入 (使用三个组合框)
        date_container = ctk.CTkFrame(date_frame)
        date_container.pack(side="left", fill="x", expand=True)

        self.year_var = ctk.StringVar(value=str(datetime.now().year))
        self.month_var = ctk.StringVar(value=str(datetime.now().month))
        self.day_var = ctk.StringVar(value=str(datetime.now().day))

        year_combo = ctk.CTkComboBox(date_container, values=[str(y) for y in range(2020, 2030)],
                                     width=70, variable=self.year_var)
        month_combo = ctk.CTkComboBox(date_container, values=[str(m) for m in range(1, 13)],
                                      width=60, variable=self.month_var)
        day_combo = ctk.CTkComboBox(date_container, values=[str(d) for d in range(1, 32)],
                                    width=60, variable=self.day_var)

        year_combo.pack(side="left", padx=2)
        ctk.CTkLabel(date_container, text="-").pack(side="left")
        month_combo.pack(side="left", padx=2)
        ctk.CTkLabel(date_container, text="-").pack(side="left")
        day_combo.pack(side="left", padx=2)

        # 开始时间字段
        time_frame = ctk.CTkFrame(form_frame)
        time_frame.pack(fill="x", padx=10, pady=5)

        start_time_label = ctk.CTkLabel(time_frame, text="开始时间:")
        start_time_label.pack(side="left", padx=5)

        # 时间输入
        start_time_container = ctk.CTkFrame(time_frame)
        start_time_container.pack(side="left", fill="x", expand=True)

        self.start_hour_var = ctk.StringVar(value=str(datetime.now().hour))
        self.start_minute_var = ctk.StringVar(value=str(datetime.now().minute))
        self.start_second_var = ctk.StringVar(value=str(datetime.now().second))

        hour_combo = ctk.CTkComboBox(start_time_container, values=[f"{h:02d}" for h in range(24)],
                                     width=60, variable=self.start_hour_var)
        minute_combo = ctk.CTkComboBox(start_time_container, values=[f"{m:02d}" for m in range(60)],
                                       width=60, variable=self.start_minute_var)
        second_combo = ctk.CTkComboBox(start_time_container, values=[f"{s:02d}" for s in range(60)],
                                       width=60, variable=self.start_second_var)

        hour_combo.pack(side="left", padx=2)
        ctk.CTkLabel(start_time_container, text=":").pack(side="left")
        minute_combo.pack(side="left", padx=2)
        ctk.CTkLabel(start_time_container, text=":").pack(side="left")
        second_combo.pack(side="left", padx=2)

        # 结束时间字段
        finish_time_frame = ctk.CTkFrame(form_frame)
        finish_time_frame.pack(fill="x", padx=10, pady=5)

        finish_time_label = ctk.CTkLabel(finish_time_frame, text="结束时间:")
        finish_time_label.pack(side="left", padx=5)

        # 结束时间输入
        finish_time_container = ctk.CTkFrame(finish_time_frame)
        finish_time_container.pack(side="left", fill="x", expand=True)

        self.finish_hour_var = ctk.StringVar(value=str(datetime.now().hour))
        self.finish_minute_var = ctk.StringVar(value=str(datetime.now().minute))
        self.finish_second_var = ctk.StringVar(value=str(datetime.now().second))

        finish_hour_combo = ctk.CTkComboBox(finish_time_container, values=[f"{h:02d}" for h in range(24)],
                                            width=60, variable=self.finish_hour_var)
        finish_minute_combo = ctk.CTkComboBox(finish_time_container, values=[f"{m:02d}" for m in range(60)],
                                              width=60, variable=self.finish_minute_var)
        finish_second_combo = ctk.CTkComboBox(finish_time_container, values=[f"{s:02d}" for s in range(60)],
                                              width=60, variable=self.finish_second_var)

        finish_hour_combo.pack(side="left", padx=2)
        ctk.CTkLabel(finish_time_container, text=":").pack(side="left")
        finish_minute_combo.pack(side="left", padx=2)
        ctk.CTkLabel(finish_time_container, text=":").pack(side="left")
        finish_second_combo.pack(side="left", padx=2)

        # 距离字段
        self.create_field(form_frame, 'distance', '距离 (公里):')

        # 按钮区域
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        save_btn = ctk.CTkButton(button_frame, text="保存更改", command=self.save_config)
        save_btn.pack(side="left", padx=5, expand=True)

        check_btn = ctk.CTkButton(button_frame, text="检查配置", command=lambda: self.check_config(True))
        check_btn.pack(side="left", padx=5, expand=True)

        run_btn = ctk.CTkButton(button_frame, text="运行", command=self.run_main)
        run_btn.pack(side="left", padx=5, expand=True)

        # 右侧日志区域
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=0)
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        log_title = ctk.CTkLabel(log_frame, text="日志输出", font=ctk.CTkFont(size=16, weight="bold"))
        log_title.grid(row=0, column=0, pady=10)

        self.log_display = ctk.CTkTextbox(log_frame, wrap="word")
        self.log_display.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.log_display.configure(state="disabled")

    def create_field(self, parent, field_name, label_text):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side="left", padx=5)

        field = ctk.CTkEntry(frame)
        field.pack(side="right", fill="x", expand=True, padx=5)

        self.fields[field_name] = field

    def create_file_field(self, parent, field_name, label_text):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)

        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side="left", padx=5)

        field = ctk.CTkEntry(frame)
        field.pack(side="left", fill="x", expand=True, padx=5)

        browse_button = ctk.CTkButton(frame, text="浏览...", width=60,
                                      command=lambda: self.browse_file(field_name))
        browse_button.pack(side="right", padx=5)

        self.fields[field_name] = field

    def browse_file(self, field_name):
        filename = filedialog.askopenfilename(
            title='选择图片',
            filetypes=(('图片文件', '*.jpg *.png'), ('所有文件', '*.*')),
        )
        if filename:
            # 替换反斜杠
            filename = filename.replace('\\', '\\\\')
            self.fields[field_name].delete(0, 'end')
            self.fields[field_name].insert(0, filename)

    def check_config(self, show_message=True):
        self.save_config()

        # 启动配置检查线程
        ConfigCheckThread(
            callback=lambda result: self.after(0, self.handle_config_check_result, result, show_message),
            error_callback=lambda error_msg: self.after(0, self.handle_config_check_error, error_msg)
        ).start()

    def handle_config_check_result(self, result, show_message):
        if result and show_message:
            messagebox.showinfo('配置检查', '配置检查通过！')
        elif not result:
            messagebox.showwarning('配置检查', '配置检查未通过，请检查配置文件！')

    def handle_config_check_error(self, error_msg):
        messagebox.showerror('错误', f'配置检查时发生错误：{error_msg}')

    def load_config(self):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                basic = config['basic']

                # 为每个普通字段加载配置
                for field_name, field in self.fields.items():
                    if field_name in basic:
                        field.delete(0, 'end')
                        field.insert(0, str(basic[field_name]))

                # 处理日期
                if 'date' in basic:
                    try:
                        date_parts = basic['date'].split('-')
                        if len(date_parts) == 3:
                            self.year_var.set(date_parts[0])
                            self.month_var.set(date_parts[1])
                            self.day_var.set(date_parts[2])
                    except:
                        pass

                # 处理时间
                if 'start_time' in basic:
                    try:
                        time_parts = basic['start_time'].split(':')
                        if len(time_parts) == 3:
                            self.start_hour_var.set(time_parts[0])
                            self.start_minute_var.set(time_parts[1])
                            self.start_second_var.set(time_parts[2])
                    except:
                        pass

                if 'finish_time' in basic:
                    try:
                        time_parts = basic['finish_time'].split(':')
                        if len(time_parts) == 3:
                            self.finish_hour_var.set(time_parts[0])
                            self.finish_minute_var.set(time_parts[1])
                            self.finish_second_var.set(time_parts[2])
                    except:
                        pass

        except Exception as e:
            messagebox.showerror('错误', f'加载配置文件时出错：{str(e)}')

    def save_config(self):
        try:
            # 读取现有配置
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 更新配置
            for field_name, field in self.fields.items():
                config['basic'][field_name] = field.get()

            # 更新日期和时间
            config['basic']['date'] = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
            config['basic'][
                'start_time'] = f"{self.start_hour_var.get()}:{self.start_minute_var.get()}:{self.start_second_var.get()}"
            config['basic'][
                'finish_time'] = f"{self.finish_hour_var.get()}:{self.finish_minute_var.get()}:{self.finish_second_var.get()}"

            # 保存配置
            with open('config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)

            self.logger.info('配置保存成功！')
        except Exception as e:
            messagebox.showerror('错误', f'保存配置文件时出错：{str(e)}')

    def run_main(self):
        # 清空日志显示
        self.log_display.configure(state="normal")
        self.log_display.delete(1.0, "end")
        self.log_display.configure(state="disabled")

        # 保存配置
        self.save_config()

        # 创建并启动主线程
        MainThread(
            config_name='config.yaml',
            log_callback=lambda msg: self.after(0, self.update_log, msg),
            result_callback=lambda result: self.after(0, self.handle_main_result, result),
            error_callback=lambda error_msg: self.after(0, self.handle_error, error_msg)
        ).start()

    def handle_error(self, error_msg):
        messagebox.showerror('错误', f'发生错误：{error_msg}')

    def update_log(self, msg):
        self.log_display.configure(state="normal")
        self.log_display.insert("end", msg + "\n")
        self.log_display.configure(state="disabled")
        self.log_display.see("end")  # 滚动到最新日志

    def handle_main_result(self, succeeded):
        if succeeded:
            messagebox.showinfo('成功', '操作成功完成！')
        else:
            messagebox.showwarning('警告', '操作失败！')


def main_gui():
    app = AppGUI()
    app.mainloop()


if __name__ == "__main__":
    main_gui()
