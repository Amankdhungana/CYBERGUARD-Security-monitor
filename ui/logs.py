import customtkinter as ctk
from utils.helpers import get_activity_logs, format_timestamp, get_severity_color

class LogsPage:    # does not inherit from ctk.CTkFrame, it manages its own frame
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.logs_container = None
        self.create_page()
        
    def create_page(self): # Create the logs page layout
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frame, text="ACTIVITY LOGS", font=("Orbitron", 24, "bold"), text_color="#00d4ff").grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.logs_container = ctk.CTkScrollableFrame(self.frame, fg_color="#141b2d", corner_radius=12)
        self.logs_container.grid(row=1, column=0, sticky="nsew")
        
        self.load_data()
        
    def load_data(self):
        for widget in self.logs_container.winfo_children():
            widget.destroy()
        
        logs = get_activity_logs(30)  # Fetch the last 30 logs
        
        if logs:
            header_frame = ctk.CTkFrame(self.logs_container, fg_color="#1a2540", corner_radius=8)
            header_frame.pack(fill="x", pady=(0, 5))
            
            headers = ["Time", "User", "Action", "Type", "IP", "Status"] # Define headers for the logs table
            for i, h in enumerate(headers):
                ctk.CTkLabel(header_frame, text=h, font=("Inter", 12, "bold"), text_color="#8892b0").grid(row=0, column=i, padx=10, pady=8, sticky="w")
                header_frame.grid_columnconfigure(i, weight=1 if i < 3 else 0)
            
            for log in logs[:30]: # Display only the last 30 logs
                row_frame = ctk.CTkFrame(self.logs_container, fg_color="#0a0e1a", corner_radius=6)
                row_frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row_frame, text=format_timestamp(log['timestamp']), font=("Inter", 11), text_color="#8892b0").grid(row=0, column=0, padx=10, pady=6, sticky="w")
                ctk.CTkLabel(row_frame, text=log['user'], font=("Inter", 11, "bold"), text_color="#00d4ff").grid(row=0, column=1, padx=10, pady=6, sticky="w")
                ctk.CTkLabel(row_frame, text=log['action'].replace('_', ' ').title(), font=("Inter", 11), text_color="#ffffff").grid(row=0, column=2, padx=10, pady=6, sticky="w")
                ctk.CTkLabel(row_frame, text=log['event_type'], font=("Inter", 10), text_color="#8892b0").grid(row=0, column=3, padx=10, pady=6, sticky="w")
                ctk.CTkLabel(row_frame, text=log['ip_address'], font=("Orbitron", 10), text_color="#8892b0").grid(row=0, column=4, padx=10, pady=6, sticky="w")
                
                status_color = "#00d4aa" if log['status'] == 'success' else "#ff4757"
                ctk.CTkLabel(row_frame, text=log['status'].upper(), font=("Inter", 10, "bold"), text_color=status_color).grid(row=0, column=5, padx=10, pady=6, sticky="w")
                
                row_frame.grid_columnconfigure(0, weight=1)
                row_frame.grid_columnconfigure(1, weight=1)
                row_frame.grid_columnconfigure(2, weight=2)
                row_frame.grid_columnconfigure(3, weight=1)
                row_frame.grid_columnconfigure(4, weight=1)
                row_frame.grid_columnconfigure(5, weight=0)
        else:
            ctk.CTkLabel(self.logs_container, text="No logs found", text_color="#8892b0", font=("Inter", 14)).pack(pady=40)
        
    def get_frame(self):
        return self.frame
    