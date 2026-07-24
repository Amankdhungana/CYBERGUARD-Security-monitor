import customtkinter as ctk
from ui.dashboard import DashboardPage
from ui.attacks import AttacksPage
from ui.logs import LogsPage
from ui.alerts import AlertsPage
from ui.incident import IncidentPage
import threading
import time
import tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CyberGuardMonitor: # Main application class for the CyberGuard Security Monitor, responsible for initializing the UI, managing pages, and handling auto-refresh of data
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CyberGuard Security Monitor")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 700)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.current_page = "dashboard"
        self.pages = {}
        self.page_objects = {}
        self.nav_buttons = {}
        self.matrix = None
        
        self.setup_ui()
        self.start_auto_refresh()
        
    def setup_ui(self):
        self.setup_sidebar()
        self.setup_main_content()
        
    def setup_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color="#0a0e1a")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        ctk.CTkLabel(sidebar, text="CYBERGUARD", font=("Orbitron", 18, "bold"), text_color="#00d4ff").pack(pady=(25, 5))
        ctk.CTkLabel(sidebar, text="Security Monitor", font=("Inter", 11), text_color="#8892b0").pack(pady=(0, 30))
        
        nav_items = [ # Define the navigation items for the sidebar with their respective page identifiers
            ("DASHBOARD", "dashboard"),
            ("ATTACKS", "attacks"),
            ("LOGS", "logs"),
            ("ALERTS", "alerts"),
            ("INCIDENT", "incident")
        ]
        
        for text, page in nav_items:
            btn = ctk.CTkButton(sidebar, text=text, font=("Inter", 13), fg_color="transparent", text_color="#8892b0",
                               hover_color="#1a2540", anchor="w", height=45, corner_radius=8,
                               command=lambda p=page: self.switch_page(p))
            btn.pack(fill="x", padx=15, pady=3)
            self.nav_buttons[page] = btn
        
        ctk.CTkLabel(sidebar, text="● LIVE", font=("Inter", 10, "bold"), text_color="#00d4aa").pack(side="bottom", pady=30)
        
    def setup_main_content(self): # Set up the main content area of the application, including the matrix rain effect and the content frame for different pages
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        matrix_frame = ctk.CTkFrame(container, fg_color="transparent")
        matrix_frame.grid(row=0, column=0, sticky="nsew")
        
        self.matrix_canvas = tk.Canvas(matrix_frame, bg="#0a0e1a", highlightthickness=0)
        self.matrix_canvas.pack(fill="both", expand=True)
        
        
        self.content_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.configure(fg_color="transparent")
        
        dashboard_obj = DashboardPage(self.content_frame)
        attacks_obj = AttacksPage(self.content_frame)
        logs_obj = LogsPage(self.content_frame)
        alerts_obj = AlertsPage(self.content_frame, self.refresh_all_pages)
        incident_obj = IncidentPage(self.content_frame)
        
        self.page_objects["dashboard"] = dashboard_obj
        self.page_objects["attacks"] = attacks_obj
        self.page_objects["logs"] = logs_obj
        self.page_objects["alerts"] = alerts_obj
        self.page_objects["incident"] = incident_obj
        
        self.pages["dashboard"] = dashboard_obj.get_frame()
        self.pages["attacks"] = attacks_obj.get_frame()
        self.pages["logs"] = logs_obj.get_frame()
        self.pages["alerts"] = alerts_obj.get_frame()
        self.pages["incident"] = incident_obj.get_frame()
        
        for page in self.pages.values():
            page.grid_remove()
        
        self.pages["dashboard"].grid(row=0, column=0, sticky="nsew")
        self.highlight_nav("dashboard")
        
    def refresh_all_pages(self): # Refresh the data on all pages by calling their respective load_data methods, handling any exceptions that may occur during the refresh process
        try:
            self.page_objects["dashboard"].load_data()
            self.page_objects["attacks"].load_data()
            self.page_objects["alerts"].load_data()
        except Exception as e:
            print(f"Refresh error: {e}")
        
    def highlight_nav(self, page):
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color="#1a2540" if key == page else "transparent", 
                         text_color="#00d4ff" if key == page else "#8892b0")
        
    def switch_page(self, page):
        self.current_page = page
        for p, frame in self.pages.items():
            frame.grid_remove()
        self.pages[page].grid(row=0, column=0, sticky="nsew")
        self.highlight_nav(page)
        
        if page == "dashboard":
            self.page_objects["dashboard"].load_data()
        elif page == "attacks":
            self.page_objects["attacks"].load_data()
        elif page == "logs":
            self.page_objects["logs"].load_data()
        elif page == "alerts":
            self.page_objects["alerts"].load_data()
        
    def start_auto_refresh(self): # Start a background thread that automatically refreshes the data on the current page every 30 seconds
        def refresh():
            while True:
                time.sleep(30)
                if self.current_page == "dashboard":
                    self.root.after(0, lambda: self.page_objects["dashboard"].load_data())
                elif self.current_page == "attacks":
                    self.root.after(0, lambda: self.page_objects["attacks"].load_data())
                elif self.current_page == "logs":
                    self.root.after(0, lambda: self.page_objects["logs"].load_data())
                elif self.current_page == "alerts":
                    self.root.after(0, lambda: self.page_objects["alerts"].load_data())
        
        thread = threading.Thread(target=refresh, daemon=True) # Start a daemon thread to run the refresh function in the background, allowing the application to exit cleanly without waiting for the thread to finish
        thread.start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CyberGuardMonitor()
    app.run()
    