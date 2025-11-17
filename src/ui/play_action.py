"""Play action UI"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import font, scrolledtext
from typing import Callable, Dict, List, Optional, Tuple
from pathlib import Path 
from PIL import Image, ImageTk

# Define team colors from the project for consistency
TEAM_COLORS = {
    "red" : "#320000",
    "green" : "#002f00"
}

class PlayAction(tk.Frame):
    TEAM_SIZE = 20

    def __init__(
        self,
        master: tk.Misc,
        red_team_players: list,
        green_team_players: list,
        assets_dir: Path,
        scoring_engine=None,
        on_return_to_entry: Optional[Callable[[], None]] = None,
    ):
        super().__init__(master, bg="#040404")
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        # store player lists for use
        self.red_players = red_team_players
        self.green_players = green_team_players
        self.scoring_engine = scoring_engine
        self.player_icon_labels: Dict[str, List[tk.Label]] = {"red": [], "green": []}
        self.player_score_labels: Dict[str, List[tk.Label]] = {"red": [], "green": []}
        self.player_rows: Dict[str, List[tk.Frame]] = {"red": [], "green": []}
        self.on_return_to_entry = on_return_to_entry
        self.return_button: Optional[tk.Button] = None
        self._game_over = False

        icon_size = (20, 20)
        try:
            icon_path = assets_dir / "baseicon.jpg"
            icon_img = Image.open(icon_path).resize(icon_size, Image.LANCZOS)
            self.base_icon_image = ImageTk.PhotoImage(icon_img)
        except Exception as e:
            print(f"Error loading baseicon.jpg: {e}")
            self.base_icon_image = None

        # Transparent placeholder used so enabling the icon later doesn't shift layout
        try:
            blank_img = Image.new("RGBA", icon_size, (0, 0, 0, 0))
            self.blank_icon_image = ImageTk.PhotoImage(blank_img)
        except Exception:
            self.blank_icon_image = None

        # define fonts
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.score_font = font.Font(family="Segoe UI", size=20)
        self.timer_font = font.Font(family="Segoe UI", size=28, weight="bold")
        self.player_font = font.Font(family="Segoe UI", size=14)
        self.action_font = font.Font(family="Segoe UI", size=12)
        # build the main UI Layout
        self._build_layout()

        # After layout is created, populate score label references for existing players
        # (the team frames were created during _build_layout)
        # Note: _create_team_frame will append to these lists when creating rows.
        self.updateTimer()

    def _build_layout(self) -> None:

        

        # top frame (scores and timer)
        top_frame = tk.Frame(self, bg="#040404", pady=10)
        top_frame.pack(fill="x", side="top")

        # red team score (placeholder)
        tk.Label(top_frame, text="RED TEAM", fg="#f55", bg="#040404", font=self.title_font).pack(side="left", padx=50)
        self.red_score_label = tk.Label(top_frame, text="0", fg="white", bg="#040404", font=self.score_font)
        self.red_score_label.pack(side="left")

        ##time left variable for the set at 360 for 6 minutes
        self.timeleft = 360

        # timer (placeholder)
        ##Timer Layout
        self.timer = tk.Label(top_frame, text="6:00", fg="#ff0", bg="#040404", font=self.score_font)
        self.timer.pack(side="left", fill="x", expand=True)   

        # green team score (placeholder)
        self.green_score_label = tk.Label(top_frame, text="0", fg="white", bg="#040404", font=self.score_font)
        self.green_score_label.pack(side="right", padx=10)
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

        # Create scrolled text widget for action log
        self.action_log = scrolledtext.ScrolledText(
            action_frame, 
            bg="#1a1a1a", 
            fg="#00ff00",  # Green terminal-style text
            font=self.action_font,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED  # Read-only
        )
        self.action_log.pack(fill="both", expand=True)
        
        # Add initial message
        self.add_action("Game started! Waiting for first tag...")
        
        # Configure tag colors for different event types
        self.action_log.tag_config("normal", foreground="#00ff00")
        self.action_log.tag_config("friendly_fire", foreground="#ff6600")
        self.action_log.tag_config("base_hit", foreground="#ffff00", font=("Segoe UI", 12, "bold"))

        # Persistent end/return button anchored below the action log
        self.return_button = tk.Button(
            self,
            text="End Game",
            command=self._handle_end_game_click,
            font=self.title_font,
            bg="#1f1f1f",
            fg="#ffffff",
            activebackground="#333333",
            activeforeground="#ffffff",
            padx=18,
            pady=6,
        )
        self.return_button.pack(side="bottom", pady=(0, 20))

    def _create_team_frame(self, parent: tk.Frame, title: str, bg_color: str, players: List[str]) -> tk.Frame:
        """Creates a team frame and populates it with players."""
        frame = tk.LabelFrame(
            parent, text="", bg=bg_color, fg="#f0f0f0",
            padx=12, pady=12, font=self.title_font,
        )

        rows = tk.Frame(frame, bg=bg_color)
        rows.pack(fill="both", expand=True)

        # Determine which team this frame represents so we can store score labels
        title_lower = title.lower()
        if "red" in title_lower:
            team_key = "red"
        elif "green" in title_lower:
            team_key = "green"
        else:
            team_key = "unknown"

        # add players to the roster
        for player_name in players:
            row = tk.Frame(rows, bg=bg_color)
            row.pack(fill="x", pady=2)

            # Base Icon Label
            icon_label = tk.Label(row, bg=bg_color, width=24)
            if self.blank_icon_image:
                icon_label.config(image=self.blank_icon_image)
                icon_label.image = self.blank_icon_image
            icon_label.pack(side="left", padx=(0,2))

            # Player Name (e.g., "Codename (#ID)")
            tk.Label(
                row, text=player_name, width=22, anchor="w",
                bg=bg_color, fg="#ffffff", font=self.player_font
            ).pack(side="left", padx=6)

            # Player Score (placeholder)
            score_label = tk.Label(
                row, text="0", width=8, anchor="e",
                bg=bg_color, fg="#cccccc", font=self.player_font
            )
            score_label.pack(side="right", padx=6)

            # store references so GameState can update them later
            if team_key in self.player_score_labels:
                self.player_score_labels[team_key].append(score_label)
                self.player_rows[team_key].append(row)
                self.player_icon_labels[team_key].append(icon_label)
            else:
                # fallback if unexpected title
                self.player_score_labels.setdefault(team_key, []).append(score_label)
                self.player_rows.setdefault(team_key, []).append(row)
                self.player_icon_labels.setdefault(team_key, []).append(icon_label)

        return frame

    def add_base_icon(self, team: str, index: int) -> None:
        """Adds the base icon next to the player's name for the remainder of the game."""
        if not self.base_icon_image:
            return

        labels = self.player_icon_labels.get(team)
        if labels and 0 <= index < len(labels):
            icon_label = labels[index]
            icon_label.config(image=self.base_icon_image)
            icon_label.image = self.base_icon_image

    #timer function
    def updateTimer(self):
        if self.timeleft > 0:
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
                self.add_action("GAME OVER! Final scores calculated.", "base_hit")
            self._set_game_over_state()
    
    def add_action(self, message: str, tag: str = "normal") -> None:
        """Add a message to the action log with optional color tag."""
        self.action_log.config(state=tk.NORMAL)  # Enable editing
        self.action_log.insert(tk.END, message + "\n", tag)
        self.action_log.see(tk.END)  # Auto-scroll to bottom
        self.action_log.config(state=tk.DISABLED)  # Disable editing
    
    def log_tag_event(self, attacker_name: str, victim_name: str) -> None:
        """Log a normal tag event."""
        message = f"{attacker_name} tagged {victim_name} (+10 points)"
        self.add_action(message, "normal")
    
    def log_friendly_fire(self, attacker_name: str, victim_name: str) -> None:
        """Log a friendly fire event."""
        message = f"FRIENDLY FIRE! {attacker_name} hit teammate {victim_name} (-10 points each)"
        self.add_action(message, "friendly_fire")
    
    def log_base_hit(self, player_name: str, base_name: str) -> None:
        """Log a base hit event."""
        message = f"** {player_name} DESTROYED {base_name.upper()} BASE! (+100 points) **"
        self.add_action(message, "base_hit")

    # ----- GameState UI callbacks -----
    def update_player_score(self, pref, score: int) -> None:
        """Callback from GameState to update a single player's score label.
        pref is expected to have attributes: team ("red"/"green") and index (int).
        """
        try:
            team = pref.team
            idx = pref.index
        except Exception:
            return

        labels = self.player_score_labels.get(team)
        if labels and 0 <= idx < len(labels):
            labels[idx].config(text=str(score))
            self._recalculate_team_total(team)

    def update_team_scores(self, red_score: int, green_score: int, leader: Optional[str]) -> None:
        """Callback from GameState to update both team score labels and highlight leader."""
        try:
            self.red_score_label.config(text=str(red_score))
            self.green_score_label.config(text=str(green_score))
        except Exception:
            return

        # simple visual cue for leader: change timer color if tied/leader
        if leader is None:
            self.red_score_label.config(fg="white")
            self.green_score_label.config(fg="white")
        elif leader == "red":
            self.red_score_label.config(fg="#ff0")
            self.green_score_label.config(fg="white")
        else:
            self.green_score_label.config(fg="#ff0")
            self.red_score_label.config(fg="white")

    def on_base_hit(self, pref, base_team: str) -> None:
        """Callback to highlight a player row briefly and log the base hit."""
        # Log the event (PlayAction already has logging helpers)
        try:
            self.log_base_hit(pref.name, base_team)
        except Exception:
            pass

        # highlight the player's row for a few seconds
        try:
            self.add_base_icon(pref.team, pref.index)
            rows = self.player_rows.get(pref.team, [])
            if 0 <= pref.index < len(rows):
                row = rows[pref.index]
                orig_bg = row.cget("bg")
                row.config(bg="#444400")
                # restore after 3s
                self.after(3000, lambda: row.config(bg=orig_bg))
        except Exception:
            pass

    def _recalculate_team_total(self, team: str) -> None:
        labels = self.player_score_labels.get(team, [])
        total = 0
        for label in labels:
            try:
                total += int(label.cget("text"))
            except (ValueError, TypeError):
                continue

        if team == "red":
            self.red_score_label.config(text=str(total))
        elif team == "green":
            self.green_score_label.config(text=str(total))

    def _handle_end_game_click(self) -> None:
        """Button always visible: ends the game early or returns after completion."""
        if not self._game_over:
            # Early end requested; stop scoring and trigger game-over UI state
            if self.scoring_engine:
                self.scoring_engine.end_game()
            self.add_action("Game ended early by operator.", "friendly_fire")
            self._set_game_over_state()
        else:
            self._return_to_entry()

    def _set_game_over_state(self) -> None:
        self._game_over = True
        if self.return_button is not None:
            self.return_button.config(text="Return to Player Entry Screen")

    def _return_to_entry(self) -> None:
        if self.return_button is not None:
            self.return_button.config(state=tk.DISABLED)
        if callable(self.on_return_to_entry):
            self.on_return_to_entry()

__all__ = ["PlayAction"]

