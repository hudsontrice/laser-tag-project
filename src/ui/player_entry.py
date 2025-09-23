import tkinter as tk
import psycopg2
import socket

DB_NAME = 'photon'
DB_USER = 'youruser'
DB_PASSWORD = 'yourpassword'
DB_HOST = 'localhost'

UDP_IP = "127.0.0.1"
UDP_PORT = 7500

def udp_broadcast(equipment_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(str(equipment_id).encode(), (UDP_IP, UDP_PORT))

def get_codename_from_db(player_id):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT codename FROM players WHERE id=%s", (player_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

def insert_new_player(player_id, codename):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (player_id, codename))
    conn.commit()
    cur.close()
    conn.close()

class PlayerEntry(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.lbl_id = tk.Label(self, text="Player ID:")
        self.lbl_id.grid(row=0, column=0)
        self.entry_id = tk.Entry(self)
        self.entry_id.grid(row=0, column=1)

        self.lbl_codename = tk.Label(self, text="Codename:")
        self.lbl_codename.grid(row=1, column=0)
        self.entry_codename = tk.Entry(self)
        self.entry_codename.grid(row=1, column=1)

        self.lbl_equipment = tk.Label(self, text="Equipment ID:")
        self.lbl_equipment.grid(row=2, column=0)
        self.entry_equipment = tk.Entry(self)
        self.entry_equipment.grid(row=2, column=1)

        self.btn_submit = tk.Button(self, text="Add Player", command=self.submit_player)
        self.btn_submit.grid(row=3, column=0, columnspan=2)

        self.btn_clear = tk.Button(self, text="Clear All", command=self.clear_entries)
        self.btn_clear.grid(row=4, column=0, columnspan=2)

    def submit_player(self):
        pid = int(self.entry_id.get())
        codename = self.entry_codename.get()
        equipment_id = int(self.entry_equipment.get())

        if not get_codename_from_db(pid):
            insert_new_player(pid, codename)

        udp_broadcast(equipment_id)
        self.clear_entries()

    def clear_entries(self):
        self.entry_id.delete(0, tk.END)
        self.entry_codename.delete(0, tk.END)
        self.entry_equipment.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Laser Tag Player Entry")
    app = PlayerEntry(master=root)
    app.mainloop()
