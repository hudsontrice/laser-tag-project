from __future__ import annotations

import os
import tkinter as tk

from src.ui.player_entry import PlayerEntry
from src.ui.splash import SplashScreen
from src.ui.countdown import Countdown   # ← ADD

SPLASH_DURATION_MS = 3000
WINDOW_GEOMETRY = os.getenv("PHOTON_WINDOW_GEOMETRY", "1024x720")
COUNTDOWN_IMAGES_DIR = r"laser-tag-project\reference files\countdown_images"  # ← ADD


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

    # (1) After splash → show PlayerEntry
    def _show_entry() -> None:
        entry = PlayerEntry(root, on_complete=_launch_game)

        # When user starts from PlayerEntry → (2) show Countdown
        def _start_countdown() -> None:
            try:
                entry.destroy()  # clear PlayerEntry UI
            except Exception:
                pass
            Countdown(
                root,
                images_dir=COUNTDOWN_IMAGES_DIR,
                alert_ms=5000,
                background_ms=5000,
                step_ms=1000,
                on_complete=_launch_game,   # (3) after countdown → game start hook
                # size=(1024, 720),          # optional resize
            )

        # Preferred: PlayerEntry exposes an on_start callback
        if hasattr(entry, "on_start"):
            entry.on_start = _start_countdown

        # Keep PlayerEntry’s close handler if present
        if hasattr(entry, "close_app"):
            root.protocol("WM_DELETE_WINDOW", entry.close_app)

    # (3) Game start hook (no audio here, just placeholder)
    def _launch_game() -> None:
		#call to game file. 
        print("Countdown finished — start the game here")

    # Splash first → then _show_entry
    SplashScreen(root, duration_ms=SPLASH_DURATION_MS, on_complete=_show_entry)

    root.mainloop()
    
if __name__ == "__main__":
		launch()

