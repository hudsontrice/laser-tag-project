"""Player entry UI for Sprint 2 requirements."""

from __future__ import annotations

import os
import random
import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Optional, Tuple

from src.db import db_connect
from src.net.udp_sender import UDPSender

DEFAULT_UDP_IP = os.getenv("PHOTON_UDP_TARGET", "127.0.0.1")
DEFAULT_UDP_PORT = int(os.getenv("PHOTON_UDP_PORT", "7500"))


class PlayerEntry(tk.Frame):
    TEAM_SIZE = 20

    def __init__(self, master: tk.Misc):
        super().__init__(master, bg="#040404")
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.sender = UDPSender(DEFAULT_UDP_IP, DEFAULT_UDP_PORT)

        self.player_id_var = tk.StringVar()
        self.codename_var = tk.StringVar()
        self.equipment_var = tk.StringVar()
        self.target_ip_var = tk.StringVar(value=self.sender.ip)
        self.target_port_var = tk.StringVar(value=str(self.sender.port))

        self.team_slots: Dict[str, List[Dict[str, tk.StringVar]]] = {
            "red": self._make_empty_slots(),
            "green": self._make_empty_slots(),
        }

        # Build the UI components that instructors interact with during player entry.
        self._build_layout()
        self.player_entry.focus_set()

    def _make_empty_slots(self) -> List[Dict[str, tk.StringVar]]:
        return [
            {"name": tk.StringVar(value=""), "equip": tk.StringVar(value="—")}
            for _ in range(self.TEAM_SIZE)
        ]

    def _build_layout(self) -> None:
        top = tk.Frame(self, bg="#040404")
        top.pack(fill="x", padx=20, pady=12)

        # Layout contains three major regions: the input form, UDP settings, and the roster board.
        form = tk.LabelFrame(top, text="Player Entry", bg="#111111", fg="#e0e0e0", padx=16, pady=12)
        form.pack(side="left", fill="x", expand=True)
        form.columnconfigure(1, weight=1)

        # Form region handles player information entry with simple textual hints.
        tk.Label(form, text="Player ID", bg="#111111", fg="#ffffff").grid(row=0, column=0, sticky="w", pady=4)
        self.player_entry = tk.Entry(form, textvariable=self.player_id_var, width=14)
        self.player_entry.grid(row=0, column=1, sticky="we", pady=4)

        id_hint = tk.Label(
            form,
            text="Existing players: enter their ID to load the saved codename automatically.",
            bg="#111111",
            fg="#9dc4ff",
            font=("Segoe UI", 9, "italic"),
            wraplength=260,
            justify="left",
        )
        id_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))

        tk.Label(form, text="Codename", bg="#111111", fg="#ffffff").grid(row=2, column=0, sticky="w", pady=4)
        self.codename_entry = tk.Entry(form, textvariable=self.codename_var)
        self.codename_entry.grid(row=2, column=1, sticky="we", pady=4)

        tk.Label(form, text="Equipment ID", bg="#111111", fg="#ffffff").grid(row=3, column=0, sticky="w", pady=4)
        self.equipment_entry = tk.Entry(form, textvariable=self.equipment_var, width=14)
        self.equipment_entry.grid(row=3, column=1, sticky="we", pady=4)

        button_row = tk.Frame(form, bg="#111111")
        # Action buttons keep the workflow focused on saving the player or clearing the form.
        button_row.grid(row=4, column=0, columnspan=2, sticky="we", pady=(10, 0))

        tk.Button(button_row, text="Add Player", command=self.save_player, width=14).pack(side="left", padx=(0, 8))
        tk.Button(button_row, text="Clear", command=self._clear_form).pack(side="left")

        network = tk.LabelFrame(top, text="UDP Target", bg="#111111", fg="#e0e0e0", padx=16, pady=12)
        # Network panel exposes the broadcast destination so instructors can adjust hardware targets on demand.
        network.pack(side="left", padx=(12, 0))

        tk.Label(network, text="IP", bg="#111111", fg="#ffffff").grid(row=0, column=0, sticky="w")
        tk.Entry(network, textvariable=self.target_ip_var, width=16).grid(row=0, column=1, padx=(4, 0))

        tk.Label(network, text="Port", bg="#111111", fg="#ffffff").grid(row=1, column=0, sticky="w", pady=(6, 0))
        tk.Entry(network, textvariable=self.target_port_var, width=8).grid(row=1, column=1, padx=(4, 0), pady=(6, 0))

        tk.Button(network, text="Apply", command=self._apply_network).grid(row=2, column=0, columnspan=2, pady=(12, 0))

        board = tk.Frame(self, bg="#040404")
        # Board visualises red and green teams so the instructor can monitor roster balance at a glance.
        board.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._create_team_frame(board, "Red Team", "#320000", self.team_slots["red"]).pack(
            side="left", expand=True, fill="both", padx=(0, 14)
        )
        self._create_team_frame(board, "Green Team", "#002f00", self.team_slots["green"]).pack(
            side="left", expand=True, fill="both"
        )

        self.player_entry.bind("<FocusOut>", self._autofill_codename)
        self.player_entry.bind("<Return>", self._autofill_codename)
        self.equipment_entry.bind("<Return>", lambda _event: self.save_player())

    def _create_team_frame(self, parent: tk.Frame, title: str, bg_color: str, slots: List[Dict[str, tk.StringVar]]) -> tk.Frame:
        frame = tk.LabelFrame(parent, text=title, bg=bg_color, fg="#f0f0f0", padx=12, pady=12)
        rows = tk.Frame(frame, bg=bg_color)
        rows.pack(fill="both", expand=True)

        for idx, slot in enumerate(slots, start=1):
            row = tk.Frame(rows, bg=bg_color)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{idx:02}", width=4, anchor="e", bg=bg_color, fg="#cccccc").pack(side="left")
            tk.Label(row, textvariable=slot["name"], width=22, anchor="w", bg=bg_color, fg="#ffffff").pack(
                side="left", padx=(6, 8)
            )
            tk.Label(row, textvariable=slot["equip"], width=12, anchor="w", bg=bg_color, fg="#cccccc").pack(side="left")
        return frame

    def _autofill_codename(self, _event=None) -> None:
        player_id = self._parse_int(self.player_id_var.get())
        if player_id is None:
            return
        existing = db_connect.fetch_player(player_id)
        if existing:
            self.codename_var.set(existing[1])

    def _apply_network(self) -> None:
        ip = self.target_ip_var.get().strip() or self.sender.ip
        port = self._parse_int(self.target_port_var.get())
        if port is None:
            port = self.sender.port
        self.sender.update_target(ip, port)

    def _clear_form(self) -> None:
        self.player_id_var.set("")
        self.codename_var.set("")
        self.equipment_var.set("")
        self.player_entry.focus_set()

    def save_player(self) -> None:
        # Main workflow: validate inputs, persist to the database, update the roster, and notify hardware.
        player_id = self._parse_int(self.player_id_var.get())
        codename = self.codename_var.get().strip()
        generated_id = False
        existing = db_connect.fetch_player(player_id) if player_id is not None else None

        if player_id is None:
            if not codename:
                messagebox.showwarning(
                    "Validation",
                    "Enter a Player ID, or provide a codename so one can be generated.",
                )
                return
            if not messagebox.askyesno(
                "Generate Player ID",
                f"No ID entered for {codename}. Generate a new player ID?",
            ):
                return
            player_id = self._generate_new_player_id()
            generated_id = True
            existing = None
            self.player_id_var.set(str(player_id))
        elif existing and not codename:
            codename = existing[1]
            self.codename_var.set(codename)

        if not codename:
            messagebox.showwarning("Validation", "Codename is required.")
            return

        # Equipment ID is required both for the roster grouping and the hardware broadcast.
        equipment_id = self._parse_int(self.equipment_var.get())
        if equipment_id is None:
            messagebox.showwarning("Validation", "Equipment ID must be a whole number.")
            return

        # Prevent duplicate roster entries where the equipment assignment has not changed.
        current_slot = self._find_player_slot(player_id)
        if current_slot:
            team_name, index = current_slot
            current_equip = self._extract_equipment_value(self.team_slots[team_name][index]["equip"].get())
            if current_equip == equipment_id:
                messagebox.showinfo(
                    "Already Added",
                    f"Player {player_id} is already on the {team_name.upper()} team with equipment {current_equip}.",
                )
                self._clear_form()
                return

        # Sync database state so other stations have the latest codename mapping.
        db_connect.upsert_player(player_id, codename)

        # Display the player in the correct team column based on equipment parity.
        team = "red" if equipment_id % 2 else "green"
        self._place_player(team, player_id, codename, equipment_id)

        try:
            # Inform the arena hardware which piece of equipment is now active.
            self.sender.send(equipment_id)
        except OSError as exc:
            messagebox.showwarning("UDP", f"Equipment ID broadcast failed: {exc}")
        else:
            # Provide a confirmation dialog the first time a player is added so instructors can double-check.
            if existing is None:
                lines = [
                    "New player saved.",
                    f"ID: {player_id}",
                    f"Codename: {codename}",
                    f"Equipment ID: {equipment_id}",
                    f"Team: {team.title()}",
                ]
                if generated_id:
                    lines.append("ID was auto-generated.")
                messagebox.showinfo("Player Added", "\n".join(lines))

        self._clear_form()

    def _place_player(self, team: str, player_id: int, codename: str, equipment_id: int) -> None:
        # Remove stale entries before reassigning the player to a new slot.
        previous_location = self._find_player_slot(player_id)
        if previous_location is not None:
            prev_team, prev_index = previous_location
            self.team_slots[prev_team][prev_index]["name"].set("")
            self.team_slots[prev_team][prev_index]["equip"].set("—")

        # Fill the first empty slot to keep the roster tightly packed.
        slot_list = self.team_slots[team]
        for slot in slot_list:
            if not slot["name"].get():
                slot["name"].set(f"{codename} (#{player_id})")
                slot["equip"].set(f"HW {equipment_id}")
                break

    def _generate_new_player_id(self) -> int:
        for _ in range(1000):
            candidate = random.randint(1, 9999)
            if db_connect.fetch_player(candidate) is None:
                return candidate
        raise RuntimeError("Unable to allocate a new player ID")

    def _find_player_slot(self, player_id: int) -> Optional[Tuple[str, int]]:
        for team_name, slots in self.team_slots.items():
            for index, slot in enumerate(slots):
                if slot["name"].get().endswith(f"(#{player_id})"):
                    return team_name, index
        return None

    def _extract_equipment_value(self, label_text: str) -> Optional[int]:
        label_text = label_text.strip()
        if not label_text or label_text == "—":
            return None
        if label_text.startswith("HW"):
            label_text = label_text[2:].strip()
        return self._parse_int(label_text)

    def _parse_int(self, value: str) -> Optional[int]:
        value = value.strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def close_app(self) -> None:
        self.sender.close()
        self.master.destroy()


__all__ = ["PlayerEntry"]