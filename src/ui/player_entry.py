import tkinter as tk
from tkinter import messagebox
import psycopg2
import socket
import os
from pathlib import Path

try:
    # Optional .env support if python-dotenv installed
    from dotenv import load_dotenv  # type: ignore
    if Path('.env').exists():
        load_dotenv()
except Exception:
    pass  # Silent if dotenv not available

# Pull DB settings from environment (aligns with db_connect.py defaults)
DB_NAME = os.getenv('PHOTON_DB_NAME', 'photon')
DB_USER = os.getenv('PHOTON_DB_USER', 'student')
DB_PASSWORD = os.getenv('PHOTON_DB_PASSWORD', '')
DB_HOST = os.getenv('PHOTON_DB_HOST', 'localhost')
DB_PORT = os.getenv('PHOTON_DB_PORT', '5432')

UDP_IP = "127.0.0.1"
UDP_PORT = 7500

def udp_broadcast(equipment_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(str(equipment_id).encode(), (UDP_IP, UDP_PORT))

def get_codename_from_db(player_id):
    """Return existing codename or None. Gracefully handle DB errors."""
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        cur.execute("SELECT codename FROM players WHERE id=%s", (player_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:  # Broad catch to keep UI alive if DB not ready
        print(f"[WARN] DB lookup failed: {e}")
        return None

def insert_new_player(player_id, codename):
    """Insert a new player. Return True on success, False otherwise."""
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        cur.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (player_id, codename))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Insert failed: {e}")
        return False

class PlayerEntry(tk.Frame):
    TEAM_SIZE = 20

    def __init__(self, master):
        super().__init__(master, bg="#050505")
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.red_rows = []  # list of (var_selected, codename_entry)
        self.green_rows = []
        self._build_layout()

    # ---------------- Layout -----------------
    def _build_layout(self):
        header = tk.Label(
            self,
            text="Edit Current Game",
            font=("Segoe UI", 18, "bold"),
            fg="#ffffff",
            bg="#000000",
            pady=6,
        )
        header.pack(fill="x")

        middle = tk.Frame(self, bg="#050505")
        middle.pack(expand=True, fill="both", padx=12, pady=8)

        red_frame = self._create_team_frame(middle, "RED TEAM", "#280808", "#6b1f1f", self.red_rows)
        green_frame = self._create_team_frame(middle, "GREEN TEAM", "#082808", "#1f6b1f", self.green_rows)
        red_frame.pack(side="left", expand=True, fill="both", padx=(0, 20))
        green_frame.pack(side="left", expand=True, fill="both")

        buttons = tk.Frame(self, bg="#111111")
        buttons.pack(fill="x", pady=(4, 0))

        commit_btn = tk.Button(buttons, text="Save Selected", command=self.commit_selected, width=14)
        broadcast_btn = tk.Button(buttons, text="Broadcast Selected", command=self.broadcast_selected, width=18)
        clear_btn = tk.Button(buttons, text="Clear All", command=self.clear_all, width=12)
        refresh_btn = tk.Button(buttons, text="Load From DB", command=self.refresh_from_db, width=14)
        commit_btn.pack(side="left", padx=6, pady=6)
        broadcast_btn.pack(side="left", padx=6, pady=6)
        clear_btn.pack(side="left", padx=6, pady=6)
        refresh_btn.pack(side="left", padx=6, pady=6)

        hint = tk.Label(
            self,
            text="Fill codename(s) then check the box(es). 'Save Selected' inserts new players. 'Broadcast Selected' sends equipment IDs (row #).",
            font=("Segoe UI", 9),
            fg="#bbbbbb",
            bg="#050505",
            anchor="w",
            wraplength=880,
            justify="left",
        )
        hint.pack(fill="x", padx=8, pady=(2, 2))

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            font=("Segoe UI", 10),
            bg="#202020",
            fg="#cccccc",
            padx=8,
        )
        status.pack(fill="x", pady=(4, 0))

    def _create_team_frame(self, parent, title, bg_color, border_color, collector_list):
        outer = tk.Frame(parent, bg=bg_color, bd=2, relief="groove", highlightbackground=border_color, highlightcolor=border_color)
        title_label = tk.Label(outer, text=title, font=("Segoe UI", 12, "bold"), fg="#dddddd", bg=bg_color)
        title_label.pack(pady=(4, 6))

        rows_container = tk.Frame(outer, bg=bg_color)
        rows_container.pack(expand=True, fill="both", padx=6, pady=(0, 6))

        for i in range(self.TEAM_SIZE):
            row_frame = tk.Frame(rows_container, bg=bg_color)
            row_frame.pack(fill="x", pady=1)
            sel_var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(row_frame, variable=sel_var, bg=bg_color, activebackground=bg_color, highlightthickness=0)
            chk.pack(side="left")
            id_label = tk.Label(row_frame, text=f"{i:>2}", width=3, anchor="e", bg=bg_color, fg="#bbbbbb")
            id_label.pack(side="left", padx=(0, 4))
            code_entry = tk.Entry(row_frame, width=18)
            code_entry.pack(side="left", fill="x", expand=True)
            collector_list.append((i, sel_var, code_entry))
        return outer

    # --------------- Actions -----------------
    def _iter_selected_rows(self):
        for team_rows in (self.red_rows, self.green_rows):
            for player_id, sel_var, entry in team_rows:
                if sel_var.get():
                    yield player_id, entry

    def commit_selected(self):
        added = 0
        skipped_existing = 0
        for player_id, entry in self._iter_selected_rows():
            codename = entry.get().strip()
            if not codename:
                continue
            existing = get_codename_from_db(player_id)
            if not existing:
                if insert_new_player(player_id, codename):
                    added += 1
            else:
                skipped_existing += 1
        self.status_var.set(f"Save done: {added} inserted, {skipped_existing} already existed")
        messagebox.showinfo("Save Complete", f"Inserted {added}. Existing skipped: {skipped_existing}.")

    def broadcast_selected(self):
        broadcasted = 0
        failures = 0
        for player_id, entry in self._iter_selected_rows():
            codename = entry.get().strip()
            if not codename:
                continue  # require a codename before broadcast
            try:
                udp_broadcast(player_id)
                broadcasted += 1
            except Exception as e:
                print(f"[WARN] Broadcast failed for {player_id}: {e}")
                failures += 1
        self.status_var.set(f"Broadcast: {broadcasted} ok, {failures} failed")
        if failures:
            messagebox.showwarning("Broadcast", f"Broadcasted {broadcasted}, {failures} failed (see console).")
        else:
            messagebox.showinfo("Broadcast", f"Broadcasted {broadcasted} equipment IDs.")

    def clear_all(self):
        for team_rows in (self.red_rows, self.green_rows):
            for _pid, _sel, entry in team_rows:
                entry.delete(0, tk.END)
        self.status_var.set("Cleared all entries (UI only)")

    def refresh_from_db(self):
        filled = 0
        for team_rows in (self.red_rows, self.green_rows):
            for player_id, _sel, entry in team_rows:
                codename = get_codename_from_db(player_id)
                if codename:
                    entry.delete(0, tk.END)
                    entry.insert(0, codename)
                    filled += 1
        self.status_var.set(f"Loaded {filled} existing players from DB")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Laser Tag Player Entry")
    app = PlayerEntry(master=root)
    app.mainloop()
