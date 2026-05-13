"""
历史粘贴板 - 应用入口
点击 run.bat 启动
"""

import sys
import os
import traceback
from datetime import datetime

# 获取项目根目录（无论从哪里运行）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def _log_error(msg):
    """将错误写入日志文件"""
    try:
        log_dir = os.path.join(PROJECT_ROOT, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'error.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]\n{msg}\n{"="*50}\n')
    except Exception:
        pass


def _setup_qt_plugin_path():
    """设置 Qt 平台插件路径，解决 qwindows.dll 找不到的问题"""
    import PyQt5
    qt_dir = os.path.dirname(PyQt5.__file__)
    plugin_dir = os.path.join(qt_dir, 'Qt5', 'plugins')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_dir
    os.environ['QT_PLUGIN_PATH'] = plugin_dir


def main():
    try:
        _setup_qt_plugin_path()

        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt

        # 高分屏适配（安全模式：如果属性不存在就跳过）
        try:
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            pass

        app = QApplication(sys.argv)
        app.setApplicationName('历史粘贴板')

        # 全局样式（默认 24px）
        from src.styles import build_qss
        app.setStyleSheet(build_qss(24))

        from src.main_window import MainWindow
        window = MainWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        error_msg = traceback.format_exc()
        _log_error(error_msg)

        # 尝试弹出错误对话框
        try:
            _setup_qt_plugin_path()
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            QMessageBox.critical(None, '启动失败', error_msg)
        except Exception:
            pass

        # 兜底：打印到 stderr
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
