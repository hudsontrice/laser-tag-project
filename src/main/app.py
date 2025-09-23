import tkinter as tk

from src.ui.splash import SplashScreen
from src.ui.player_entry import PlayerEntry


def center_window(win: tk.Tk, width: int = 640, height: int = 360) -> None:
	win.update_idletasks()
	x = (win.winfo_screenwidth() // 2) - (width // 2)
	y = (win.winfo_screenheight() // 2) - (height // 2)
	win.geometry(f"{width}x{height}+{x}+{y}")


def main() -> None:
	root = tk.Tk()
	root.title("Laser Tag System")
	center_window(root, 720, 420)

	# Show placeholder splash first
	splash = SplashScreen(root)

	# After 2 seconds, remove splash and show Player Entry
	def show_player_entry():
		splash.close()
		# Ensure the content area expands
		root.rowconfigure(0, weight=1)
		root.columnconfigure(0, weight=1)
		player_entry = PlayerEntry(root)
		# PlayerEntry already calls grid() in its __init__
		player_entry.grid(sticky="nsew")

	root.after(2000, show_player_entry)
	root.mainloop()


if __name__ == "__main__":
	main()

