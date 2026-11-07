import os, time, tkinter as tk
from tkinter import messagebox as mb, simpledialog as sd, ttk

class Room:
    def __init__(self, num, price, cap, avail="True", name="None", phone="", email="", nights=1, b_time="N/A", r_type="Standard"):
        self.num, self.type = str(num).strip(), r_type
        
        try: self.price = float(price)
        except: self.price = 0.0
        
        try: self.cap = int(float(cap)) # Bulletproof capacity fallback
        except: self.cap = 1
        
        self.available, self.guest_name, self.guest_phone, self.guest_email = str(avail).lower() == "true", name, phone, email
        
        try: self.nights = int(float(nights))
        except: self.nights = 1
        
        self.booking_time = b_time

class HotelManagementGUI:
    def __init__(self, root):
        # Force files to save exactly where this python script is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, "data.txt")
        self.staff_file = os.path.join(base_dir, "staff.txt")
        self.root, self.rooms, self.staff_accounts = root, [], {}
        self.start_time = time.time()
        self.root.title("Hotel Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg="#0B1926")
        self.root.withdraw()
        self.setup_and_load_data()
        self.show_login_screen()
    def setup_and_load_data(self):
        try:
            for line in open(self.staff_file):
                if len(p := line.strip().split("|")) == 3: self.staff_accounts[p[0].lower()] = {"pass": p[1], "role": p[2].lower()}
        except: pass
        self.staff_accounts.update({"admin": {"pass": "admin123", "role": "admin"}})
        self.staff_accounts.setdefault("staff1", {"pass": "1234", "role": "staff"})
        self.save_staff_data()
        
        try:
            for line in open(self.filename):
                p = (line.strip().split("|") + ["", "", "1", "N/A"])[:10]
                if p[0]: self.rooms.append(Room(p[0], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], r_type=p[1]))
        except: pass

    def save_staff_data(self):
        try: open(self.staff_file, "w").writelines(f"{u}|{acc['pass']}|{acc['role']}\n" for u, acc in self.staff_accounts.items())
        except Exception as e: mb.showerror("Error", f"Save staff failed: {e}")

    def save_data(self):
        try: open(self.filename, "w").writelines(f"{r.num}|{r.type}|{r.price}|{r.cap}|{r.available}|{r.guest_name}|{r.guest_phone}|{r.guest_email}|{r.nights}|{r.booking_time}\n" for r in self.rooms)
        except Exception as e: mb.showerror("Error", f"Save room failed: {e}")

    def show_login_screen(self):
        self.login_win = w = tk.Toplevel(self.root)
        w.title("Hotel System Login"); w.geometry("420x450"); w.configure(bg="#102A3C"); w.grab_set(); w.protocol("WM_DELETE_WINDOW", self.root.destroy)
        tk.Label(w, text="🏨 HOTEL DASHBOARD", font=("Segoe UI", 14, "bold"), bg="#102A3C", fg="#00F0FF").pack(pady=(20, 2))
        tk.Label(w, text="Enter credentials to access system", font=("Segoe UI", 9), bg="#102A3C", fg="#7A9BB3").pack(pady=(0, 15))
        f = tk.Frame(w, bg="#102A3C"); f.pack(fill=tk.BOTH, expand=True, padx=40)

        def make_entry(lbl_txt, is_pwd=False):
            tk.Label(f, text=lbl_txt, font=("Segoe UI", 9, "bold"), bg="#102A3C", fg="#B0BEC5", anchor="w").pack(fill=tk.X, pady=(5, 2))
            e = tk.Entry(f, font=("Segoe UI", 10), show="*" if is_pwd else "", bg="#1A3D54", fg="#FFFFFF", bd=0, insertbackground="#00F0FF")
            e.pack(fill=tk.X, ipady=5); return e

        u_entry, p_entry = make_entry("Username:"), make_entry("Password:", True)
        u_entry.insert(0, "admin"); p_entry.insert(0, "admin123")
        tk.Label(w, text="Admin: admin / admin123\nStaff: staff1 / 1234", font=("Segoe UI", 8, "bold"), bg="#102A3C", fg="#00FF88").pack(pady=5)

        def attempt_login(e=None):
            u, p = u_entry.get().strip().lower(), p_entry.get().strip()
            if u in self.staff_accounts and self.staff_accounts[u]["pass"] == p:
                self.current_user, self.user_role = u, self.staff_accounts[u]["role"]
                w.destroy(); self.root.deiconify(); self.build_gui(); self.update_timer(); self.refresh_list()
            else: mb.showerror("Login Failed", "Invalid Credentials!", parent=w)

        w.bind("<Return>", attempt_login)
        tk.Button(w, text="LOGIN", command=attempt_login, bg="#00F0FF", fg="#0B1926", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2").pack(fill=tk.X, padx=40, pady=(10, 15), ipady=6)

    def build_gui(self):
        t_bar = tk.Frame(self.root, bg="#102A3C", height=60)
        t_bar.pack(fill=tk.X); t_bar.pack_propagate(False)
        tk.Label(t_bar, text="🔷Hotel Management System", font=("Segoe UI", 12, "bold"), bg="#102A3C", fg="#00F0FF").pack(side=tk.LEFT, padx=20)

        s_frame = tk.Frame(t_bar, bg="#1A3D54", padx=8, pady=4); s_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(s_frame, text="🔍", bg="#1A3D54", fg="#00F0FF").pack(side=tk.LEFT, padx=(2, 5))
        self.search_var = tk.StringVar()
        s_ent = tk.Entry(s_frame, textvariable=self.search_var, font=("Segoe UI", 10), bg="#1A3D54", fg="#FFFFFF", bd=0, insertbackground="#00F0FF", width=32)
        s_ent.pack(side=tk.LEFT); s_ent.insert(0, "Search rooms, guests, phone...")
        s_ent.bind("<FocusIn>", lambda e: s_ent.delete(0, tk.END) if s_ent.get() == "Search rooms, guests, phone..." else None)
        s_ent.bind("<FocusOut>", lambda e: s_ent.insert(0, "Search rooms, guests, phone...") if not s_ent.get() else None)
        # 🟢 UPGRADED SEARCH: Now includes r.cap so you can search "4" to find all rooms with 4 capacity!
        s_ent.bind("<KeyRelease>", lambda e: self.refresh_list([r for r in self.rooms if any(self.search_var.get().strip().lower() in str(v).lower() for v in (r.num, r.guest_name, r.guest_phone, r.guest_email, r.type, r.cap))] if self.search_var.get().strip().lower() not in ("", "search rooms, guests, phone...") else None))

        u_frame = tk.Frame(t_bar, bg="#102A3C", cursor="hand2"); u_frame.pack(side=tk.RIGHT, padx=20)
        self.timer_label = tk.Label(u_frame, font=("Consolas", 9, "bold"), bg="#102A3C", fg="#00F0FF")
        self.timer_label.pack(side=tk.LEFT, padx=15)
        avatar = tk.Label(u_frame, text=self.current_user[:2].upper(), font=("Segoe UI", 9, "bold"), bg="#00F0FF" if self.user_role=="admin" else "#00FF88", fg="#0B1926", width=3)
        avatar.pack(side=tk.LEFT, padx=5)
        name_lbl = tk.Label(u_frame, text=f"{self.current_user} ({self.user_role.title()}) ▾", font=("Segoe UI", 9, "bold"), bg="#102A3C", fg="#E1F5FE")
        name_lbl.pack(side=tk.LEFT, padx=5)

        menu = tk.Menu(self.root, tearoff=0, bg="#1A3D54", fg="#FFFFFF")
        menu.add_command(label="🔄 Switch Account", command=self.relogin)
        menu.add_command(label="❌ Exit System", command=self.exit_app)
        for w in (u_frame, avatar, name_lbl): w.bind("<Button-1>", lambda e: menu.tk_popup(e.x_root, e.y_root))

        b_frame = tk.Frame(self.root, bg="#0B1926"); b_frame.pack(fill=tk.BOTH, expand=True)
        sb = tk.Frame(b_frame, bg="#102A3C", width=220); sb.pack(side=tk.LEFT, fill=tk.Y); sb.pack_propagate(False)

        def add_btn(txt, cmd=None, active=False, fg=None):
            tk.Button(sb, text=txt, font=("Segoe UI", 10), bg="#1F4863" if active else "#102A3C", fg=fg or ("#00F0FF" if active else "#B0BEC5"), bd=0, anchor="w", padx=15, pady=8, cursor="hand2", command=cmd).pack(fill=tk.X, pady=1)

        for sect, btns in [("MAIN DASHBOARD", [("📊 Overview", None, True)]), ("STAFF ACTIONS", [("📅 Make Booking", self.make_booking, False), ("🖨️ View / Print Receipt", self.prompt_view_receipt, False), ("🚪 Check-Out", self.check_out, False)])] + ([("ADMIN CONTROLS", [("➕ Add Room", self.add_room, False), ("✏️ Edit Room", self.edit_room, False), ("🗑️ Delete Room", self.delete_room, False, "#FF5252"), ("👥 Manage Staff", self.manage_staff, False, "#00FF88")])] if self.user_role == "admin" else []):
            tk.Label(sb, text=sect, font=("Segoe UI", 8, "bold"), bg="#102A3C", fg="#5C8CAE", anchor="w").pack(fill=tk.X, padx=15, pady=(15, 5))
            for b in btns: add_btn(*b)
        
        tk.Button(sb, text="💾 Save & Exit", command=self.exit_app, font=("Segoe UI", 10), bg="#1F4863", fg="#00F0FF", bd=0, anchor="w", padx=15, pady=8).pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=20)

        mc = tk.Frame(b_frame, bg="#0B1926"); mc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        tf = tk.Frame(mc, bg="#0B1926"); tf.pack(fill=tk.X, pady=(0, 15))
        tk.Label(tf, text="Rooms Overview", font=("Segoe UI", 18, "bold"), bg="#0B1926", fg="#FFFFFF").pack(side=tk.LEFT)
        tk.Label(tf, text=f"Active Session: {self.current_user} [{self.user_role.upper()}]", font=("Segoe UI", 9), bg="#0B1926", fg="#7A9BB3").pack(side=tk.LEFT, padx=15, pady=(5, 0))

        tc = tk.Frame(mc, bg="#153044", bd=1, relief=tk.FLAT); tc.pack(fill=tk.BOTH, expand=True)
        ttk.Style().theme_use("clam")
        ttk.Style().configure("Treeview", background="#153044", foreground="#FFFFFF", fieldbackground="#153044", font=("Segoe UI", 10), rowheight=34, borderwidth=0)
        ttk.Style().configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#1F4863", foreground="#00F0FF", borderwidth=0)
        ttk.Style().map("Treeview", background=[("selected", "#00F0FF")], foreground=[("selected", "#0B1926")])

        cols = ("Room", "Type", "Capacity", "Price", "Status", "Guest", "Phone", "Email")
        self.tree = ttk.Treeview(tc, columns=cols, show="headings", selectmode="browse")
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=130 if c in ("Email", "Guest") else 95, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        sc = ttk.Scrollbar(tc, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=sc.set); sc.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def relogin(self):
        for w in self.root.winfo_children(): w.destroy()
        self.root.withdraw(); self.show_login_screen()

    def update_timer(self):
        m, s = divmod(int(time.time() - self.start_time), 60)
        self.timer_label.config(text=f"🕒 {time.strftime('%I:%M:%S %p')}  |  {m:02d}m {s:02d}s")
        self.root.after(1000, self.update_timer)

    def refresh_list(self, filter_rooms=None):
        self.tree.delete(*self.tree.get_children())
        for r in (filter_rooms if filter_rooms is not None else self.rooms):
            self.tree.insert("", tk.END, values=(r.num, r.type, r.cap, f"${r.price:.2f}", "🟢 Available" if r.available else "🔴 Occupied", r.guest_name if r.guest_name != "None" else "-", r.guest_phone, r.guest_email))

    def _get_target_room(self, title, msg, occ_only=False):
        sel = self.tree.selection()
        if not (num := str(self.tree.item(sel[0], "values")[0]).strip() if sel else sd.askstring(title, msg, parent=self.root)): return None
        for r in self.rooms:
            if r.num == num.strip():
                if occ_only and r.available:
                    mb.showwarning("Warning", f"Room {num} is vacant.", parent=self.root)
                    return None
                return r
        mb.showerror("Error", f"Room '{num}' not found.", parent=self.root)
        return None

    def add_room(self):
        kw = {"parent": self.root}
        num = sd.askstring("Add Room", "Room Number:", **kw)
        if not num or any(r.num == num.strip() for r in self.rooms): 
            return mb.showerror("Error", "Invalid or exists!", **kw)
            
        p = sd.askfloat("Add Room", "Price ($):", **kw)
        if p is None: return
        
        c = sd.askinteger("Add Room", "Capacity:", **kw)
        if c is None: return
        
        rtype = sd.askstring("Add Room", "Type (Standard/Suite):", **kw)
        
        self.rooms.append(Room(num, p, c, r_type=(rtype or "Standard").title()))
        self.save_data()
        self.refresh_list()
        mb.showinfo("Success", f"Room {num} added.", **kw)

    def edit_room(self):
        kw = {"parent": self.root}
        if r := self._get_target_room("Edit Room", "Room Number:"):
            p = sd.askfloat("Edit", f"New Price (Current: ${r.price}):", **kw)
            if p is not None: r.price = p
            
            c = sd.askinteger("Edit", f"New Capacity (Current: {r.cap}):", **kw)
            if c is not None: r.cap = c
            
            self.save_data()
            self.refresh_list()
            mb.showinfo("Success", "Room updated.", **kw)

    def delete_room(self):
        kw = {"parent": self.root}
        if (r := self._get_target_room("Delete Room", "Room Number:")) and (r.available or not mb.showwarning("Warning", "Cannot delete occupied!", **kw)) and mb.askyesno("Confirm", f"Delete Room {r.num}?", **kw):
            self.rooms.remove(r); self.save_data(); self.refresh_list(); mb.showinfo("Deleted", "Room removed.", **kw)

    def manage_staff(self):
        kw = {"parent": self.root}
        if not (act := sd.askstring("Manage Staff", "Type 'add' or 'del':", **kw)): return
        if act.strip().lower() == "add":
            u, p = sd.askstring("Add Staff", "Username:", **kw), sd.askstring("Add Staff", "Password:", **kw)
            if not u or not p or u.lower() in self.staff_accounts: return mb.showerror("Error", "Invalid or existing username.", **kw)
            self.staff_accounts[u.lower()] = {"pass": p.strip(), "role": (sd.askstring("Add Staff", "Role (staff/admin):", **kw) or "staff").lower()}
            self.save_staff_data(); mb.showinfo("Success", f"Account '{u}' added.", **kw)
        elif act.strip().lower() == "del":
            u = sd.askstring("Delete Staff", "Username:", **kw)
            if not u or u.lower() not in self.staff_accounts or u.lower() == self.current_user: return mb.showerror("Error", "Invalid or active user.", **kw)
            del self.staff_accounts[u.lower()]; self.save_staff_data(); mb.showinfo("Deleted", f"Account '{u}' removed.", **kw)

    def _get_receipt_info(self, r):
        return [("Booking Time:", r.booking_time), ("Guest Name:", r.guest_name), ("Phone Number:", r.guest_phone or "N/A"), ("Email:", r.guest_email or "N/A"), ("Room Number:", r.num), ("Room Type:", r.type), ("Capacity:", f"{r.cap} Persons"), ("Price per Night:", f"${r.price:.2f}"), ("Nights:", f"{r.nights} Night(s)"), ("Total Amount:", f"${r.price * r.nights:.2f}")]

    def show_receipt(self, r):
        w = tk.Toplevel(self.root); w.title(f"Receipt - Room {r.num}"); w.geometry("400x530"); w.configure(bg="#102A3C"); w.grab_set()
        tk.Label(w, text="🏨 HOTEL MANAGEMENT SYSTEM", font=("Segoe UI", 12, "bold"), bg="#102A3C", fg="#00F0FF").pack(pady=(15, 2))
        ttk.Separator(w, orient="horizontal").pack(fill="x", padx=20, pady=5)
        df = tk.Frame(w, bg="#102A3C"); df.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        for lbl, val in self._get_receipt_info(r):
            rf = tk.Frame(df, bg="#102A3C"); rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=lbl, font=("Segoe UI", 9, "bold"), bg="#102A3C", fg="#B0BEC5", anchor="w", width=16).pack(side=tk.LEFT)
            tk.Label(rf, text=val, font=("Segoe UI", 9, "bold" if "Total" in lbl else "normal"), bg="#102A3C", fg="#00FF88" if "Total" in lbl else "#FFFFFF", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        bf = tk.Frame(w, bg="#102A3C"); bf.pack(fill=tk.X, pady=10)
        tk.Button(bf, text="🖨️ Print", command=lambda: self.print_receipt(r), bg="#00F0FF", fg="#0B1926", font=("Segoe UI", 9, "bold"), width=12, bd=0).pack(side=tk.LEFT, padx=15)
        tk.Button(bf, text="Close", command=w.destroy, bg="#1F4863", fg="white", font=("Segoe UI", 9, "bold"), width=12, bd=0).pack(side=tk.RIGHT, padx=15)

    def print_receipt(self, r):
        fn = f"Receipt_Room_{r.num}.txt"
        open(fn, "w").write("========================================\n      OFFICIAL BOOKING RECEIPT          \n========================================\n" + "\n".join(f"{lbl:18} {val}" for lbl, val in self._get_receipt_info(r)))
        mb.showinfo("Success", f"Receipt saved to '{fn}'", parent=self.root)

    def prompt_view_receipt(self):
        if r := self._get_target_room("Receipt", "Enter Occupied Room Number:", True): self.show_receipt(r)

    def make_booking(self):
        kw = {"parent": self.root}
        if not (r := self._get_target_room("Booking", "Enter Room Number to book:")): return
        if not r.available: return mb.showwarning("Unavailable", f"Room {r.num} is occupied.", **kw)
        
        gn = sd.askstring("Booking", "Guest Name:", **kw)
        if not gn: return
        
        gp = sd.askstring("Booking", "Phone Number (Digits only):", **kw)
        while gp and not gp.isdigit(): gp = sd.askstring("Booking", "Digits only! Phone Number:", **kw)
        if not gp: return
        
        ge = sd.askstring("Booking", "Guest Email Address:", **kw)
        while ge and ("@" not in ge or "." not in ge): ge = sd.askstring("Booking", "Must contain '@' and '.'! Email:", **kw)
        if not ge: return
        
        n = sd.askinteger("Booking", "Number of Nights:", minvalue=1, **kw)
        if not n: return
        
        r.guest_name, r.guest_phone, r.guest_email, r.nights, r.available, r.booking_time = gn.strip(), gp, ge, n, False, time.strftime("%Y-%m-%d %I:%M:%S %p")
        self.save_data()
        self.refresh_list()
        self.show_receipt(r)

    def check_out(self):
        kw = {"parent": self.root}
        if r := self._get_target_room("Check-Out", "Enter Room Number:"):
            if r.available: return mb.showinfo("Info", "Room is already empty.", **kw)
            gn = r.guest_name
            r.available, r.guest_name, r.guest_phone, r.guest_email, r.nights, r.booking_time = True, "None", "", "", 1, "N/A"
            self.save_data()
            self.refresh_list()
            mb.showinfo("Success", f"Guest {gn} checked out.", **kw)

    def exit_app(self):
        self.save_data()
        self.save_staff_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelManagementGUI(root)
    root.mainloop()