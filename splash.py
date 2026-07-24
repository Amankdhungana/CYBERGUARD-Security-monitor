import customtkinter as ctk
from tkinter import Canvas
import threading
import time
import random
import importlib.util
import os
from datetime import datetime

ctk.set_appearance_mode("dark") # Set the appearance mode of the application to dark mode
ctk.set_default_color_theme("dark-blue") # Set the default color theme of the application to dark blue

MATRIX_CHARS = "011オ110カ0ク011ケコ001サシ0110タ0ツ1テ0トhe100ヌネ0101$%&" # Characters used for the matrix rain effect, including binary digits, Japanese katakana characters, and special symbols
BG = "#050810"
PANEL = "#0b0f1a"
GREEN = "#00ff88"
CYAN = "#00d4ff"
YELLOW = "#ffd93d"
RED = "#ff4757"
MUTED = "#4a5568"

class SplashScreen: # Splash screen class for the CyberGuard Security Monitor, responsible for displaying an animated matrix rain effect and system metrics while the main application is loading
    def __init__(self):
        self.root = ctk.CTk()
        self.root.overrideredirect(True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.configure(fg_color=BG)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.running = True
        self.loading_complete = False
        self.dot_index = 0
        self.cpu_history = [0] * 60
        self.mem_history = [0] * 60
        self.net_history = [0] * 60
        self.drops = []
        self.font_size = 14
        self.step_index = 0

        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self): # Set up the user interface of the splash screen, including the matrix rain effect, system metrics, and loading progress bar
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=BG)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.matrix_canvas = Canvas(self.main_frame, bg=BG, highlightthickness=0)
        self.matrix_canvas.grid(row=0, column=0, rowspan=5, sticky="nsew")

        self._init_matrix_drops()

        top_bar = ctk.CTkFrame(self.main_frame, height=60, corner_radius=0, fg_color="#07090f")
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)

        left_top = ctk.CTkFrame(top_bar, fg_color="transparent")
        left_top.pack(side="left", padx=25, pady=10)

        ctk.CTkLabel(left_top, text="⬡", font=("Courier", 22, "bold"), text_color=GREEN).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(left_top, text="CYBERGUARD", font=("Courier", 18, "bold"), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(left_top, text=" MONITOR v2.0", font=("Courier", 12), text_color=MUTED).pack(side="left")

        right_top = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_top.pack(side="right", padx=25, pady=10)

        self.status_label = ctk.CTkLabel(right_top, text="● INITIALIZING", font=("Courier", 13, "bold"), text_color=YELLOW)
        self.status_label.pack(side="left", padx=(0, 20))

        self.time_label = ctk.CTkLabel(right_top, text="", font=("Courier", 13), text_color=MUTED)
        self.time_label.pack(side="left")

        center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(40, 0))
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)
        center_frame.grid_columnconfigure(2, weight=1)

        self.cpu_card = self._make_stat_card(center_frame, "CPU", "0%", GREEN, 0)
        self.mem_card = self._make_stat_card(center_frame, "MEMORY", "0%", CYAN, 1)
        self.disk_card = self._make_stat_card(center_frame, "DISK", "0%", YELLOW, 2)

        graphs_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        graphs_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=20)
        graphs_frame.grid_columnconfigure(0, weight=1)
        graphs_frame.grid_columnconfigure(1, weight=1)
        graphs_frame.grid_columnconfigure(2, weight=1)
        graphs_frame.grid_rowconfigure(0, weight=1)

        self.cpu_canvas = self._make_graph_panel(graphs_frame, "CPU ACTIVITY", GREEN, 0)
        self.mem_canvas = self._make_graph_panel(graphs_frame, "MEMORY USAGE", CYAN, 1)
        self.net_canvas = self._make_graph_panel(graphs_frame, "NETWORK I/O", "#a855f7", 2)

        bottom_bar = ctk.CTkFrame(self.main_frame, height=55, corner_radius=0, fg_color="#07090f")
        bottom_bar.grid(row=3, column=0, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(bottom_bar, width=400, height=6,
                                                progress_color=GREEN, fg_color="#1a1a2e",
                                                corner_radius=3)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=25, pady=18)

        self.loading_label = ctk.CTkLabel(bottom_bar, text="Initializing Security Modules...",
                                           font=("Courier", 11), text_color=GREEN)
        self.loading_label.pack(side="left", padx=10)

        self.dot_label = ctk.CTkLabel(bottom_bar, text="", font=("Courier", 14, "bold"), text_color=GREEN)
        self.dot_label.pack(side="left")

        ctk.CTkLabel(bottom_bar, text="CLASSIFIED  //  AUTHORIZED ACCESS ONLY",
                     font=("Courier", 10), text_color=MUTED).pack(side="right", padx=25)

        self._start_matrix_animation()
        self._run_init_sequence()
        self._animate_dots()
        self._update_time()

    def _make_stat_card(self, parent, title, value, color, col): # Create a card to display a specific system metric (CPU, Memory, Disk) with a title, value, and color-coded progress bar
        card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=10,
                            border_width=1, border_color="#1a2035")
        card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(inner, text=title, font=("Courier", 10), text_color=MUTED).pack(anchor="w")

        val_label = ctk.CTkLabel(inner, text=value, font=("Courier", 36, "bold"), text_color=color)
        val_label.pack(anchor="w", pady=(4, 0))

        bar = ctk.CTkProgressBar(card, height=3, progress_color=color,
                                  fg_color="#1a1a2e", corner_radius=2)
        bar.set(0.3)
        bar.pack(fill="x", padx=20, pady=(0, 15))

        return {"val": val_label, "bar": bar}

    def _make_graph_panel(self, parent, title, color, col): # Create a panel to display a line graph for a specific system metric (CPU, Memory, Network) with a title and color-coded line
        frame = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=10,
                             border_width=1, border_color="#1a2035")
        frame.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")

        ctk.CTkLabel(frame, text=title, font=("Courier", 11, "bold"),
                     text_color=color).pack(anchor="w", padx=15, pady=(12, 4))

        canvas = Canvas(frame, bg=PANEL, highlightthickness=0, height=140)
        canvas.pack(fill="x", padx=10, pady=(0, 10))

        return canvas

    def _init_matrix_drops(self): # Initialize the matrix rain effect by creating a list of drops, each with random properties such as position, speed, length, and characters to display
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        cols = int(sw / self.font_size)
        for x in range(cols):
            self.drops.append({
                "x": x * self.font_size,
                "y": random.randint(-sh, 0),
                "speed": random.uniform(1.5, 4.0),
                "length": random.randint(8, 20),
                "chars": [random.choice(MATRIX_CHARS) for _ in range(25)],
            })

    def _start_matrix_animation(self): # Start the animation loop for the matrix rain effect
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        def animate():
            if not self.running:
                return
            self.matrix_canvas.delete("matrix")
            for d in self.drops:
                for i in range(d["length"]):
                    yp = d["y"] - i * self.font_size
                    if 0 < yp < sh:
                        if i == 0:
                            col = GREEN
                        elif i < 3:
                            col = "#00cc66"
                        else:
                            alpha = max(20, 180 - i * 12)
                            col = f"#{alpha:02x}{min(255, 180-i*6):02x}{alpha//3:02x}"
                        self.matrix_canvas.create_text(
                            d["x"], yp,
                            text=d["chars"][i % len(d["chars"])],
                            fill=col, font=("Courier", self.font_size),
                            tags="matrix"
                        )
                d["y"] += d["speed"]
                if d["y"] > sh + 20:
                    d["y"] = random.randint(-200, -20)
                    d["chars"] = [random.choice(MATRIX_CHARS) for _ in range(25)]
                    d["speed"] = random.uniform(1.5, 4.0)
            self.root.after(30, animate)

        animate()

    def _animate_dots(self):
        if not self.running:
            return
        frames = ["", ".", "..", "..."]
        self.dot_index = (self.dot_index + 1) % len(frames)
        self.dot_label.configure(text=frames[self.dot_index])
        self.root.after(350, self._animate_dots)

    def _update_time(self): # Update the time label on the splash screen every second to display the current date and time
        if not self.running:
            return
        self.time_label.configure(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._update_time)

    def _draw_graph(self, canvas, data, color, max_val=100):
        canvas.delete("all")
        w = canvas.winfo_width() or 300
        h = 140
        pad = 10

        for i in range(5):
            gy = pad + (h - 2 * pad) * i / 4
            canvas.create_line(pad, gy, w - pad, gy, fill="#0d1117", dash=(3, 5))

        if len(data) < 2:
            return

        pts = []
        for i, v in enumerate(data):
            x = pad + (w - 2 * pad) * i / (len(data) - 1)
            y = h - pad - (h - 2 * pad) * (v / max(max_val, 1))
            pts.extend([x, y])

        if len(pts) >= 4:
            canvas.create_line(pts, fill=color, width=2, smooth=True)
            last_x, last_y = pts[-2], pts[-1]
            canvas.create_oval(last_x - 4, last_y - 4, last_x + 4, last_y + 4,
                               fill=color, outline="")

    def _update_metrics(self): # Update the system metrics (CPU, Memory, Disk, Network) 
        if not self.running:
            return

        cpu = random.uniform(8, 45)
        mem = random.uniform(35, 65)
        disk = random.uniform(40, 75)
        net = random.uniform(10, 90)

        self.cpu_history.append(cpu)
        self.cpu_history.pop(0)
        self.mem_history.append(mem)
        self.mem_history.pop(0)
        self.net_history.append(net)
        self.net_history.pop(0)

        self.cpu_card["val"].configure(text=f"{cpu:.0f}%")
        self.cpu_card["bar"].set(cpu / 100)
        self.mem_card["val"].configure(text=f"{mem:.0f}%")
        self.mem_card["bar"].set(mem / 100)
        self.disk_card["val"].configure(text=f"{disk:.0f}%")
        self.disk_card["bar"].set(disk / 100)

        self._draw_graph(self.cpu_canvas, self.cpu_history, GREEN)
        self._draw_graph(self.mem_canvas, self.mem_history, CYAN)
        self._draw_graph(self.net_canvas, self.net_history, "#a855f7")

    def _monitor_loop(self):
        while self.running and not self.loading_complete:
            try:
                self.root.after(0, self._update_metrics)
                time.sleep(1)
            except Exception:
                break

    def start_monitoring(self):
        t = threading.Thread(target=self._monitor_loop, daemon=True)
        t.start()

    def _run_init_sequence(self):
        steps = [
            ("Scanning Security Modules", 0.12),
            ("Loading Threat Intelligence", 0.25),
            ("Analyzing Attack Vectors", 0.38),
            ("Initializing Monitoring Engine", 0.50),
            ("Connecting to Security Feeds", 0.62),
            ("Loading System Logs", 0.72),
            ("Tracking Active Sessions", 0.84),
            ("Calibrating Detection Rules", 0.93),
            ("System Ready", 1.0),
        ]
        delay = 1600

        def update(idx=0):
            if not self.running:
                return
            if idx < len(steps):
                text, progress = steps[idx]
                self.loading_label.configure(text=text + "...")
                self.progress_bar.set(progress)
                self.root.after(delay, lambda: update(idx + 1))
            else:
                self.loading_complete = True
                self.status_label.configure(text="● ONLINE", text_color=GREEN)
                self.loading_label.configure(text="All systems operational")
                self.root.after(800, self.launch_app)

        update()

    def launch_app(self): # Launch the main application by destroying the splash screen and importing the main module
        self.running = False
        self.root.destroy()

        spec = importlib.util.spec_from_file_location(
            "main",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        )
        main_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_mod)
        app = main_mod.CyberGuardMonitor()
        app.run()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    splash = SplashScreen()
    splash.run()
    