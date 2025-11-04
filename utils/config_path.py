"""配置路径管理模块"""

import os
import sys


def get_config_file_path():
    """
    获取配置文件路径

    在打包环境中,配置文件应保存到用户目录的可写位置
    在开发环境中,使用当前目录
    """
    if getattr(sys, "frozen", False):
        # 打包后的环境,使用用户主目录下的应用数据目录
        if sys.platform == "darwin":  # macOS
            config_dir = os.path.expanduser("~/Library/Application Support/FreePDF")
        elif sys.platform == "win32":  # Windows
            config_dir = os.path.expanduser("~/AppData/Local/FreePDF")
        else:  # Linux
            config_dir = os.path.expanduser("~/.config/FreePDF")

        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "pdf2zh_config.json")

        # 如果配置文件不存在,尝试从应用包复制默认配置
        if not os.path.exists(config_file):
            default_config = os.path.join(get_app_resource_dir(), "pdf2zh_config.json")
            if os.path.exists(default_config):
                import shutil
                try:
                    shutil.copy2(default_config, config_file)
                    print(f"已复制默认配置到: {config_file}")
                except Exception as e:
                    print(f"复制默认配置失败: {e}")

        return config_file
    else:
        # 开发环境,使用项目目录
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pdf2zh_config.json")


def get_app_resource_dir():
    """获取应用资源目录"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller打包环境
        return sys._MEIPASS
    else:
        # 开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """
    获取资源文件路径(只读资源,如模型、字体等)

    这些资源打包在应用内,不应被修改
    """
    base_path = get_app_resource_dir()
    resource_path = os.path.join(base_path, relative_path)
    return resource_path
