"""UI组件模块"""

import math
import threading

import requests

try:
    from markdown_it import MarkdownIt

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtCore import QTimer as _QTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AnimationOverlay(QWidget):
    """动画覆盖层 - 确保旋转动画在最上层"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.animation_center_x = 0
        self.animation_center_y = 0
        self.radius = 22  # 增大半径，让动画更明显

        # 设置为透明覆盖层
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)

        # 确保这个widget在最上层
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.raise_()

    def set_animation_center(self, x, y):
        """设置动画中心点"""
        self.animation_center_x = x
        self.animation_center_y = y
        self.update()

    def set_angle(self, angle):
        """设置旋转角度"""
        self.angle = angle
        self.update()

    def paintEvent(self, event):
        """绘制旋转动画"""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.animation_center_x
        center_y = self.animation_center_y

        # 只在有效位置绘制
        if center_x > 0 and center_y > 0:
            # 绘制外圈淡色圆圈 - 增加可见性
            painter.setPen(QColor(0, 122, 204, 80))
            painter.setBrush(QColor(0, 122, 204, 30))
            painter.drawEllipse(
                center_x - self.radius - 8,
                center_y - self.radius - 8,
                (self.radius + 8) * 2,
                (self.radius + 8) * 2,
            )

            # 绘制旋转的加载点 - 增强可见性
            painter.setPen(QColor(0, 122, 204, 150))

            for i in range(12):
                angle_rad = math.radians(self.angle + i * 30)
                x = center_x + self.radius * math.cos(angle_rad)
                y = center_y + self.radius * math.sin(angle_rad)

                # 计算透明度，形成尾巴效果 - 增加最小透明度
                alpha = int(255 * (1 - i * 0.06))  # 减少透明度衰减
                if alpha < 80:  # 提高最小透明度
                    alpha = 80

                painter.setBrush(QColor(0, 122, 204, alpha))

                # 绘制更大的圆点，增加可见性
                point_size = 7 - (i * 0.2)  # 增大基础尺寸，减少衰减
                if point_size < 4:  # 提高最小尺寸
                    point_size = 4

                painter.drawEllipse(
                    int(x - point_size / 2),
                    int(y - point_size / 2),
                    int(point_size),
                    int(point_size),
                )


class LoadingWidget(QWidget):
    """加载动画组件"""

    def __init__(self, message="正在处理...", parent=None):
        super().__init__(parent)
        # 设置固定大小，确保加载框显示正确
        self.message = message
        self.angle = 0

        # 设置固定大小为合适的加载框尺寸
        self.setFixedSize(500, 300)

        # 设置大小策略为固定大小
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # 设置背景
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.98);
                border: 2px solid #007acc;
                border-radius: 15px;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)

        # 创建中心容器，用于限制内容宽度
        center_container = QWidget()
        center_container.setMaximumWidth(460)  # 适应500px的固定宽度
        center_container.setMinimumHeight(220)  # 适应300px的固定高度
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(20, 20, 20, 20)
        center_layout.setSpacing(20)

        # 旋转动画区域 - 创建一个专门的容器
        animation_container = QWidget()
        animation_container.setFixedHeight(100)
        animation_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        self.animation_container = animation_container
        center_layout.addWidget(animation_container)

        # 创建独立的动画覆盖层，确保动画在最上层
        self.animation_overlay = AnimationOverlay(self)
        self.animation_overlay.hide()  # 初始隐藏

        # 消息标签
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 15px;
                line-height: 1.4;
            }
        """)
        center_layout.addWidget(self.message_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #e0e0e0;
                margin: 10px 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #007acc, stop: 0.5 #4fc3f7, stop: 1 #007acc
                );
                border-radius: 3px;
            }
        """)
        center_layout.addWidget(self.progress_bar)

        # 将中心容器添加到主布局
        main_layout.addWidget(center_container, 0, Qt.AlignmentFlag.AlignCenter)

        # 动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(40)  # 40ms刷新一次，更流畅

    def update_animation(self):
        """更新动画"""
        self.angle = (self.angle + 8) % 360  # 更平滑的角度变化

        # 更新覆盖层的角度
        if hasattr(self, "animation_overlay"):
            self.animation_overlay.set_angle(self.angle)

        # 重新计算动画中心位置
        self._update_animation_position()

    def set_message(self, message):
        """设置消息"""
        self.message = message
        self.message_label.setText(message)

    def _update_animation_position(self):
        """更新动画位置"""
        if hasattr(self, "animation_overlay") and hasattr(self, "animation_container"):
            # 确保覆盖层大小与LoadingWidget一致
            self.animation_overlay.setGeometry(self.rect())

            # 计算动画中心位置
            if self.animation_container:
                animation_rect = self.animation_container.geometry()
                center_x = self.width() // 2
                center_y = animation_rect.center().y() + 30  # 往下移动

                # 设置动画中心
                self.animation_overlay.set_animation_center(center_x, center_y)

                # 显示覆盖层并确保在最上层
                self.animation_overlay.show()
                self.animation_overlay.raise_()

    def paintEvent(self, event):
        """绘制背景（动画由覆盖层处理）"""
        super().paintEvent(event)
        # 确保动画位置更新
        self._update_animation_position()

    def show_centered(self, parent_widget):
        """在父控件中心显示"""
        if parent_widget:
            parent_rect = parent_widget.rect()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2,
            )
        self.show()
        self.raise_()

    def closeEvent(self, event):
        """关闭时停止定时器"""
        if hasattr(self, "timer"):
            self.timer.stop()
        if hasattr(self, "animation_overlay"):
            self.animation_overlay.hide()
        super().closeEvent(event)


class StatusLabel(QLabel):
    """状态标签组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 5px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)
        self.setText("就绪")

    def set_status(self, message, status_type="info"):
        """设置状态信息
        status_type: info, success, warning, error
        """
        colors = {
            "info": "#007acc",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
        }

        color = colors.get(status_type, "#007acc")
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                padding: 5px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-weight: bold;
            }}
        """)
        self.setText(message)


class DragDropOverlay(QWidget):
    """拖拽提示覆盖层"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 不设置为独立窗口，作为子控件使用
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background: rgba(0, 122, 204, 0.15);
                border: 3px dashed #007acc;
                border-radius: 15px;
            }
            QLabel {
                color: #007acc;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)

        # 创建布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # 添加图标标签
        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(icon_label)

        # 添加文本标签
        text_label = QLabel("拖拽PDF文件到此处")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        # 添加说明文字
        desc_label = QLabel("支持 .pdf 格式文件")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 16px;
                font-weight: normal;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(desc_label)

        # 默认隐藏
        self.hide()

    def show_overlay(self, parent_widget):
        """显示覆盖层"""
        if parent_widget:
            # 设置父窗口（如果还没有设置的话）
            if self.parent() != parent_widget:
                self.setParent(parent_widget)

            # 设置覆盖层覆盖整个父窗口的客户区
            self.setGeometry(parent_widget.rect())

            # 确保覆盖层在所有子控件之上
        self.raise_()

        self.show()

    def hide_overlay(self):
        """隐藏覆盖层"""
        self.hide()


class TranslationConfigDialog(QDialog):
    connection_test_finished = pyqtSignal(object, bool, str)
    """引擎配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("引擎配置")
        self.setFixedSize(650, 900)
        self.setModal(True)

        # 加载当前配置
        self.load_current_config()

        # 创建UI
        self.setup_ui()

        self.connection_test_finished.connect(self._on_connection_result)

    def setup_ui(self):
        """设置UI界面"""
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox, QLineEdit {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
                min-height: 14px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #007acc;
            }
            QComboBox:hover, QLineEdit:hover {
                border-color: #999;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题
        title_label = QLabel("引擎配置")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #007acc;
                padding: 10px 0;
                border-bottom: 1px solid #ddd;
                margin-bottom: 5px;
            }
        """)
        main_layout.addWidget(title_label)

        # 翻译引擎配置组
        basic_group = QGroupBox("翻译引擎配置")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(12)
        basic_layout.setContentsMargins(15, 25, 15, 25)
        basic_layout.setVerticalSpacing(15)

        # 翻译引擎选择
        self.service_combo = QComboBox()
        self.service_combo.addItems(["bing", "google", "silicon", "ollama"])
        self.service_combo.currentTextChanged.connect(self.on_service_changed)
        basic_layout.addRow("翻译引擎:", self.service_combo)

        # 语言映射字典
        self.lang_display_map = {
            "zh": "中文",
            "en": "英文",
            "ja": "日语",
            "ko": "韩语",
            "zh-TW": "繁体中文",
        }
        self.lang_code_map = {
            "中文": "zh",
            "英文": "en",
            "日语": "ja",
            "韩语": "ko",
            "繁体中文": "zh-TW",
        }

        # 原语言
        self.lang_in_combo = QComboBox()
        self.lang_in_combo.addItems(["英文", "中文", "日语", "韩语", "繁体中文"])
        basic_layout.addRow("原语言:", self.lang_in_combo)

        # 目标语言
        self.lang_out_combo = QComboBox()
        self.lang_out_combo.addItems(["中文", "英文", "日语", "韩语", "繁体中文"])
        basic_layout.addRow("目标语言:", self.lang_out_combo)

        main_layout.addWidget(basic_group)

        # 参数配置组
        self.env_group = QGroupBox("翻译引擎参数")
        self.env_layout = QFormLayout(self.env_group)
        self.env_layout.setSpacing(12)
        self.env_layout.setContentsMargins(15, 25, 15, 25)
        self.env_layout.setVerticalSpacing(15)

        # 环境变量输入框会根据服务类型动态创建

        main_layout.addWidget(self.env_group)

        # 问答引擎配置组
        qa_group = QGroupBox("问答引擎配置")
        qa_layout = QFormLayout(qa_group)
        qa_layout.setSpacing(12)
        qa_layout.setContentsMargins(15, 25, 15, 25)
        qa_layout.setVerticalSpacing(15)

        # 问答引擎选择
        self.qa_service_combo = QComboBox()
        self.qa_service_combo.addItems(["关闭", "silicon", "ollama", "自定义"])
        self.qa_service_combo.currentTextChanged.connect(self.on_qa_service_changed)
        qa_layout.addRow("问答引擎:", self.qa_service_combo)

        main_layout.addWidget(qa_group)

        # 问答引擎参数配置组
        self.qa_env_group = QGroupBox("问答引擎参数")
        self.qa_env_layout = QFormLayout(self.qa_env_group)
        self.qa_env_layout.setSpacing(12)
        self.qa_env_layout.setContentsMargins(15, 25, 15, 25)
        self.qa_env_layout.setVerticalSpacing(15)

        main_layout.addWidget(self.qa_env_group)

        # 添加弹性空间
        spacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        main_layout.addItem(spacer)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # 添加按钮间距
        button_layout.addSpacing(10)

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        main_layout.addLayout(button_layout)

        # 初始化显示
        self.on_service_changed(self.service_combo.currentText())
        self.on_qa_service_changed(self.qa_service_combo.currentText())

    def on_qa_service_changed(self, service):
        """问答引擎改变时的处理"""
        # 清除之前的问答引擎环境变量输入框
        while self.qa_env_layout.rowCount() > 0:
            self.qa_env_layout.removeRow(0)

        if service == "silicon":
            # 创建Silicon问答配置控件
            self.qa_silicon_api_key = QLineEdit()
            self.qa_silicon_api_key.setPlaceholderText("请输入Silicon API Key")
            self.qa_silicon_model = QLineEdit()
            self.qa_silicon_model.setPlaceholderText("例如: Qwen/Qwen2.5-7B-Instruct")

            self.qa_env_layout.addRow("API Key:", self.qa_silicon_api_key)
            self.qa_env_layout.addRow("模型:", self.qa_silicon_model)
            self.qa_test_btn = QPushButton("测试连接")
            self.qa_test_btn.clicked.connect(self._test_qa_connection)
            self.qa_test_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 6px 18px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                    color: #efefef;
                }
            """)
            self.qa_env_layout.addRow("", self.qa_test_btn)
        elif service == "ollama":
            # 创建Ollama问答配置控件
            self.qa_ollama_host = QLineEdit()
            self.qa_ollama_host.setPlaceholderText("例如: http://127.0.0.1:11434")
            self.qa_ollama_model = QLineEdit()
            self.qa_ollama_model.setPlaceholderText("例如: deepseek-r1:1.5b")

            self.qa_env_layout.addRow("服务地址:", self.qa_ollama_host)
            self.qa_env_layout.addRow("模型:", self.qa_ollama_model)
            self.qa_test_btn = QPushButton("测试连接")
            self.qa_test_btn.clicked.connect(self._test_qa_connection)
            self.qa_test_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 6px 18px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                    color: #efefef;
                }
            """)
            self.qa_env_layout.addRow("", self.qa_test_btn)
        elif service == "自定义":
            # 自定义问答引擎
            self.custom_qa_host = QLineEdit()
            self.custom_qa_host.setPlaceholderText("https://api.siliconflow.cn")
            self.custom_qa_key = QLineEdit()
            self.custom_qa_key.setPlaceholderText("可选: API Key")
            self.custom_qa_model = QLineEdit()
            self.custom_qa_model.setPlaceholderText("可选: 模型")

            self.qa_test_btn = QPushButton("测试连接")
            self.qa_test_btn.clicked.connect(self._test_qa_connection)
            self.qa_test_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 6px 18px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                    color: #efefef;
                }
            """)

            self.qa_env_layout.addRow("Host:", self.custom_qa_host)
            self.qa_env_layout.addRow("API Key:", self.custom_qa_key)
            self.qa_env_layout.addRow("模型:", self.custom_qa_model)
            self.qa_env_layout.addRow("", self.qa_test_btn)
        else:
            # 关闭问答引擎
            info_label = QLabel("问答引擎已关闭")
            info_label.setStyleSheet("color: #6c757d; font-style: italic;")
            self.qa_env_layout.addRow(info_label)

    def on_service_changed(self, service):
        """翻译引擎改变时的处理"""
        # 清除之前的环境变量输入框
        while self.env_layout.rowCount() > 0:
            self.env_layout.removeRow(0)

        if service == "silicon":
            # 创建Silicon配置控件
            self.silicon_api_key = QLineEdit()
            self.silicon_api_key.setPlaceholderText("请输入Silicon API Key")
            self.silicon_model = QLineEdit()
            self.silicon_model.setPlaceholderText("例如: Qwen/Qwen2.5-7B-Instruct")

            self.env_layout.addRow("API Key:", self.silicon_api_key)
            self.env_layout.addRow("模型:", self.silicon_model)
        elif service == "ollama":
            # 创建Ollama配置控件
            self.ollama_host = QLineEdit()
            self.ollama_host.setPlaceholderText("例如: http://127.0.0.1:11434")
            self.ollama_model = QLineEdit()
            self.ollama_model.setPlaceholderText("例如: deepseek-r1:1.5b")

            self.env_layout.addRow("服务地址:", self.ollama_host)
            self.env_layout.addRow("模型:", self.ollama_model)
        elif service == "自定义":
            # 自定义翻译服务
            self.custom_host = QLineEdit()
            self.custom_host.setPlaceholderText("http://example.com/api")
            self.custom_key = QLineEdit()
            self.custom_key.setPlaceholderText("可选: API Key")
            self.custom_model = QLineEdit()
            self.custom_model.setPlaceholderText("可选: 模型")

            self.env_layout.addRow("模型:", self.custom_model)

        else:
            # Google/Bing 不需要额外配置
            info_label = QLabel("该翻译引擎无需额外配置")
            info_label.setStyleSheet("color: #6c757d; font-style: italic;")
            self.env_layout.addRow(info_label)

        # 统一添加测试按钮
        self.trans_test_btn = QPushButton("测试连接")
        self.trans_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 6px 18px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #efefef;
            }
        """)
        self.trans_test_btn.clicked.connect(self._test_trans_connection)
        self.env_layout.addRow("", self.trans_test_btn)

    def load_current_config(self):
        """加载当前配置"""
        import json
        import os

        # 默认配置
        self.current_config = {
            "service": "bing",
            "lang_in": "en",
            "lang_out": "zh",
            "envs": {},
        }

        # 默认问答配置
        self.current_qa_config = {"service": "关闭", "envs": {}}

        # 从统一配置文件加载
        config_file = "pdf2zh_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    full_config = json.load(f)
                    if "translation" in full_config:
                        self.current_config.update(full_config["translation"])
                    if "qa_engine" in full_config:
                        self.current_qa_config.update(full_config["qa_engine"])
            except Exception as e:
                print(f"读取配置失败: {e}")

    def save_config(self):
        """保存配置"""
        import json
        import os

        # 收集配置，将显示名称转换为代码
        config = {
            "service": self.service_combo.currentText(),
            "lang_in": self.lang_code_map.get(self.lang_in_combo.currentText(), "en"),
            "lang_out": self.lang_code_map.get(self.lang_out_combo.currentText(), "zh"),
            "envs": {},
        }

        # 收集环境变量
        service = config["service"]
        if service == "silicon":
            if hasattr(self, "silicon_api_key") and self.silicon_api_key.text().strip():
                config["envs"]["SILICON_API_KEY"] = self.silicon_api_key.text().strip()
            if hasattr(self, "silicon_model") and self.silicon_model.text().strip():
                config["envs"]["SILICON_MODEL"] = self.silicon_model.text().strip()
        elif service == "ollama":
            if hasattr(self, "ollama_host") and self.ollama_host.text().strip():
                config["envs"]["OLLAMA_HOST"] = self.ollama_host.text().strip()
            if hasattr(self, "ollama_model") and self.ollama_model.text().strip():
                config["envs"]["OLLAMA_MODEL"] = self.ollama_model.text().strip()
        elif service == "自定义":
            if hasattr(self, "custom_host") and self.custom_host.text().strip():
                config["envs"]["CUSTOM_HOST"] = self.custom_host.text().strip()
            if hasattr(self, "custom_key") and self.custom_key.text().strip():
                config["envs"]["CUSTOM_KEY"] = self.custom_key.text().strip()
            if hasattr(self, "custom_model") and self.custom_model.text().strip():
                config["envs"]["CUSTOM_MODEL"] = self.custom_model.text().strip()

        # 读取现有的完整配置文件
        config_file = "pdf2zh_config.json"
        full_config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    full_config = json.load(f)
            except Exception as e:
                print(f"读取现有配置失败: {e}")

        # 收集问答引擎配置
        qa_config = {"service": self.qa_service_combo.currentText(), "envs": {}}

        # 收集问答引擎环境变量
        qa_service = qa_config["service"]
        if qa_service == "silicon":
            if (
                hasattr(self, "qa_silicon_api_key")
                and self.qa_silicon_api_key.text().strip()
            ):
                qa_config["envs"]["SILICON_API_KEY"] = (
                    self.qa_silicon_api_key.text().strip()
                )
            if (
                hasattr(self, "qa_silicon_model")
                and self.qa_silicon_model.text().strip()
            ):
                qa_config["envs"]["SILICON_MODEL"] = (
                    self.qa_silicon_model.text().strip()
                )
        elif qa_service == "ollama":
            if hasattr(self, "qa_ollama_host") and self.qa_ollama_host.text().strip():
                qa_config["envs"]["OLLAMA_HOST"] = self.qa_ollama_host.text().strip()
            if hasattr(self, "qa_ollama_model") and self.qa_ollama_model.text().strip():
                qa_config["envs"]["OLLAMA_MODEL"] = self.qa_ollama_model.text().strip()
        elif qa_service == "自定义":
            if hasattr(self, "custom_qa_host") and self.custom_qa_host.text().strip():
                qa_config["envs"]["CUSTOM_HOST"] = self.custom_qa_host.text().strip()
            if hasattr(self, "custom_qa_key") and self.custom_qa_key.text().strip():
                qa_config["envs"]["CUSTOM_KEY"] = self.custom_qa_key.text().strip()
            if hasattr(self, "custom_qa_model") and self.custom_qa_model.text().strip():
                qa_config["envs"]["CUSTOM_MODEL"] = self.custom_qa_model.text().strip()

        # 更新翻译配置部分
        full_config["translation"] = config
        # 更新问答引擎配置部分
        full_config["qa_engine"] = qa_config

        # 保存到统一配置文件
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(full_config, f, indent=4, ensure_ascii=False)

        self.current_config = config
        self.current_qa_config = qa_config

    def apply_current_config(self):
        """应用当前配置到UI"""
        # 设置服务
        index = self.service_combo.findText(self.current_config.get("service", "bing"))
        if index >= 0:
            self.service_combo.setCurrentIndex(index)

        # 设置语言，将代码转换为显示名称
        lang_in_code = self.current_config.get("lang_in", "en")
        lang_in_display = self.lang_display_map.get(lang_in_code, "英文")
        index = self.lang_in_combo.findText(lang_in_display)
        if index >= 0:
            self.lang_in_combo.setCurrentIndex(index)

        lang_out_code = self.current_config.get("lang_out", "zh")
        lang_out_display = self.lang_display_map.get(lang_out_code, "中文")
        index = self.lang_out_combo.findText(lang_out_display)
        if index >= 0:
            self.lang_out_combo.setCurrentIndex(index)

        # 设置环境变量
        envs = self.current_config.get("envs", {})
        if hasattr(self, "silicon_api_key") and "SILICON_API_KEY" in envs:
            self.silicon_api_key.setText(envs["SILICON_API_KEY"])
        if hasattr(self, "silicon_model") and "SILICON_MODEL" in envs:
            self.silicon_model.setText(envs["SILICON_MODEL"])
        if hasattr(self, "ollama_host") and "OLLAMA_HOST" in envs:
            self.ollama_host.setText(envs["OLLAMA_HOST"])
        if hasattr(self, "ollama_model") and "OLLAMA_MODEL" in envs:
            self.ollama_model.setText(envs["OLLAMA_MODEL"])
        if hasattr(self, "custom_host") and "CUSTOM_HOST" in envs:
            self.custom_host.setText(envs["CUSTOM_HOST"])
        if hasattr(self, "custom_key") and "CUSTOM_KEY" in envs:
            self.custom_key.setText(envs["CUSTOM_KEY"])
        if hasattr(self, "custom_model") and "CUSTOM_MODEL" in envs:
            self.custom_model.setText(envs["CUSTOM_MODEL"])

        # 设置问答引擎
        qa_service = self.current_qa_config.get("service", "关闭")
        index = self.qa_service_combo.findText(qa_service)
        if index >= 0:
            self.qa_service_combo.setCurrentIndex(index)

        # 设置问答引擎环境变量
        qa_envs = self.current_qa_config.get("envs", {})
        if hasattr(self, "qa_silicon_api_key") and "SILICON_API_KEY" in qa_envs:
            self.qa_silicon_api_key.setText(qa_envs["SILICON_API_KEY"])
        if hasattr(self, "qa_silicon_model") and "SILICON_MODEL" in qa_envs:
            self.qa_silicon_model.setText(qa_envs["SILICON_MODEL"])
        if hasattr(self, "qa_ollama_host") and "OLLAMA_HOST" in qa_envs:
            self.qa_ollama_host.setText(qa_envs["OLLAMA_HOST"])
        if hasattr(self, "qa_ollama_model") and "OLLAMA_MODEL" in qa_envs:
            self.qa_ollama_model.setText(qa_envs["OLLAMA_MODEL"])
        if hasattr(self, "custom_qa_host") and "CUSTOM_HOST" in qa_envs:
            self.custom_qa_host.setText(qa_envs["CUSTOM_HOST"])
        if hasattr(self, "custom_qa_key") and "CUSTOM_KEY" in qa_envs:
            self.custom_qa_key.setText(qa_envs["CUSTOM_KEY"])
        if hasattr(self, "custom_qa_model") and "CUSTOM_MODEL" in qa_envs:
            self.custom_qa_model.setText(qa_envs["CUSTOM_MODEL"])

    def showEvent(self, event):
        """显示对话框时应用配置"""
        super().showEvent(event)
        self.apply_current_config()

    def accept(self):
        """确定按钮处理"""
        self.save_config()
        super().accept()

    def get_config(self):
        """获取当前配置"""
        return self.current_config.copy()

    def get_qa_config(self):
        """获取问答引擎配置"""
        return self.current_qa_config.copy()

    # ================== 连接测试 ==================
    def _test_trans_connection(self):
        service = self.service_combo.currentText()
        url = ""
        headers = {}
        expect_model = None

        if service == "自定义" and hasattr(self, "custom_host"):
            url = self.custom_host.text().strip()
            expect_model = (
                self.custom_model.text().strip()
                if hasattr(self, "custom_model")
                else None
            )
        elif service == "ollama" and hasattr(self, "ollama_host"):
            url = self.ollama_host.text().strip()
            expect_model = (
                self.ollama_model.text().strip()
                if hasattr(self, "ollama_model")
                else None
            )
        elif service == "silicon":
            url = "https://api.siliconflow.cn"
            expect_model = (
                self.silicon_model.text().strip()
                if hasattr(self, "silicon_model")
                else None
            )
            if hasattr(self, "silicon_api_key") and self.silicon_api_key.text().strip():
                headers["Authorization"] = (
                    f"Bearer {self.silicon_api_key.text().strip()}"
                )
        elif service == "bing":
            url = "https://www.bing.com/translator"
        elif service == "google":
            url = "https://translate.google.com/m"

        # 检查需要模型的服务是否填写了模型
        if service in ("silicon", "ollama") and not expect_model:
            QMessageBox.warning(
                self, "测试连接", f"{service} 服务需要指定模型名称，请填写模型字段"
            )
            return

        if not url:
            QMessageBox.warning(self, "测试连接", "缺少可测试的 Host")
            return

        self._perform_connection_test(service, url, headers, expect_model, is_qa=False)

    def _test_qa_connection(self):
        service = self.qa_service_combo.currentText()
        url = ""
        headers = {}
        expect_model = None

        if service == "自定义" and hasattr(self, "custom_qa_host"):
            url = self.custom_qa_host.text().strip()
            expect_model = (
                self.custom_qa_model.text().strip()
                if hasattr(self, "custom_qa_model")
                else None
            )
            if self.custom_qa_key.text().strip():
                headers["Authorization"] = f"Bearer {self.custom_qa_key.text().strip()}"
        elif service == "ollama" and hasattr(self, "qa_ollama_host"):
            url = self.qa_ollama_host.text().strip()
            expect_model = (
                self.qa_ollama_model.text().strip()
                if hasattr(self, "qa_ollama_model")
                else None
            )
        elif service == "silicon" and hasattr(self, "qa_silicon_api_key"):
            url = "https://api.siliconflow.cn"
            expect_model = (
                self.qa_silicon_model.text().strip()
                if hasattr(self, "qa_silicon_model")
                else None
            )
            if self.qa_silicon_api_key.text().strip():
                headers["Authorization"] = (
                    f"Bearer {self.qa_silicon_api_key.text().strip()}"
                )

        # 检查模型是否为空
        if service in ("silicon", "ollama") and not expect_model:
            QMessageBox.warning(
                self, "测试连接", f"{service} 服务需要指定模型名称，请填写模型字段"
            )
            return

        if not url:
            QMessageBox.warning(self, "测试连接", "缺少可测试的 Host")
            return

        self._perform_connection_test(service, url, headers, expect_model, is_qa=True)

    def _perform_connection_test(
        self, service, url, headers, expect_model=None, is_qa=False
    ):
        # 按钮引用
        btn = self.qa_test_btn if is_qa else self.trans_test_btn
        btn.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        # 若网络阻塞，10 秒后强制恢复界面
        def fallback_restore():
            try:
                if btn.isEnabled():
                    return  # 已恢复
                btn.setEnabled(True)
            except RuntimeError:
                # 按钮已被删除
                pass
            finally:
                QApplication.restoreOverrideCursor()

        _QTimer.singleShot(10000, fallback_restore)

        def worker():
            ok = False
            msg = ""
            try:
                # 针对不同服务发送最小有效请求
                if service == "ollama" and expect_model and is_qa:
                    # Ollama QA: POST /api/chat (与智能问答一致)
                    chat_url = url.rstrip("/") + "/v1/chat/completions"
                    payload = {
                        "model": expect_model,
                        "messages": [{"role": "user", "content": "ping"}],
                        "stream": False,
                    }
                    print(f"测试Ollama QA API: {chat_url}")
                    r = requests.post(
                        chat_url, headers=headers, json=payload, timeout=10
                    )
                    ok = r.status_code == 200
                    msg = f"状态码: {r.status_code}" if not ok else ""
                elif service in ("ollama", "自定义") and expect_model and not is_qa:
                    gen_url = url.rstrip("/") + "/v1/chat/completions"
                    payload = {
                        "model": expect_model,
                        "messages": [{"role": "user", "content": "ping"}],
                        "stream": False,
                    }
                    print(f"测试Ollama 翻译API: {gen_url}")
                    r = requests.post(
                        gen_url, headers=headers, json=payload, timeout=10
                    )
                    ok = r.status_code == 200
                    msg = f"状态码: {r.status_code}" if not ok else ""
                elif service == "silicon" and expect_model:
                    # Silicon: POST /v1/chat/completions
                    sil_url = url.rstrip("/") + "/v1/chat/completions"
                    # Silicon的高峰响应比较慢，设置为stream=True
                    payload = {
                        "model": expect_model,
                        "messages": [{"role": "user", "content": "ping"}],
                        "max_tokens": 1,
                        "stream": True,
                    }
                    print(f"测试Silicon API: {sil_url}")
                    r = requests.post(
                        sil_url, headers=headers, json=payload, timeout=10
                    )
                    ok = r.status_code == 200
                    msg = f"状态码: {r.status_code}" if not ok else ""
                elif service == "自定义" and is_qa:
                    # 自定义QA服务
                    custom_url = url.rstrip("/") + "/v1/chat/completions"
                    payload = {
                        "model": expect_model,
                        "messages": [{"role": "user", "content": "ping"}],
                        "max_tokens": 1,
                        "stream": False,
                    }
                    print(f"测试自定义QA API: {custom_url}")
                    r = requests.post(
                        custom_url, headers=headers, json=payload, timeout=10
                    )
                    ok = r.status_code == 200
                    msg = f"状态码: {r.status_code}" if not ok else ""
                else:
                    # 简单 GET/HEAD 测试
                    print(f"测试基本连接: {url}")
                    r = requests.get(url, headers=headers, timeout=10)
                    ok = r.status_code == 200
                    msg = f"状态码: {r.status_code}" if not ok else ""
            except Exception as e:
                msg = str(e)

            # emit result back to GUI thread
            self.connection_test_finished.emit(btn, ok, msg)

        threading.Thread(target=worker, daemon=True).start()

    def _on_connection_result(self, btn, ok, msg):
        QApplication.restoreOverrideCursor()
        btn.setEnabled(True)
        if ok:
            QMessageBox.information(self, "测试连接", "连接成功！")
        else:
            QMessageBox.critical(self, "测试连接", f"连接失败！\n{msg}")


class QADialog(QDialog):
    """问答对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("智能问答")
        self.setModal(False)
        self.resize(600, 700)

        # 对话历史
        self.chat_history = []
        self.pdf_content = ""
        self.current_response = ""  # 当前AI回答

        # 创建问答引擎管理器
        from core.qa_engine import QAEngineManager

        self.qa_manager = QAEngineManager(self)

        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("📚 PDF智能问答")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 10px 0;
            }
        """)
        title_layout.addWidget(title_label)

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        close_btn.clicked.connect(self.hide)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)

        main_layout.addLayout(title_layout)

        # 对话显示区域
        from PyQt6.QtWidgets import QTextEdit

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                background-color: #f8f9fa;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        self.chat_display.setPlaceholderText("对话内容将在这里显示...")
        main_layout.addWidget(self.chat_display)

        # 输入区域
        input_layout = QVBoxLayout()

        # 问题输入框
        self.question_input = QTextEdit()
        self.question_input.setMaximumHeight(120)
        self.question_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #007acc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #0056b3;
            }
        """)
        self.question_input.setPlaceholderText("请输入您的问题...")
        input_layout.addWidget(self.question_input)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 清空对话按钮
        clear_btn = QPushButton("清空对话")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        # 发送按钮
        self.send_btn = QPushButton("发送问题")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.send_btn.clicked.connect(self.send_question)
        button_layout.addWidget(self.send_btn)

        input_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)

        # 状态栏
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)

    def set_pdf_content(self, content):
        """设置PDF内容"""
        self.pdf_content = content
        self.status_label.setText(f"已加载PDF内容 ({len(content)} 字符)")

    def clear_chat(self):
        """清空对话历史"""
        self.chat_history.clear()
        self.chat_display.clear()
        self.status_label.setText("对话已清空")

    def add_message(self, sender, message):
        """添加消息到对话显示区域"""
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")

        if sender == "用户":
            html = f"""<div style="margin-bottom: 15px;">
                <div style="color: #007acc; font-weight: bold; margin-bottom: 5px;">
                    👤 {sender} [{timestamp}]
                </div>
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 8px; border-left: 4px solid #007acc;">
                    {message}
                </div>
            </div>"""
        else:
            html = f"""<div style="margin-bottom: 15px;">
                <div style="color: #28a745; font-weight: bold; margin-bottom: 5px;">
                    🤖 {sender} [{timestamp}]
                </div>
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 4px solid #28a745;">
                    {message}
                </div>
            </div>"""

        self.chat_display.insertHtml(html)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def process_question(self, question):
        """处理问题"""
        # 重置当前回答
        self.current_response = ""

        # 检查PDF内容是否会被截断
        self._check_and_show_truncation_info(question)

        # 开始AI问答
        self.qa_manager.start_qa(
            question=question,
            pdf_content=self.pdf_content,
            chat_history=self.chat_history,
            chunk_callback=self.on_response_chunk,
            completed_callback=self.on_response_completed,
            failed_callback=self.on_response_failed,
        )

    def _check_and_show_truncation_info(self, question):
        """检查并显示截断信息"""
        if not self.pdf_content:
            return

        # 只在首次对话时显示系统提示
        if len(self.chat_history) > 0:
            return

        try:
            from core.qa_engine import QAEngineThread
            from utils.text_processor import text_processor

            # 创建临时QA线程来获取模型信息和处理页面过滤
            temp_thread = QAEngineThread(question, self.pdf_content, self.chat_history)
            model_name = temp_thread._get_current_model()

            # 获取QA设置中的页面配置
            qa_settings = temp_thread.config.get("qa_settings", {})
            pages_config = qa_settings.get("pages", "").strip()

            # 应用页面过滤，获取实际会被处理的内容
            processed_pdf_content = temp_thread._process_pdf_content_by_pages(
                self.pdf_content, pages_config
            )

            # 计算可用token
            system_prompt_template = """你是一个专业的PDF文档分析助手。用户上传了一个PDF文档，你需要基于文档内容回答用户的问题。
PDF文档内容如下：
{pdf_content}
请注意：
1. 请仅基于上述PDF文档内容回答问题
2. 如果问题与文档内容无关，请明确说明
3. 回答要准确、详细，并引用相关页面信息
4. 使用中文回答
"""

            available_tokens = text_processor.calculate_available_tokens(
                model_name=model_name,
                system_prompt=system_prompt_template,
                chat_history=self.chat_history,
                current_question=question,
                max_response_tokens=2000,
            )

            # 检查是否需要截断并显示相应提示（使用过滤后的内容）
            original_tokens = text_processor.count_tokens(processed_pdf_content)
            model_limit = text_processor.get_model_token_limit(model_name)

            # 构建提示信息
            if pages_config:
                page_info = f"（已按配置过滤到第{pages_config}页）"
            else:
                page_info = "（完整文档）"

            if original_tokens > available_tokens:
                # 显示截断提示
                truncation_msg = f"💡 提示：PDF内容{page_info}较长({original_tokens:,} tokens)，已智能截断至{available_tokens:,} tokens以适应{model_name}模型({model_limit:,} tokens限制)。AI将基于最相关的内容回答您的问题。"
                self.add_message("系统", truncation_msg)
            else:
                # 显示未截断提示
                normal_msg = f"📄 提示：PDF内容{page_info}({original_tokens:,} tokens)在{model_name}模型限制范围内({model_limit:,} tokens)，AI将基于完整内容回答您的问题。"
                self.add_message("系统", normal_msg)

        except Exception as e:
            print(f"检查截断信息时出错: {e}")
            # 静默失败，不影响正常问答流程

    def on_response_chunk(self, chunk):
        """处理AI回答片段"""
        self.current_response += chunk

        # 实时更新AI回答显示
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")

        # 如果是第一个chunk，添加AI消息头
        if len(self.current_response) == len(chunk):
            html = f"""<div style="margin-bottom: 15px;" id="current-ai-response">
                <div style="color: #28a745; font-weight: bold; margin-bottom: 5px;">
                    🤖 AI助手 [{timestamp}]
                </div>
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 4px solid #28a745;">
                    {self.current_response}
                </div>
            </div>"""
            self.chat_display.insertHtml(html)
        else:
            # 更新现有的AI回答内容
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)

            # 查找并更新最后一个AI回答
            content = self.chat_display.toHtml()
            if "current-ai-response" in content:
                # 简单替换最后的回答内容
                updated_html = f"""<div style="margin-bottom: 15px;" id="current-ai-response">
                    <div style="color: #28a745; font-weight: bold; margin-bottom: 5px;">
                        🤖 AI助手 [{timestamp}] (思考中...)
                    </div>
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 4px solid #28a745;">
                        {self.current_response}
                    </div>
                </div>"""

                # 重新设置内容（简化处理）
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if 'id="current-ai-response"' in line:
                        # 找到开始位置，替换到对应的结束div
                        start_idx = i
                        div_count = 0
                        end_idx = start_idx
                        for j in range(start_idx, len(lines)):
                            if "<div" in lines[j]:
                                div_count += 1
                            if "</div>" in lines[j]:
                                div_count -= 1
                                if div_count == 0:
                                    end_idx = j
                                    break

                        # 替换内容
                        new_lines = (
                            lines[:start_idx] + [updated_html] + lines[end_idx + 1 :]
                        )
                        new_content = "\n".join(new_lines)

                        # 保存当前滚动位置
                        scrollbar = self.chat_display.verticalScrollBar()
                        current_pos = scrollbar.value()
                        max_pos = scrollbar.maximum()
                        at_bottom = current_pos >= max_pos - 10

                        self.chat_display.setHtml(new_content)

                        # 如果之前在底部，保持在底部
                        if at_bottom:
                            scrollbar.setValue(scrollbar.maximum())
                        else:
                            scrollbar.setValue(current_pos)
                        break

        # 滚动到底部
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def on_response_completed(self):
        """AI回答完成"""
        # 保存到对话历史
        self.chat_history.append(
            {
                "question": self.question_input.toPlainText().strip()
                if hasattr(self, "_last_question")
                else "",
                "answer": self.current_response,
            }
        )

        # 恢复发送按钮
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送问题")
        self.status_label.setText("回答完成")

        # 移除临时ID标记
        content = self.chat_display.toHtml()
        content = content.replace('id="current-ai-response"', "")
        content = content.replace("(思考中...)", "")
        self.chat_display.setHtml(content)

    def on_response_failed(self, error_message):
        """AI回答失败"""
        self.add_message("系统", f"回答失败: {error_message}")

        # 恢复发送按钮
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送问题")
        self.status_label.setText(f"回答失败: {error_message}")

    def send_question(self):
        """发送问题"""
        question = self.question_input.toPlainText().strip()
        if not question:
            return

        # 保存问题用于历史记录
        self._last_question = question

        # 添加用户问题到显示区域
        self.add_message("用户", question)
        self.question_input.clear()

        # 禁用发送按钮
        self.send_btn.setEnabled(False)
        self.send_btn.setText("思考中...")
        self.status_label.setText("正在生成回答...")

        # 调用AI问答功能
        self.process_question(question)


class ChatInputWidget(QTextEdit):
    """支持回车发送的聊天输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

    def keyPressEvent(self, event):
        """处理键盘事件"""
        from PyQt6.QtCore import Qt

        # 检查是否按下回车键（不是Shift+回车）
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() != Qt.KeyboardModifier.ShiftModifier
        ):
            # 发送消息
            if hasattr(self.parent_widget, "send_question"):
                self.parent_widget.send_question()
        else:
            # 其他按键正常处理
            super().keyPressEvent(event)


class EmbeddedQAWidget(QWidget):
    """嵌入式问答组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化Markdown渲染器
        if MARKDOWN_AVAILABLE:
            # 使用commonmark预设并手动启用表格支持
            self.md = MarkdownIt("commonmark", {"breaks": True, "html": True})
            # 启用表格支持
            self.md.enable(["table"])
        else:
            self.md = None

        # 对话历史
        self.chat_history = []
        self.pdf_content = ""
        self.current_response = ""  # 当前AI回答

        # 创建问答引擎管理器
        from core.qa_engine import QAEngineManager

        self.qa_manager = QAEngineManager(self)

        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 对话显示区域 - 使用QTextBrowser支持Markdown渲染
        from PyQt6.QtWidgets import QTextBrowser

        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenExternalLinks(True)  # 支持外部链接
        # 确保支持HTML渲染
        from PyQt6.QtCore import Qt

        self.chat_display.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 15px;
                background-color: white;
                font-size: 14px;
                line-height: 1.8;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
        """)
        self.chat_display.setPlaceholderText("对话内容将在这里显示...")
        main_layout.addWidget(self.chat_display)

        # 输入区域
        input_layout = QVBoxLayout()

        # 问题输入框 - 支持回车发送
        self.question_input = ChatInputWidget(self)
        self.question_input.setMaximumHeight(80)
        self.question_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #007acc;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #0056b3;
            }
        """)
        self.question_input.setPlaceholderText(
            "请输入您的问题...（按回车发送，Shift+回车换行）"
        )
        input_layout.addWidget(self.question_input)

        # 按钮布局
        button_layout = QHBoxLayout()

        # QA配置按钮（放在原来清空按钮的位置）
        config_btn = QPushButton("配置")
        config_btn.setFixedSize(50, 28)
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        config_btn.clicked.connect(self.open_qa_settings)
        button_layout.addWidget(config_btn)

        button_layout.addStretch()

        # 清空对话按钮（移到发送按钮左边）
        clear_btn = QPushButton("清空")
        clear_btn.setFixedSize(50, 28)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        button_layout.addWidget(clear_btn)

        # 添加小间距
        button_layout.addSpacing(5)

        # 发送按钮
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(60, 28)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.send_btn.clicked.connect(self.send_question)
        button_layout.addWidget(self.send_btn)

        # 添加停止按钮
        self._stop_qa_button = QPushButton("停止生成")
        self._stop_qa_button.setFixedSize(80, 28)
        self._stop_qa_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self._stop_qa_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_qa_button.hide()
        self._stop_qa_button.clicked.connect(self._on_stop_qa_clicked)
        button_layout.addWidget(self._stop_qa_button)

        input_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)

        # 状态栏
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
                padding: 2px;
            }
        """)
        main_layout.addWidget(self.status_label)

        # 初始设置为显示
        self.setVisible(True)

    def _preprocess_math(self, text):
        """预处理数学公式，保护它们不被Markdown处理"""
        import re

        # 先处理块级公式，再处理行内公式，避免冲突

        # 保护LaTeX块级数学公式 \[...\]
        latex_block_pattern = r"\\\[([^\]]+)\\\]"
        text = re.sub(
            latex_block_pattern,
            r'<div class="math-block">\1</div>',
            text,
            flags=re.DOTALL,
        )

        # 保护块级数学公式 $$...$$（必须在行内公式之前处理）
        block_math_pattern = r"\$\$([^$]+)\$\$"
        text = re.sub(
            block_math_pattern,
            r'<div class="math-block">\1</div>',
            text,
            flags=re.DOTALL,
        )

        # 保护LaTeX行内数学公式 \(...\)
        latex_inline_pattern = r"\\\(([^)]+)\\\)"
        text = re.sub(
            latex_inline_pattern, r'<span class="math-inline">\1</span>', text
        )

        # 保护行内数学公式 $...$（必须在块级公式之后处理）
        inline_math_pattern = r"\$([^$\n]+)\$"
        text = re.sub(inline_math_pattern, r'<span class="math-inline">\1</span>', text)

        return text

    def _postprocess_math(self, html):
        """后处理数学公式，添加样式"""
        import re

        # 处理行内数学公式
        inline_pattern = r'<span class="math-inline">(.*?)</span>'
        html = re.sub(
            inline_pattern,
            r'<span style="font-family: \'Times New Roman\', serif; font-style: italic; color: #d63384; background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-weight: bold;">\1</span>',
            html,
            flags=re.DOTALL,
        )

        # 处理块级数学公式
        block_pattern = r'<div class="math-block">(.*?)</div>'
        html = re.sub(
            block_pattern,
            r'<div style="text-align: center; margin: 16px 0; padding: 12px; background-color: #f8f9fa; border-radius: 6px; font-family: \'Times New Roman\', serif; font-size: 18px; color: #d63384; font-weight: bold; border: 2px solid #e9ecef;">\1</div>',
            html,
            flags=re.DOTALL,
        )

        return html

    def _render_markdown_to_html(self, text):
        """将Markdown文本渲染为HTML"""
        if not self.md:
            # 如果没有markdown库，返回简单的HTML格式
            return self._fallback_text_to_html(text)

        try:
            # 预处理数学公式
            text = self._preprocess_math(text)

            # 使用markdown-it渲染
            html = self.md.render(text)

            # 后处理数学公式
            html = self._postprocess_math(html)

            # 使用内联样式而不是CSS样式表，提高QTextBrowser兼容性
            # 先处理表格，添加内联样式
            import re

            # 为表格添加内联样式
            html = re.sub(
                r"<table>",
                '<table style="border-collapse: collapse; width: 100%; margin: 16px 0; border: 1px solid #dee2e6;">',
                html,
            )
            html = re.sub(
                r"<th>",
                '<th style="border: 1px solid #dee2e6; padding: 8px 12px; text-align: left; background-color: #f8f9fa; font-weight: bold;">',
                html,
            )
            html = re.sub(
                r"<td>",
                '<td style="border: 1px solid #dee2e6; padding: 8px 12px; text-align: left;">',
                html,
            )

            # 为代码块添加内联样式
            html = re.sub(
                r"<pre><code>",
                '<pre style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 12px; overflow-x: auto; font-family: Consolas, Monaco, monospace; font-size: 13px;"><code>',
                html,
            )
            html = re.sub(
                r"<code>",
                '<code style="background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: Consolas, Monaco, monospace; font-size: 13px;">',
                html,
            )

            # 为引用添加内联样式
            html = re.sub(
                r"<blockquote>",
                '<blockquote style="border-left: 4px solid #007acc; margin: 16px 0; padding-left: 16px; color: #6c757d; font-style: italic;">',
                html,
            )

            styled_html = f"""
            <div style="font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
                {html}
            </div>
            """
            return styled_html
        except Exception as e:
            print(f"Markdown渲染失败: {e}")
            return self._fallback_text_to_html(text)

    def _fallback_text_to_html(self, text):
        """备用的文本到HTML转换（当markdown库不可用时）"""
        import re
        import html

        # 预处理数学公式
        text = self._preprocess_math(text)

        # HTML转义（但保护数学公式标记）
        text = html.escape(text)

        # 恢复数学公式标记
        text = text.replace(
            '&lt;span class="math-inline"&gt;', '<span class="math-inline">'
        )
        text = text.replace("&lt;/span&gt;", "</span>")
        text = text.replace(
            '&lt;div class="math-block"&gt;', '<div class="math-block">'
        )
        text = text.replace("&lt;/div&gt;", "</div>")

        # 简单的文本格式化
        lines = text.split("\n")
        html_lines = []
        in_code_block = False
        in_list = False

        for line in lines:
            original_line = line
            line = line.strip()

            if not line:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append("<br>")
                continue

            # 处理代码块
            if line.startswith("```"):
                if not in_code_block:
                    html_lines.append("<pre><code>")
                    in_code_block = True
                else:
                    html_lines.append("</code></pre>")
                    in_code_block = False
                continue

            if in_code_block:
                html_lines.append(original_line)
                continue

            # 处理标题
            if line.startswith("# "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h3>{line[4:]}</h3>")
            # 处理列表
            elif line.startswith("- ") or line.startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                list_content = line[2:]
                # 处理列表项中的粗体
                list_content = re.sub(
                    r"\*\*(.*?)\*\*", r"<strong>\1</strong>", list_content
                )
                html_lines.append(f"<li>{list_content}</li>")
            # 处理引用
            elif line.startswith("> "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                quote_content = line[2:]
                quote_content = re.sub(
                    r"\*\*(.*?)\*\*", r"<strong>\1</strong>", quote_content
                )
                html_lines.append(f"<blockquote><p>{quote_content}</p></blockquote>")
            # 处理表格行
            elif "|" in line and line.count("|") >= 2:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                # 简单的表格处理
                cells = [cell.strip() for cell in line.split("|")]
                # 去掉首尾的空元素
                if cells and cells[0] == "":
                    cells = cells[1:]
                if cells and cells[-1] == "":
                    cells = cells[:-1]

                if all(
                    cell.replace("-", "").replace(" ", "").replace("|", "") == ""
                    for cell in cells
                ):
                    # 这是表格分隔行，跳过
                    continue
                else:
                    # 这是表格数据行
                    # 检查是否需要开始新表格
                    table_open = False
                    for i in range(
                        len(html_lines) - 1, max(0, len(html_lines) - 10), -1
                    ):
                        if "<table>" in html_lines[i]:
                            table_open = True
                            break
                        elif "</table>" in html_lines[i]:
                            break

                    if not table_open:
                        html_lines.append("<table>")

                    # 处理表格单元格
                    processed_cells = []
                    for cell in cells:
                        # 处理单元格中的粗体和行内代码
                        cell = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", cell)
                        cell = re.sub(r"`(.*?)`", r"<code>\1</code>", cell)
                        processed_cells.append(cell)

                    row_html = (
                        "<tr>"
                        + "".join(f"<td>{cell}</td>" for cell in processed_cells)
                        + "</tr>"
                    )
                    html_lines.append(row_html)
            # 处理普通段落
            else:
                # 如果前面有未闭合的表格，先闭合
                if (
                    html_lines
                    and "<table>" in html_lines
                    and "</table>" not in html_lines[-10:]
                ):
                    html_lines.append("</table>")

                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                # 处理粗体和行内代码
                line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
                line = re.sub(r"`(.*?)`", r"<code>\1</code>", line)
                html_lines.append(f"<p>{line}</p>")

        # 关闭未闭合的标签
        if in_list:
            html_lines.append("</ul>")
        if in_code_block:
            html_lines.append("</code></pre>")
        # 关闭未闭合的表格
        if (
            html_lines
            and "<table>" in html_lines
            and "</table>" not in html_lines[-10:]
        ):
            html_lines.append("</table>")

        # 后处理数学公式
        html_content = "".join(html_lines)
        html_content = self._postprocess_math(html_content)

        return f"""
        <div style="font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
            <style>
                pre {{
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    padding: 12px;
                    overflow-x: auto;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 13px;
                }}
                code {{
                    background-color: #f8f9fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 13px;
                }}
                blockquote {{
                    border-left: 4px solid #007acc;
                    margin: 16px 0;
                    padding-left: 16px;
                    color: #6c757d;
                    font-style: italic;
                    background-color: #f8f9fa;
                }}
                ul {{
                    margin: 16px 0;
                    padding-left: 24px;
                }}
                li {{
                    margin: 4px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }}
                th, td {{
                    border: 1px solid #dee2e6;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
            </style>
            {html_content}
        </div>
        """

    def set_pdf_content(self, content):
        """设置PDF内容"""
        self.pdf_content = content
        self.status_label.setText(f"已加载PDF内容 ({len(content)} 字符)")

    def clear_chat(self):
        """清空对话历史"""
        self.chat_history.clear()
        self.chat_display.clear()
        # 添加简洁的欢迎信息
        welcome_msg = """# 🎉 智能问答面板

💡 **提示**: 请先打开PDF文件，然后就可以开始提问了！

---
"""
        welcome_html = self._render_markdown_to_html(welcome_msg)
        self.chat_display.setHtml(welcome_html)
        self.status_label.setText("对话已清空")

    def open_qa_settings(self):
        """打开QA设置对话框"""
        from ui.qa_settings_dialog import QASettingsDialog

        dialog = QASettingsDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.status_label.setText("QA配置已更新")

    def show_widget(self):
        """显示组件"""
        self.setVisible(True)

    def hide_widget(self):
        """隐藏组件"""
        self.setVisible(False)

    def toggle_widget(self):
        """切换小部件的可见性"""
        self.setVisible(not self.isVisible())

    def hide_title_bar(self):
        """隐藏标题栏"""
        if hasattr(self, "title_label"):
            self.title_label.hide()

    def _reset_qa_buttons(self):
        """恢复发送按钮，隐藏停止按钮"""
        self.send_btn.show()
        self._stop_qa_button.hide()

    def _on_stop_qa_clicked(self):
        """处理停止问答按钮点击事件"""
        if self.qa_manager.is_qa_running():
            self.qa_manager.stop_current_qa()
            self._reset_qa_buttons()
            self.add_message("系统", "已停止回答。")
            self.status_label.setText("操作已停止")
            self.current_response = ""

    def send_question(self):
        """发送问题"""
        question = self.question_input.toPlainText().strip()
        if not question:
            return

        # 保存问题用于历史记录
        self._last_question = question

        # 添加用户问题到显示区域
        self.add_message("用户", question)
        self.question_input.clear()

        # 隐藏发送按钮，显示停止按钮
        self.send_btn.hide()
        self._stop_qa_button.show()
        self.status_label.setText("正在生成回答...")

        # 调用AI问答功能
        self.process_question(question)

    def add_message(self, sender, message):
        """添加消息到对话显示区域"""
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")

        # 构建消息样式
        if sender == "用户":
            color = "#007acc"
        elif sender == "AI助手":
            color = "#28a745"
        else:
            color = "#6c757d"

        # 渲染消息内容为HTML
        message_html = self._render_markdown_to_html(message)

        # 获取当前内容
        current_html = self.chat_display.toHtml()

        # 构建完整的消息HTML（去除背景色）
        # 如果不是第一条消息，添加换行
        if current_html.strip() and "智能问答面板" not in current_html:
            styled_message_html = f"""
            <br>
            <div style="margin-bottom: 20px; border-left: 4px solid {color}; padding-left: 15px;">
                <div style="color: {color}; font-weight: bold; margin-bottom: 8px; font-size: 14px;">
                    {sender} [{timestamp}]
                </div>
                <div style="line-height: 1.6;">
                    {message_html}
                </div>
            </div>
            """
        else:
            styled_message_html = f"""
            <div style="margin-bottom: 20px; border-left: 4px solid {color}; padding-left: 15px;">
                <div style="color: {color}; font-weight: bold; margin-bottom: 8px; font-size: 14px;">
                    {sender} [{timestamp}]
                </div>
                <div style="line-height: 1.6;">
                    {message_html}
                </div>
            </div>
            """

        # 如果是第一条消息，直接设置HTML
        if not current_html.strip() or "智能问答面板" in current_html:
            self.chat_display.setHtml(styled_message_html)
        else:
            # 追加到现有内容
            self.chat_display.insertHtml(styled_message_html)

        # 确保滚动到底部
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def process_question(self, question):
        """处理问题"""
        # 重置当前回答
        self.current_response = ""

        # 检查PDF内容是否会被截断
        self._check_and_show_truncation_info(question)

        # 开始AI问答
        self.qa_manager.start_qa(
            question=question,
            pdf_content=self.pdf_content,
            chat_history=self.chat_history,
            chunk_callback=self.on_response_chunk,
            completed_callback=self.on_response_completed,
            failed_callback=self.on_response_failed,
        )

    def _check_and_show_truncation_info(self, question):
        """检查并显示截断信息"""
        if not self.pdf_content:
            return

        # 只在首次对话时显示系统提示
        if len(self.chat_history) > 0:
            return

        try:
            from core.qa_engine import QAEngineThread
            from utils.text_processor import text_processor

            # 创建临时QA线程来获取模型信息和处理页面过滤
            temp_thread = QAEngineThread(question, self.pdf_content, self.chat_history)
            model_name = temp_thread._get_current_model()

            # 获取QA设置中的页面配置
            qa_settings = temp_thread.config.get("qa_settings", {})
            pages_config = qa_settings.get("pages", "").strip()

            # 应用页面过滤，获取实际会被处理的内容
            processed_pdf_content = temp_thread._process_pdf_content_by_pages(
                self.pdf_content, pages_config
            )

            # 计算可用token
            system_prompt_template = """你是一个专业的PDF文档分析助手。用户上传了一个PDF文档，你需要基于文档内容回答用户的问题。
PDF文档内容如下：
{pdf_content}
请注意：
1. 请仅基于上述PDF文档内容回答问题
2. 如果问题与文档内容无关，请明确说明
3. 回答要准确、详细，并引用相关页面信息
4. 使用中文回答
"""

            available_tokens = text_processor.calculate_available_tokens(
                model_name=model_name,
                system_prompt=system_prompt_template,
                chat_history=self.chat_history,
                current_question=question,
                max_response_tokens=2000,
            )

            # 检查是否需要截断并显示相应提示（使用过滤后的内容）
            original_tokens = text_processor.count_tokens(processed_pdf_content)
            model_limit = text_processor.get_model_token_limit(model_name)

            # 构建提示信息
            if pages_config:
                page_info = f"（已按配置过滤到第{pages_config}页）"
            else:
                page_info = "（完整文档）"

            if original_tokens > available_tokens:
                # 显示截断提示
                truncation_msg = f"💡 提示：PDF内容{page_info}较长({original_tokens:,} tokens)，已智能截断至{available_tokens:,} tokens以适应{model_name}模型({model_limit:,} tokens限制)。AI将基于最相关的内容回答您的问题。"
                self.add_message("系统", truncation_msg)
            else:
                # 显示未截断提示
                normal_msg = f"📄 提示：PDF内容{page_info}({original_tokens:,} tokens)在{model_name}模型限制范围内({model_limit:,} tokens)，AI将基于完整内容回答您的问题。"
                self.add_message("系统", normal_msg)

        except Exception as e:
            print(f"检查截断信息时出错: {e}")
            # 静默失败，不影响正常问答流程

    def on_response_chunk(self, chunk):
        """处理AI回答片段"""
        self.current_response += chunk

        # 简单的流式显示：每次都重新显示完整内容
        if len(self.current_response) == len(chunk):
            # 第一个chunk，添加AI消息头
            timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")

            # 记录开始位置
            self._ai_start_position = len(self.chat_display.toPlainText())

            # 添加AI消息头
            ai_header = f"\n\nAI助手 [{timestamp}]\n"
            self.chat_display.append(ai_header)

            # 添加第一个chunk
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(chunk)
        else:
            # 后续chunk，直接追加
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(chunk)

        # 自动滚动到底部
        self.chat_display.ensureCursorVisible()

    def on_response_completed(self):
        """AI回答完成"""
        # 保存到对话历史
        self.chat_history.append(
            {
                "question": getattr(self, "_last_question", ""),
                "answer": self.current_response,
            }
        )

        # 简化方案：获取流式输出前的内容，然后添加完整的AI回答
        if hasattr(self, "_ai_start_position"):
            # 获取流式输出开始前的所有内容
            current_text = self.chat_display.toPlainText()
            before_ai_text = current_text[: self._ai_start_position]

            # 将之前的纯文本内容转换为HTML
            before_ai_html = before_ai_text.replace("\n", "<br>")

            # 渲染AI回答为完整的Markdown
            timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
            response_html = self._render_markdown_to_html(self.current_response)

            # 构建完整的AI回答HTML
            ai_message_html = f"""
            <br>
            <div style="margin-bottom: 20px; border-left: 4px solid #28a745; padding-left: 15px;">
                <div style="color: #28a745; font-weight: bold; margin-bottom: 8px; font-size: 14px;">
                    AI助手 [{timestamp}]
                </div>
                <div style="line-height: 1.6;">
                    {response_html}
                </div>
            </div>
            """

            # 重新设置完整内容
            full_html = before_ai_html + ai_message_html
            self.chat_display.setHtml(full_html)
        else:
            # 如果没有记录开始位置，直接使用add_message
            self.add_message("AI助手", self.current_response)

        # 恢复发送按钮，隐藏停止按钮
        self._reset_qa_buttons()
        self.status_label.setText("回答完成")

        # 滚动到底部
        self.chat_display.ensureCursorVisible()

    def on_response_failed(self, error_message):
        """AI回答失败"""
        self.add_message("系统", f"回答失败: {error_message}")

        # 恢复发送按钮，隐藏停止按钮
        self._reset_qa_buttons()
        self.status_label.setText(f"回答失败: {error_message}")
