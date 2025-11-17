from __future__ import annotations

"""App entry point and simple page flow controller.
Flow: Splash -> PlayerEntry -> Countdown -> PlayAction.
"""

import os
import random
import tkinter as tk
from pathlib import Path
from threading import Thread
from typing import Optional

from src.ui.countdown import Countdown
from src.ui.player_entry import PlayerEntry
from src.ui.play_action import PlayAction
from src.ui.splash import SplashScreen
from src.logic.scoring import Logic
from src.logic.game_state import GameState
from src.net.udp_receiver import UDPServer
from src.net.udp_sender import UDPSender


SPLASH_DURATION_MS = 3000
# Default window size large enough to show both team panes without manual maximization.
WINDOW_GEOMETRY = os.getenv("PHOTON_WINDOW_GEOMETRY", "1366x820")
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
COUNTDOWN_IMAGES_DIR = str(ASSETS_DIR)


def _play_random_track(base_dir: Path) -> None:
    """Play a random track from tracks 1 thro 8, [Track01.mp3 ... Track08.mp3] (best effort).

    Falls back silently if the module or chosen file is missing.
    """
    try:
        from playsound import PlaysoundException, playsound  # type: ignore[import-not-found]
    except ImportError:
        return

    track_number = random.randint(1, 8)
    filename = f"Track{track_number:02}.mp3"
    track_path = base_dir / filename
    if not track_path.exists():  # If assets incomplete, just skip, don't break.
        return

    def _runner() -> None:
        try:
            playsound(str(track_path), block=True)
        except PlaysoundException:
            pass
        except Exception:
            pass

    Thread(target=_runner, daemon=True).start()


def _center(root: tk.Tk, geometry: str) -> None:
    """Apply the given geometry string and center the window on screen."""
    root.geometry(geometry)
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


class App:
    """Controller that manages page transitions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.entry: Optional[PlayerEntry] = None
        self.countdown_view: Optional[Countdown] = None
        self.play_action_view: Optional[PlayAction] = None
        self.red_roster: list[str] = []
        self.green_roster: list[str] = []
        self.red_equipment_ids: list[int] = []
        self.green_equipment_ids: list[int] = []
        self._audio_started = False

        # Central GameState (scoring + UI bridge)
        self.game_state = GameState()
        self.scoring = Logic(self.game_state) # Create udp send/rec and start score tracking

        self.root.title("Photon Entry Terminal")
        _center(self.root, WINDOW_GEOMETRY)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self.force_quit)

        # Splash -> PlayerEntry
        SplashScreen(self.root, duration_ms=SPLASH_DURATION_MS, on_complete=self.show_entry)

    def show_entry(self) -> None:
        """Show the PlayerEntry page."""
        if self.countdown_view is not None:
            self.countdown_view.destroy()
            self.countdown_view = None

        self.entry = PlayerEntry(self.root, on_complete=self.start_countdown)

    def start_countdown(self) -> None:
        """PlayerEntry -> Countdown, capturing rosters before moving on."""
        if self.entry is not None:
            self.red_roster, self.green_roster, self.red_equipment_ids, self.green_equipment_ids = self.entry.pop_rosters()
            self.entry.cleanup()
            self.entry = None

        if self.countdown_view is not None:
            self.countdown_view.destroy()

        self.countdown_view = Countdown(
            self.root,
            images_dir=COUNTDOWN_IMAGES_DIR,
            alert_ms=5000,
            background_ms=5000,
            step_ms=1000,
            on_complete=self.launch_game,
            audio_trigger_value=14,
            on_audio_trigger=self._trigger_game_audio,
        )

    def launch_game(self) -> None:
        """Countdown -> PlayAction and kick off background music (best effort)."""
        if self.countdown_view is not None:
            self.countdown_view.destroy()
            self.countdown_view = None

        if self.play_action_view is not None:
            self.play_action_view.destroy()

        # Register rosters with the GameState so UI updates map correctly
        try:
            self.game_state.register_rosters(self.red_roster, self.green_roster, self.red_equipment_ids, self.green_equipment_ids)
        except Exception:
            pass

        self.scoring.start_game()

        self.play_action_view = PlayAction(
            self.root,
            self.red_roster,
            self.green_roster,
            ASSETS_DIR,
            self.scoring,
            on_return_to_entry=self.return_to_entry,
            on_timer_start=self._trigger_game_audio,
        )

        # Wire GameState -> PlayAction UI callbacks
        try:
            self.game_state.bind_ui(
                on_player_score=self.play_action_view.update_player_score,
                on_team_scores=self.play_action_view.update_team_scores,
                on_base_hit=self.play_action_view.on_base_hit,
            )
        except Exception:
            pass

        # Push initial scores into the UI so labels show 0 (or any pre-existing values)
        try:
            # Team totals
            self.play_action_view.update_team_scores(
                self.game_state.team_scores.get("red", 0),
                self.game_state.team_scores.get("green", 0),
                None,
            )

            # Individual player scores: iterate equipment id lists in the same order used to build the UI
            for eid in self.red_equipment_ids:
                pref = self.game_state.players_by_eid.get(eid)
                if pref is not None:
                    score = self.game_state.player_scores.get(eid, 0)
                    self.play_action_view.update_player_score(pref, score)

            for eid in self.green_equipment_ids:
                pref = self.game_state.players_by_eid.get(eid)
                if pref is not None:
                    score = self.game_state.player_scores.get(eid, 0)
                    self.play_action_view.update_player_score(pref, score)
        except Exception:
            # Best-effort; if UI not ready ignore
            pass

        # Keep legacy reference for Logic fallback logging
        self.scoring.play_action_screen = self.play_action_view
        
        # Start scoring UDP listener in background thread
        def run_scoring():
            self.scoring.main_loop(
                self.red_equipment_ids, self.green_equipment_ids,
                self.red_roster, self.green_roster
            )
        
        Thread(target=run_scoring, daemon=True).start()

    def _trigger_game_audio(self) -> None:
        if self._audio_started:
            return
        self._audio_started = True
        _play_random_track(ASSETS_DIR)
            
    def return_to_entry(self) -> None:
        """Tear down the PlayAction view and show Player Entry again."""
        try:
            if self.scoring.game_active:
                self.scoring.end_game()
        except Exception:
            pass

        if self.play_action_view is not None:
            try:
                self.play_action_view.destroy()
            except Exception:
                pass
            self.play_action_view = None

        # Reset cached rosters/equipment for the next game
        self.red_roster = []
        self.green_roster = []
        self.red_equipment_ids = []
        self.green_equipment_ids = []

        self.show_entry()

    def force_quit(self, _event: Optional[tk.Event] = None) -> None:
        """Handle window close (X) by tearing everything down like Ctrl+C."""
        try:
            if self.entry is not None:
                self.entry.cleanup()
                self.entry = None
        except Exception:
            pass

        for view_attr in ("countdown_view", "play_action_view"):
            view = getattr(self, view_attr, None)
            if view is not None:
                try:
                    view.destroy()
                except Exception:
                    pass
                setattr(self, view_attr, None)

        try:
            if self.scoring.game_active:
                self.scoring.end_game()
        except Exception:
            pass

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass


def launch() -> None:
    """Create the Tk root and run the app controller."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    launch()

