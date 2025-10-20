from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

import tkinter as tk
from PIL import Image, ImageTk


class Countdown(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        images_dir: str | Path,
        *,
        alert_ms: int = 5000,
        background_ms: int = 5000,
        step_ms: int = 1000,
        on_complete: Optional[Callable[[], None]] = None,
        size: tuple[int, int] | None = None,
    ) -> None:
        super().__init__(master)
        self.pack(expand=True, fill="both")

        self.images_dir = Path(images_dir)
        self.alert_ms = int(alert_ms)
        self.background_ms = int(background_ms)
        self.step_ms = int(step_ms)
        self.on_complete = on_complete
        self.size = size  # Optional resize target (width, height)

        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")

        # UI container
        self._label = tk.Label(self, borderwidth=0, highlightthickness=0)
        self._label.pack(expand=True)

        # Preload images
        self._alert_img = self._load_image(self.images_dir / "alert-on.tif")
        self._bg_img = self._load_image(self.images_dir / "background.tif")
        self._number_imgs = self._load_number_images()

        # State for stepping through numbers
        self._num_index = 0

        # Start sequence: alert → background → numbers
        self._show(self._alert_img)
        self.after(self.alert_ms, self._phase_background)

    # ------------------------
    # Image loading utilities
    # ------------------------
    def _load_image(self, path: Path) -> ImageTk.PhotoImage:
        if not path.exists():
            raise FileNotFoundError(f"Required image missing: {path}")
        img = Image.open(path)
        if self.size:
            img = img.resize(self.size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _load_number_images(self) -> list[tuple[int, ImageTk.PhotoImage]]:
        number_pairs: list[tuple[int, Path]] = []
        for p in self.images_dir.glob("*.tif"):
            name = p.name.lower()
            if name in {"alert-on.tif", "background.tif"}:
                continue
            m = re.fullmatch(r"(\d+)\.tif", name)
            if m:
                number_pairs.append((int(m.group(1)), p))

        # Sort by numeric value descending (e.g., 30, 29, ..., 0)
        number_pairs.sort(key=lambda t: t[0], reverse=True)

        # Load and keep strong references to the PhotoImages
        return [(n, self._load_image(p)) for (n, p) in number_pairs]

    # ------------------------
    # Sequencing
    # ------------------------
    def _show(self, photo: ImageTk.PhotoImage) -> None:
        # Keep strong reference on the label to prevent GC
        self._label.configure(image=photo)
        self._label.image = photo

    def _phase_background(self) -> None:
        self._show(self._bg_img)
        if self._number_imgs:
            self.after(self.background_ms, self._phase_numbers)
        else:
            self.after(self.background_ms, self._finish)

    def _phase_numbers(self) -> None:
        if self._num_index < len(self._number_imgs):
            _, img = self._number_imgs[self._num_index]
            self._show(img)
            self._num_index += 1
            self.after(self.step_ms, self._phase_numbers)
        else:
            self._finish()

    def _finish(self) -> None:
        self.destroy()
        if self.on_complete:
            self.on_complete()


__all__ = ["Countdown"]


if __name__ == "__main__":
    # Quick manual test harness. Adjust `images_dir` and `size` as needed.
    root = tk.Tk()
    root.title("Countdown Test")
    root.geometry("1024x720")

    def done():
        print("Countdown finished.")
        root.destroy()

    Countdown(
        root,
        images_dir=r"laser-tag-project\reference files\countdown_images",
        alert_ms=5000,
        background_ms=5000,
        step_ms=1000,
        on_complete=done,
        # size=(1024, 720),  # uncomment to force-resize images
    )

    root.mainloop()
