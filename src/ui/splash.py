"""Simple functional splash screen placeholder.

Replaces the earlier no-op placeholder so the main app can demonstrate
multi-screen navigation: splash -> player entry. Intended to be replaced
later with a richer graphical version.
"""

import tkinter as tk


class SplashScreen(tk.Frame):
	def __init__(self, master: tk.Misc):
		super().__init__(master, bg="#111111")
		self.grid(row=0, column=0, sticky="nsew")
		master.rowconfigure(0, weight=1)
		master.columnconfigure(0, weight=1)

		title = tk.Label(
			self,
			text="Laser Tag System",
			font=("Segoe UI", 28, "bold"),
			fg="#4ade80",  # green accent
			bg="#111111",
		)
		subtitle = tk.Label(
			self,
			text="Loading...",
			font=("Segoe UI", 14),
			fg="#cccccc",
			bg="#111111",
		)
		title.pack(pady=(60, 12))
		subtitle.pack()

	def close(self):
		self.grid_forget()
		self.destroy()

