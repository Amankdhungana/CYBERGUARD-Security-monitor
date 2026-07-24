import customtkinter as ctk
from utils.helpers import get_security_events, format_timestamp, get_severity_color

class AttacksPage: 
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.attacks_container = None
        self.severity_filter = None
        self.create_page()
        
    def create_page(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(title_frame, text="ATTACK INTELLIGENCE", font=("Orbitron", 24, "bold"), text_color="#00d4ff").grid(row=0, column=0, sticky="w") # Title label for the attacks page
        
        filter_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(filter_frame, text="Filter:", font=("Inter", 12), text_color="#8892b0").pack(side="left", padx=5)
        
        self.severity_filter = ctk.CTkComboBox(filter_frame, values=["All", "High", "Medium", "Low"], width=120,
                                               fg_color="#141b2d", border_color="#1a2540", button_color="#141b2d",
                                               command=self.load_data)
        self.severity_filter.pack(side="left", padx=5)
        
        self.attacks_container = ctk.CTkScrollableFrame(self.frame, fg_color="#141b2d", corner_radius=12)
        self.attacks_container.grid(row=1, column=0, sticky="nsew")
        
        self.load_data()
        
    def load_data(self, *args): # Load and display attack events based on the selected severity filter
        for widget in self.attacks_container.winfo_children():
            widget.destroy()
        
        severity = self.severity_filter.get() if self.severity_filter else "All"
        events = get_security_events(100, severity)
        
        if events:
            header_frame = ctk.CTkFrame(self.attacks_container, fg_color="#1a2540", corner_radius=8)
            header_frame.pack(fill="x", pady=(0, 5), padx=5)
            
            headers = ["Time", "Attack Type", "Severity", "Source IP", "Target", "Status"]
            for i, h in enumerate(headers):
                ctk.CTkLabel(header_frame, text=h, font=("Inter", 12, "bold"), text_color="#8892b0").grid(row=0, column=i, padx=10, pady=8, sticky="w")
                header_frame.grid_columnconfigure(i, weight=1)
            
            for event in events: # Display each attack event in a row with relevant details and severity color coding
                row_frame = ctk.CTkFrame(self.attacks_container, fg_color="#0a0e1a", corner_radius=6)
                row_frame.pack(fill="x", pady=2, padx=5)
                
                for i in range(6):
                    row_frame.grid_columnconfigure(i, weight=1)
                
                ctk.CTkLabel(row_frame, text=format_timestamp(event['timestamp']), font=("Inter", 11), text_color="#8892b0").grid(row=0, column=0, padx=10, pady=8, sticky="w") # Display the timestamp of the attack event in a formatted manner
                
                ctk.CTkLabel(row_frame, text=event['event_type'].replace('_', ' ').title(), font=("Inter", 11), text_color="#ffffff").grid(row=0, column=1, padx=10, pady=8, sticky="w") # Display the attack type in a user-friendly format by replacing underscores with spaces and capitalizing words
                
                color = get_severity_color(event['severity'])
                badge = ctk.CTkFrame(row_frame, fg_color=color, corner_radius=12, height=24)
                badge.grid(row=0, column=2, padx=10, pady=6)
                ctk.CTkLabel(badge, text=event['severity'].upper(), font=("Inter", 10, "bold"), text_color="#ffffff").pack(padx=10, pady=2)
                
                ctk.CTkLabel(row_frame, text=event['source_ip'], font=("Orbitron", 10), text_color="#8892b0").grid(row=0, column=3, padx=10, pady=8, sticky="w") # Display the source IP address of the attack event
                
                ctk.CTkLabel(row_frame, text=event['target_endpoint'], font=("Inter", 11), text_color="#8892b0").grid(row=0, column=4, padx=10, pady=8, sticky="w")
                
                status_text = "RESOLVED" if event['resolved'] else "UNRESOLVED"
                status_color = "#00d4aa" if event['resolved'] else "#ff4757"
                ctk.CTkLabel(row_frame, text=status_text, font=("Inter", 11, "bold"), text_color=status_color).grid(row=0, column=5, padx=10, pady=8, sticky="w")
        else:
            ctk.CTkLabel(self.attacks_container, text="No attack events found", text_color="#8892b0", font=("Inter", 14)).pack(pady=40)
        
    def get_frame(self):
        return self.frame
    