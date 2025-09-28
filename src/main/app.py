"""Application entry point: splash screen followed by player entry UI. -HT"""

from __future__ import annotations

import os
import tkinter as tk

from src.ui.player_entry import PlayerEntry
from src.ui.splash import SplashScreen

SPLASH_DURATION_MS = 3000
WINDOW_GEOMETRY = os.getenv("PHOTON_WINDOW_GEOMETRY", "1024x720")


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

	def _show_entry() -> None:
		entry = PlayerEntry(root)
		root.protocol("WM_DELETE_WINDOW", entry.close_app)

	splash = SplashScreen(root, duration_ms=SPLASH_DURATION_MS, on_complete=_show_entry)

	root.mainloop()


if __name__ == "__main__":
	launch()