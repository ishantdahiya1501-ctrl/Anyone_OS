"""Music app with player controls and progress."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget, QFrame,
)

from apps.base_app import AppTheme, PhoneAppScreen


TRACKS = [
    {"title": "Sunrise Melody", "artist": "PhoneOS Music", "duration": 215},
    {"title": "Night Drive", "artist": "Synthwave FM", "duration": 248},
    {"title": "Ocean Breeze", "artist": "Chill Beats", "duration": 192},
    {"title": "Electric Dreams", "artist": "Retro Wave", "duration": 276},
    {"title": "Morning Coffee", "artist": "Lo-Fi Studio", "duration": 184},
]


class MusicApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Music", theme, "Player", parent)

        self.playing = False
        self.current_track = 0
        self.elapsed = 0

        # Now playing card
        np_card = QFrame()
        np_card.setMinimumHeight(200)
        np_card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme.accent.name()}, stop:1 rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 140);
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; }}
            """
        )
        np_layout = QVBoxLayout(np_card)
        np_layout.setContentsMargins(24, 20, 24, 20)
        np_layout.setSpacing(6)

        self.track_title = QLabel(TRACKS[0]["title"])
        self.track_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.track_title.setStyleSheet("color: #FFFFFF;")
        np_layout.addWidget(self.track_title)

        self.track_artist = QLabel(TRACKS[0]["artist"])
        self.track_artist.setFont(QFont("Segoe UI", 16))
        self.track_artist.setStyleSheet("color: rgba(255,255,255,180);")
        np_layout.addWidget(self.track_artist)

        np_layout.addStretch(1)

        # Progress bar
        progress_row = QHBoxLayout()
        self.time_elapsed = QLabel("0:00")
        self.time_elapsed.setFont(QFont("Segoe UI", 12))
        self.time_elapsed.setStyleSheet("color: rgba(255,255,255,180);")
        progress_row.addWidget(self.time_elapsed)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, TRACKS[0]["duration"])
        self.progress_slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: rgba(255,255,255,60);
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: #FFFFFF;
                border-radius: 2px;
            }}
            """
        )
        progress_row.addWidget(self.progress_slider, 1)

        self.time_total = QLabel(self._fmt(TRACKS[0]["duration"]))
        self.time_total.setFont(QFont("Segoe UI", 12))
        self.time_total.setStyleSheet("color: rgba(255,255,255,180);")
        progress_row.addWidget(self.time_total)
        np_layout.addLayout(progress_row)

        self.content_layout.addWidget(np_card)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(20)

        prev_btn = QPushButton("⏮")
        prev_btn.setFixedSize(56, 56)
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.setFont(QFont("Segoe UI", 20))
        prev_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: {theme.surface}; border: none; border-radius: 28px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        prev_btn.clicked.connect(self._prev_track)
        ctrl.addWidget(prev_btn)

        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(72, 72)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setFont(QFont("Segoe UI", 26))
        self.play_btn.setStyleSheet(
            f"QPushButton {{ color: #FFF; background: {theme.accent.name()}; border: none; border-radius: 36px; }}"
            f"QPushButton:pressed {{ background: rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 170); }}"
        )
        self.play_btn.clicked.connect(self._toggle_play)
        ctrl.addWidget(self.play_btn)

        next_btn = QPushButton("⏭")
        next_btn.setFixedSize(56, 56)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setFont(QFont("Segoe UI", 20))
        next_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: {theme.surface}; border: none; border-radius: 28px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        next_btn.clicked.connect(self._next_track)
        ctrl.addWidget(next_btn)
        self.content_layout.addLayout(ctrl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # Track list
        list_title = QLabel("Queue")
        list_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        list_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(list_title)

        self.track_labels = []
        for i, track in enumerate(TRACKS):
            card = self.add_card(
                f"  {track['title']}",
                f"  {track['artist']}  •  {self._fmt(track['duration'])}",
                72,
            )
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = lambda e, idx=i: self._select_track(idx)
            self.track_labels.append(card)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

        self.finish()

    def _fmt(self, secs: int) -> str:
        return f"{secs // 60}:{secs % 60:02d}"

    def _toggle_play(self) -> None:
        self.playing = not self.playing
        self.play_btn.setText("⏸" if self.playing else "▶")

    def _next_track(self) -> None:
        self.current_track = (self.current_track + 1) % len(TRACKS)
        self.elapsed = 0
        self._update_track_display()

    def _prev_track(self) -> None:
        self.current_track = (self.current_track - 1) % len(TRACKS)
        self.elapsed = 0
        self._update_track_display()

    def _select_track(self, idx: int) -> None:
        self.current_track = idx
        self.elapsed = 0
        self.playing = True
        self.play_btn.setText("⏸")
        self._update_track_display()

    def _update_track_display(self) -> None:
        track = TRACKS[self.current_track]
        self.track_title.setText(track["title"])
        self.track_artist.setText(track["artist"])
        self.progress_slider.setRange(0, track["duration"])
        self.progress_slider.setValue(0)
        self.time_total.setText(self._fmt(track["duration"]))
        self.time_elapsed.setText("0:00")

    def _tick(self) -> None:
        if self.playing:
            self.elapsed += 1
            track = TRACKS[self.current_track]
            if self.elapsed >= track["duration"]:
                self._next_track()
                return
            self.progress_slider.setValue(self.elapsed)
            self.time_elapsed.setText(self._fmt(self.elapsed))
