"""Launcher: splash -> player entry.

Provides a simple two-stage UI flow to satisfy multi-screen navigation
requirements while keeping scope minimal. Splash is a lightweight
placeholder in `src/ui/splash.py`.
"""

import tkinter as tk

from src.ui.splash import SplashScreen
from src.ui.player_entry import PlayerEntry


SPLASH_DURATION_MS = 1800  # adjustable delay before switching screens


def center(root: tk.Tk, w: int = 720, h: int = 420) -> None:
	root.update_idletasks()
	x = (root.winfo_screenwidth() // 2) - (w // 2)
	y = (root.winfo_screenheight() // 2) - (h // 2)
	root.geometry(f"{w}x{h}+{x}+{y}")


def launch():
	root = tk.Tk()
	root.title("Laser Tag System")
	center(root)

	splash = SplashScreen(root)

	def show_player_entry():
		splash.close()
		player = PlayerEntry(root)
		# PlayerEntry already grids itself in __init__
		player.grid(sticky="nsew")

	root.after(SPLASH_DURATION_MS, show_player_entry)
	root.mainloop()


if __name__ == "__main__":  # allow module import without auto-run
	launch()

