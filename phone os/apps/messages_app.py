"""Messages app with conversation list and message view."""

from __future__ import annotations

from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from apps.base_app import AppTheme, PhoneAppScreen


CONVERSATIONS = [
    {
        "name": "Family Group",
        "last_msg": "Mom: Don't forget dinner tonight!",
        "time": "08:42",
        "unread": 3,
        "messages": [
            ("Mom", "Hey, are you coming for dinner?", "18:30"),
            ("You", "Yes, on my way!", "18:32"),
            ("Mom", "Don't forget to bring dessert!", "18:45"),
            ("Sis", "I'm already here 😊", "18:50"),
            ("Mom", "Don't forget dinner tonight!", "08:42"),
        ],
    },
    {
        "name": "Ishant",
        "last_msg": "See you at 3!",
        "time": "Yesterday",
        "unread": 0,
        "messages": [
            ("You", "Hey, want to meet up?", "14:00"),
            ("Ishant", "Sure! What time?", "14:05"),
            ("You", "How about 3?", "14:10"),
            ("Ishant", "See you at 3!", "14:12"),
        ],
    },
    {
        "name": "PhoneOS",
        "last_msg": "Welcome to your new phone!",
        "time": "Mon",
        "unread": 1,
        "messages": [
            ("PhoneOS", "Welcome to your new phone!", "09:00"),
            ("PhoneOS", "Swipe up on the lock screen to unlock.", "09:01"),
            ("PhoneOS", "Tap any tile to open an app.", "09:02"),
        ],
    },
    {
        "name": "Service",
        "last_msg": "Your data pack is active",
        "time": "Sun",
        "unread": 0,
        "messages": [
            ("Service", "Your data pack is active until 30 June.", "10:00"),
            ("Service", "You have used 2.3GB of 5GB.", "10:01"),
        ],
    },
]


class MessageBubble(QFrame):
    def __init__(self, sender: str, text: str, time_str: str, is_me: bool, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        bg = theme.accent.name() if is_me else theme.surface
        radius = "14px 14px 4px 14px" if is_me else "14px 14px 14px 4px"

        self.setStyleSheet(
            f"""
            QFrame {{
                background: {bg};
                border-radius: {radius};
            }}
            QLabel {{
                background: transparent;
            }}
            """
        )
        self.setMaximumWidth(500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 6)
        layout.setSpacing(2)

        if not is_me:
            sender_label = QLabel(sender)
            sender_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            sender_label.setStyleSheet(f"color: {theme.accent.name()};")
            layout.addWidget(sender_label)

        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setFont(QFont("Segoe UI", 15))
        msg.setStyleSheet(f"color: {'#FFFFFF' if is_me else theme.foreground.name()};")
        layout.addWidget(msg)

        time_label = QLabel(time_str)
        time_label.setFont(QFont("Segoe UI", 10))
        time_label.setStyleSheet(f"color: {'rgba(255,255,255,160)' if is_me else theme.muted};")
        layout.addWidget(time_label, 0, Qt.AlignmentFlag.AlignRight if is_me else Qt.AlignmentFlag.AlignLeft)


class ConversationView(QWidget):
    """A single conversation thread."""
    back = pyqtSignal()

    def __init__(self, conversation: dict, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self.theme = theme
        self.conversation = conversation
        self.setStyleSheet(f"background: {theme.background};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(f"background: {theme.surface};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        back_btn = QPushButton("<")
        back_btn.setFixedSize(40, 40)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFont(QFont("Segoe UI", 22, QFont.Weight.Light))
        back_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: transparent; border: none; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        back_btn.clicked.connect(self.back.emit)
        header_layout.addWidget(back_btn)

        name_lbl = QLabel(conversation["name"])
        name_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        header_layout.addWidget(name_lbl)
        header_layout.addStretch(1)
        root.addWidget(header)

        # Messages
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {theme.background}; }}")
        msg_widget = QWidget()
        msg_widget.setStyleSheet(f"background: {theme.background};")
        msg_layout = QVBoxLayout(msg_widget)
        msg_layout.setContentsMargins(16, 12, 16, 12)
        msg_layout.setSpacing(8)

        for sender, text, time_str in conversation["messages"]:
            is_me = sender == "You"
            bubble = MessageBubble(sender, text, time_str, is_me, theme)
            wrapper = QHBoxLayout()
            if is_me:
                wrapper.addStretch(1)
                wrapper.addWidget(bubble)
            else:
                wrapper.addWidget(bubble)
                wrapper.addStretch(1)
            msg_layout.addLayout(wrapper)

        msg_layout.addStretch(1)
        scroll.setWidget(msg_widget)
        root.addWidget(scroll, 1)

        # Input bar
        input_bar = QWidget()
        input_bar.setFixedHeight(60)
        input_bar.setStyleSheet(f"background: {theme.surface};")
        input_layout = QHBoxLayout(input_bar)
        input_layout.setContentsMargins(12, 8, 12, 8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setFont(QFont("Segoe UI", 15))
        self.input_field.setStyleSheet(
            f"QLineEdit {{ color: {theme.foreground.name()}; background: {theme.background}; "
            f"border: 1px solid {self.theme.muted}; border-radius: 18px; padding: 0 14px; }}"
        )
        input_layout.addWidget(self.input_field, 1)

        send_btn = QPushButton("→")
        send_btn.setFixedSize(40, 40)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        send_btn.setStyleSheet(
            f"QPushButton {{ color: #FFF; background: {theme.accent.name()}; border: none; border-radius: 20px; }}"
            f"QPushButton:pressed {{ background: rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 170); }}"
        )
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        root.addWidget(input_bar)

    def _send_message(self) -> None:
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()


class MessagesApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Messages", theme, "Conversations", parent)
        self._theme = theme

        for conv in CONVERSATIONS:
            unread_str = f"{conv['unread']} unread" if conv["unread"] else ""
            detail = f"{unread_str}  •  {conv['time']}" if unread_str else conv["time"]
            card = self.add_card(conv["name"], f"{conv['last_msg']}\n{detail}", 90)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = lambda e, c=conv: self._open_conversation(c)

        self.add_action_button("New Message")
        self.finish()

    def _open_conversation(self, conv: dict) -> None:
        view = ConversationView(conv, self._theme, parent=self)
        if hasattr(self, '_stack'):
            pass
        # Find the stacked widget in parent hierarchy
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stack'):
                parent.stack.addWidget(view)
                parent.stack.setCurrentWidget(view)
                view.back.connect(lambda: self._go_back(parent, view))
                break
            parent = parent.parent()

    def _go_back(self, parent, view) -> None:
        parent.stack.setCurrentWidget(self)
        view.deleteLater()
