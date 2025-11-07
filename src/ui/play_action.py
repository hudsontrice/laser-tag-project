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

    def __init__(self, master: tk.Misc, red_team_players: list, green_team_players: list, scoring_engine=None):
        super().__init__(master, bg="#040404")
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        # store player lists for use
        self.red_players = red_team_players
        self.green_players = green_team_players
        self.scoring_engine = scoring_engine

        # define fonts
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.score_font = font.Font(family="Segoe UI", size=20)
        self.timer_font = font.Font(family="Segoe UI", size=28, weight="bold")
        self.player_font = font.Font(family="Segoe UI", size=14)
        self.action_font = font.Font(family="Segoe UI", size=12)

        # build the main UI Layout
        self._build_layout()
        self.updateTimer()

    def _build_layout(self) -> None:

        

        # top frame (scores and timer)
        top_frame = tk.Frame(self, bg="#040404", pady=10)
        top_frame.pack(fill="x", side="top")

        # red team score (placeholder)
        tk.Label(top_frame, text="RED TEAM", fg="#f55", bg="#040404", font=self.title_font).pack(side="left", padx=50)
        tk.Label(top_frame, text="0", fg="white", bg="#040404", font=self.score_font).pack(side="left")

        ##time left variable for the set at 360 for 6 minutes
        self.timeleft = 360

        # timer (placeholder)
        ##Timer Layout
        self.timer = tk.Label(top_frame, text="6:00", fg="#ff0", bg="#040404", font=self.score_font)
        self.timer.pack(side="left", fill="x", expand=True)   

        # green team score (placeholder)
        tk.Label(top_frame, text="0", fg="white", bg="#040404", font=self.score_font).pack(side="right", padx=10)
        tk.Label(top_frame, text="GREEN TEAM", fg="#5f5", bg="#040404", font=self.title_font).pack(side="right", padx=50)

        # roster frame
        roster_frame = tk.Frame(self, bg="#040404", padx=20)
        roster_frame.pack(fill="both", expand=True)

        # red team roster
        self._create_team_frame(
            roster_frame, "Red Team", TEAM_COLORS["red"], self.red_players
        ).pack(side="left", fill="both", expand=True, padx=(0,10))

        # green team roster
        self._create_team_frame(
            roster_frame, "Green Team", TEAM_COLORS["green"], self.green_players
        ).pack(side="right", fill="both", expand=True, padx=(10, 0))

        # bottom frame (action log)
        action_frame = tk.LabelFrame(
            self, text="Current Game Action", bg="#111", fg="#e0e0e0",
            font=self.player_font, padx=10, pady=10
        )
        action_frame.pack(fill="both", expand=True, side="bottom", padx=20, pady=(10,20))

        # placeholder text for the action log
        tk.Label(
            action_frame, text="--- Game events will appear here ---", bg="#111", fg="#999", font=self.action_font
        ).pack(anchor="nw")

    def _create_team_frame(self, parent: tk.Frame, title: str, bg_color: str, players: List[str]) -> tk.Frame:
        """Creates a team frame and populates it with players."""
        frame = tk.LabelFrame(
            parent, text="", bg=bg_color, fg="#f0f0f0",
            padx=12, pady=12, font=self.title_font,
        )

        rows = tk.Frame(frame, bg=bg_color)
        rows.pack(fill="both", expand=True)

        # add players to the roster
        # for this sprint, display the names passed from player_entry
        for player_name in players:
            row = tk.Frame(rows, bg=bg_color)
            row.pack(fill="x", pady=2)

            # Player Name (e.g., "Codename (#ID)")
            tk.Label(
                row, text=player_name, width=22, anchor="w",
                bg=bg_color, fg="#ffffff", font=self.player_font
            ).pack(side="left", padx=6)

            # Player Score (placeholder)
            tk.Label(
                row, text="0", width=8, anchor="e",
                bg=bg_color, fg="#cccccc", font=self.player_font
            ).pack(side="right", padx=6)

        return frame

    #timer function
    def updateTimer(self):
        if self.timeleft > 0:
            print("timer running")
            mins = self.timeleft // 60
            seconds = self.timeleft % 60
            self.timer.config(text=f"{mins:02d}:{seconds:02d}")
            self.timeleft -=1    
            self.timer.after(1000, self.updateTimer)
        else:
            self.timer.config(text=f"GAME OVER")
            # Broadcast game end code 221 three times
            if self.scoring_engine:
                self.scoring_engine.end_game()

__all__ = ["PlayAction"]

