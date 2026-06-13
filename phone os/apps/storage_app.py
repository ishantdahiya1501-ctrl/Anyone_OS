"""Storage app with storage breakdown and visual bars."""

from __future__ import annotations

import shutil
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


def get_disk_usage() -> dict:
    """Get real disk usage on the system drive."""
    if sys.platform == "win32":
        try:
            usage = shutil.disk_usage("C:\\")
            total = usage.total
            free = usage.free
            used = total - free
            return {
                "total_gb": round(total / (1024**3), 1),
                "used_gb": round(used / (1024**3), 1),
                "free_gb": round(free / (1024**3), 1),
                "percent_used": round(used / total * 100, 1),
            }
        except Exception:
            pass
    return {"total_gb": 32.0, "used_gb": 20.0, "free_gb": 12.0, "percent_used": 62.5}


class StorageBar(QWidget):
    """Visual storage usage bar."""
    def __init__(self, percent: float, color: QColor, label: str, size_text: str, parent=None) -> None:
        super().__init__(parent)
        self.percent = percent
        self.color = color
        self.label_text = label
        self.size_text = size_text
        self.setFixedHeight(52)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background bar
        painter.setBrush(QColor(40, 40, 46))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), 14, 7, 7)

        # Fill
        fill_w = int(self.width() * self.percent / 100)
        painter.setBrush(self.color)
        painter.drawRoundedRect(0, 0, fill_w, 14, 7, 7)

        # Label
        painter.setPen(QColor(255, 255, 255, 220))
        painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        painter.drawText(0, 20, self.width(), 30, Qt.AlignmentFlag.AlignLeft, f"{self.label_text}")
        painter.setPen(QColor(255, 255, 255, 140))
        painter.setFont(QFont("Segoe UI", 12))
        painter.drawText(0, 20, self.width(), 30, Qt.AlignmentFlag.AlignRight, self.size_text)
        painter.end()


class StorageApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Storage", theme, "Storage breakdown", parent)

        info = get_disk_usage()
        total = info["total_gb"]
        used = info["used_gb"]
        free = info["free_gb"]
        pct = info["percent_used"]

        # Overview card
        overview = QFrame()
        overview.setMinimumHeight(160)
        overview.setStyleSheet(
            f"""
            QFrame {{ background: {theme.surface}; border-radius: 12px; }}
            QLabel {{ background: transparent; }}
            """
        )
        ov_layout = QVBoxLayout(overview)
        ov_layout.setContentsMargins(24, 20, 24, 20)
        ov_layout.setSpacing(4)

        free_label = QLabel(f"{free}GB Free")
        free_label.setFont(QFont("Segoe UI Light", 44, QFont.Weight.Light))
        free_label.setStyleSheet(f"color: {theme.foreground.name()};")
        ov_layout.addWidget(free_label, 0, Qt.AlignmentFlag.AlignCenter)

        total_label = QLabel(f"of {total}GB total")
        total_label.setFont(QFont("Segoe UI", 16))
        total_label.setStyleSheet(f"color: {self.theme.muted};")
        ov_layout.addWidget(total_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(overview)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # Category breakdown
        cat_title = QLabel("Storage by Category")
        cat_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        cat_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(cat_title)

        # Simulated categories (proportional to used space)
        categories = [
            ("Apps", used * 0.38, QColor("#0078D7")),
            ("Photos & Videos", used * 0.24, QColor("#E81123")),
            ("System", used * 0.20, QColor("#8764B8")),
            ("Documents", used * 0.10, QColor("#107C10")),
            ("Other", used * 0.08, QColor("#F7630C")),
        ]

        for label, size_gb, color in categories:
            size_gb = round(size_gb, 1)
            bar_pct = (size_gb / total) * 100
            self.content_layout.addWidget(
                StorageBar(bar_pct, color, label, f"{size_gb}GB")
            )

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep2)

        self.add_card("Manage Storage", "Free up space by removing unused apps and files")
        self.add_action_button("Clean Up")
        self.finish()
