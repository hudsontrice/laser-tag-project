
from __future__ import annotations

from tkinter import Frame, Label, Misc
from typing import Callable, Optional

from PIL import Image, ImageTk

LOGO_PATH = "src/assets/logo.jpg" # Moved image to assets folder


class SplashScreen(Frame): # Changed to be call based, that way it can be used from the app.py folder
	"""Minimal splash: show logo, wait, then trigger callback."""

	def __init__(
		self,
		master: Misc,
		*,
		duration_ms: int = 3000,
		on_complete: Optional[Callable[[], None]] = None,
	) -> None:
		super().__init__(master)
		self._photo = ImageTk.PhotoImage(Image.open(LOGO_PATH).resize((1000, 800)))
		Label(self, image=self._photo, borderwidth=0, highlightthickness=0).pack()
		self.pack()
		self._on_complete = on_complete
		self.after(duration_ms, self._finish)

	def _finish(self) -> None:
		self.destroy()
		if self._on_complete:
			self._on_complete()


__all__ = ["SplashScreen"]
