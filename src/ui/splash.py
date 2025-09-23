import tkinter as tk


class SplashScreen(tk.Frame):
	"""A minimal placeholder splash screen.

	This shows a simple label so you can verify the splash flow works now.
	The other teammate can replace this with an image later without changing
	the app flow.
	"""

	def __init__(self, master: tk.Misc):
		super().__init__(master)
		# Make root expandable when using grid
		master.rowconfigure(0, weight=1)
		master.columnconfigure(0, weight=1)

		# Place this frame with grid so we don't mix managers on the same parent
		self.grid(row=0, column=0, sticky="nsew")

		# Inside this frame we can use pack freely
		self.configure(bg="#111")
		label = tk.Label(
			self,
			text="Laser Tag System\nLoading...",
			fg="#0f0",
			bg="#111",
			font=("Segoe UI", 24, "bold"),
			justify="center",
		)
		label.pack(expand=True, fill="both", padx=24, pady=24)

	def close(self):
		"""Remove the splash from the layout and destroy it."""
		self.grid_forget()
		self.destroy()

