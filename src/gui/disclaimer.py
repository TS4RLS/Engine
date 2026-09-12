"""First-launch disclaimer gate, shown before the main window until accepted.

Acceptance is persisted via src.common.app_state so it only shows once per
install -- see gui.py for where this is invoked. A plain QDialog needs none
of the withdraw()/transient() dance the old Tk version required (and that
dance is exactly what made the old dialog silently never appear on Windows
in the first place).
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from src.common import paths

DISCLAIMER_TITLE = "Before you continue"
DISCLAIMER_TEXT = (
    "TS4RLS is an unofficial, independent tool. It is not affiliated with, "
    "endorsed by, or sponsored by Electronic Arts or Maxis.\n\n"
    "It works by writing a single .package file into your Sims 4 Mods "
    "folder. Only one loading screen package can be active at a time, so "
    "remove any other loading screen mod first.\n\n"
    "This software is provided \"as is\", without warranty of any kind — "
    "use it at your own risk."
)


class DisclaimerDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(DISCLAIMER_TITLE)
        self.setModal(True)
        self.setFixedWidth(460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        logo_path = paths.resource_path(os.path.join("assets", "logo.png"))
        if os.path.isfile(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(96, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(logo_label)

        title = QLabel(DISCLAIMER_TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        font = title.font()
        font.setPointSize(font.pointSize() + 3)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        body = QLabel(DISCLAIMER_TEXT)
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(body)

        buttons = QDialogButtonBox()
        continue_btn = buttons.addButton("I understand — Continue", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton("Exit", QDialogButtonBox.ButtonRole.RejectRole)
        continue_btn.setDefault(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
