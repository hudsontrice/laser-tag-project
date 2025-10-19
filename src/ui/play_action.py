"""Play action UI"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import font
from typing import Dict, List, Optional, Tuple

# Define team colors from the project for consistency
TEAM_COLORS = {
    "red" : "#320000",
    "green" : "#002f00"
}

class PlayAction(tk.Frame):
    TEAM_SIZE = 20

    def __init__(self, master: tk.Misc, red_team_players: list, green_team_players: list):
        super().__init__(master, bg="#040404")
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnfigure(0, weight=1)

        # store player lists for use
        self.red_players = red_team_players
        self.green_players = green_team_players

        # define fonts
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.score_font = font.Font(family="Segoe UI", size=20)
        self.timer_font = font.Font(family="Segoe UI", size=28, weight="bold")
        self.player_font = font.Font(family="Segoe UI", size=14)
        self.action_font = font.Font(family="Segoe UI", size=12)

        # build the main UI Layout
        self._build_layout()

        def _build_layout(self) -> None:
            # top frame (scores and timer)
            top_frame = tk.Frame(self, bg="#040404", pady=10)
            top_frame.pack(fill="x", side="top")

            # red team score (placeholder)
            tk.Label(top_frame, text="RED TEAM", fg="#f55", bg="#040404", font=self.title_font).pack(side="left", padx=50)
            tk.Label(top_frame, text="GREEN TEAM", fg="#5f5", bg="040404", font=self.title_font).pack(side="left")

            # timer (placeholder)
            tk.Label(top_frame, text="6:00", fg="#ff0", bg="#040404", font=self.score_font).pack(side="left", fill="x", expand=True)

            # green team score (placeholder)
            tk.Label(top_frame, text="0", fg="white", bg="#040404", font=self.score_font).pack(side="right", padx=10)
            tk.Label(top_frame, text="GREEN TEAM", fg="#5f5", bg="#040404", font=self.title_font).pack(side="right", padx=50)
