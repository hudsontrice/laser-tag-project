from __future__ import annotations

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


SPLASH_DURATION_MS = 3000
WINDOW_GEOMETRY = os.getenv("PHOTON_WINDOW_GEOMETRY", "1024x720")
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
COUNTDOWN_IMAGES_DIR = str(ASSETS_DIR)


def _play_random_track(base_dir: Path) -> None:
    try:
        from playsound import PlaysoundException, playsound  # type: ignore[import-not-found]
    except ImportError:
        return

    try:
        tracks = [
            p
            for p in base_dir.iterdir()
            if p.suffix.lower() == ".mp3" and p.stem.lower().startswith("track")
        ]
    except OSError:
        return

    if not tracks:
        return

    track = random.choice(tracks)

    def _runner() -> None:
        try:
            playsound(str(track), block=True)
        except PlaysoundException:
            pass
        except Exception:
            pass

    Thread(target=_runner, daemon=True).start()


def _center(root: tk.Tk, geometry: str) -> None:
    """Apply the given geometry string and centre the window. -HT"""
    root.geometry(geometry)
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def launch() -> None:
    root = tk.Tk()
    root.title("Photon Entry Terminal")
    _center(root, WINDOW_GEOMETRY)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    entry: Optional[PlayerEntry] = None
    countdown_view: Optional[Countdown] = None
    play_action_view: Optional[PlayAction] = None
    red_roster: list[str] = []
    green_roster: list[str] = []
    
    def _start_countdown() -> None:
        nonlocal entry, countdown_view, red_roster, green_roster

        if entry is not None:
            red_roster, green_roster = entry.pop_rosters()
            entry.cleanup()
            entry = None

        if countdown_view is not None:
            countdown_view.destroy()

        countdown_view = Countdown(
            root,
            images_dir=COUNTDOWN_IMAGES_DIR,
            alert_ms=5000,
            background_ms=5000,
            step_ms=1000,
            on_complete=_launch_game,
        )
            
    # (1) After splash → show PlayerEntry
    def _show_entry() -> None:
        nonlocal entry, countdown_view

        if countdown_view is not None:
            countdown_view.destroy()
            countdown_view = None

        entry = PlayerEntry(root, on_complete=_start_countdown)
        root.protocol("WM_DELETE_WINDOW", entry.close_app)

    # (3) Game start hook (no audio here, just placeholder)
    def _launch_game() -> None:
        nonlocal countdown_view, play_action_view

        if countdown_view is not None:
            countdown_view.destroy()
            countdown_view = None

        if play_action_view is not None:
            play_action_view.destroy()

        play_action_view = PlayAction(root, red_roster, green_roster)
        _play_random_track(ASSETS_DIR)

    # Splash first → then _show_entry
    SplashScreen(root, duration_ms=SPLASH_DURATION_MS, on_complete=_show_entry)

    root.mainloop()
    
if __name__ == "__main__":
    launch()

