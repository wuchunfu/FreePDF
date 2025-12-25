"""详细日志对话框"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtGui import QFont, QTextCursor, QColor

from utils.translation_logger import get_translation_logger


class LogDialog(QDialog):
    """详细日志对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("翻译详细日志")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)

        # 获取日志管理器
        self.logger = get_translation_logger()

        # 自动刷新定时器
        self._auto_refresh_timer = QTimer(self)
        self._auto_refresh_timer.timeout.connect(self._refresh_logs)

        self._setup_ui()
        self._connect_signals()

        # 初始加载日志
        self._refresh_logs()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题和状态
        header_layout = QHBoxLayout()

        title_label = QLabel("翻译详细日志")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.log_text)

        # 底部控制区
        control_layout = QHBoxLayout()

        # 自动刷新复选框
        self.auto_refresh_cb = QCheckBox("自动刷新")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.stateChanged.connect(self._toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_cb)

        # 自动滚动复选框
        self.auto_scroll_cb = QCheckBox("自动滚动到底部")
        self.auto_scroll_cb.setChecked(True)
        control_layout.addWidget(self.auto_scroll_cb)

        control_layout.addStretch()

        # 清空按钮
        clear_btn = QPushButton("清空日志")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_btn.clicked.connect(self._clear_logs)
        control_layout.addWidget(clear_btn)

        # 导出按钮
        export_btn = QPushButton("导出日志")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        export_btn.clicked.connect(self._export_logs)
        control_layout.addWidget(export_btn)

        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        refresh_btn.clicked.connect(self._refresh_logs)
        control_layout.addWidget(refresh_btn)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.close)
        control_layout.addWidget(close_btn)

        layout.addLayout(control_layout)

    def _connect_signals(self):
        """连接信号"""
        # 连接日志更新信号
        self.logger.log_updated.connect(self._on_log_updated)

    def _toggle_auto_refresh(self, state):
        """切换自动刷新"""
        if state == Qt.CheckState.Checked.value:
            self._auto_refresh_timer.start(1000)  # 每秒刷新
        else:
            self._auto_refresh_timer.stop()

    def _on_log_updated(self, message):
        """处理新日志消息"""
        self._append_log_line(message)

    def _append_log_line(self, line):
        """添加一行日志（带颜色高亮）"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # 根据日志级别设置颜色
        color = "#d4d4d4"  # 默认颜色
        if "[ERROR]" in line:
            color = "#f44747"  # 红色
        elif "[WARN]" in line:
            color = "#cca700"  # 黄色
        elif "[INFO]" in line:
            color = "#4ec9b0"  # 青色
        elif "[DEBUG]" in line:
            color = "#808080"  # 灰色
        elif "[PROGRESS]" in line:
            color = "#569cd6"  # 蓝色

        # 插入带颜色的文本
        cursor.insertHtml(f'<span style="color: {color};">{line}</span><br>')

        # 自动滚动到底部
        if self.auto_scroll_cb.isChecked():
            self.log_text.setTextCursor(cursor)
            self.log_text.ensureCursorVisible()

    def _refresh_logs(self):
        """刷新日志显示"""
        # 保存当前滚动位置
        scrollbar = self.log_text.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

        # 清空并重新加载所有日志
        self.log_text.clear()

        logs = self.logger.get_all_logs()
        for log in logs:
            self._append_log_line(log)

        # 更新状态
        self.status_label.setText(f"共 {len(logs)} 条日志")

        # 如果之前在底部，则滚动到底部
        if was_at_bottom or self.auto_scroll_cb.isChecked():
            scrollbar.setValue(scrollbar.maximum())

    def _clear_logs(self):
        """清空日志"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有日志吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logger.clear()
            self.log_text.clear()
            self.status_label.setText("日志已清空")

    def _export_logs(self):
        """导出日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志",
            "translation_log.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )

        if file_path:
            try:
                logs_text = self.logger.get_logs_text()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(logs_text)
                QMessageBox.information(self, "导出成功", f"日志已导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出日志时出错:\n{str(e)}")

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 启动自动刷新
        if self.auto_refresh_cb.isChecked():
            self._auto_refresh_timer.start(1000)
        # 刷新一次
        self._refresh_logs()

    def hideEvent(self, event):
        """隐藏事件"""
        super().hideEvent(event)
        # 停止自动刷新
        self._auto_refresh_timer.stop()

    def closeEvent(self, event):
        """关闭事件"""
        self._auto_refresh_timer.stop()
        super().closeEvent(event)
