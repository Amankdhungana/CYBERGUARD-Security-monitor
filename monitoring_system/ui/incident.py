import customtkinter as ctk

class IncidentPage:
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.main_frame = None
        self.create_page()
        
    def create_page(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.main_frame, text="INCIDENT RESPONSE PLAYBOOK", font=("Orbitron", 24, "bold"), text_color="#00d4ff").pack(anchor="w", pady=(0, 25))
        
        steps_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        steps_frame.pack(fill="both", expand=True)
        
        steps = [     # Define the steps of the incident response playbook with their respective actions and colors
            ("DETECTION", 
             ["Monitor security events dashboard", "Review high severity alerts", "Analyze attack patterns"],
             "#00d4ff"),
            ("INVESTIGATION", 
             ["Identify source IP addresses", "Review activity logs", "Determine attack vector"],
             "#ffd93d"),
            ("CONTAINMENT", 
             ["Block malicious IP addresses", "Implement rate limiting", "Disable compromised accounts"],
             "#ff4757"),
            ("RECOVERY", 
             ["Apply security patches", "Update security policies", "Generate incident report"],
             "#00d4aa")
        ] 
        
        for i, (title, items, color) in enumerate(steps): # Iterate through each step and create a frame for it
            step_frame = ctk.CTkFrame(steps_frame, fg_color="#141b2d", corner_radius=12)
            step_frame.pack(side="left", fill="both", expand=True, padx=8)
            
            ctk.CTkLabel(step_frame, text=title, font=("Orbitron", 14, "bold"), text_color=color).pack(anchor="w", pady=15, padx=20)
            
            for item in items:
                ctk.CTkLabel(step_frame, text=f"► {item}", font=("Inter", 12), text_color="#8892b0", justify="left").pack(anchor="w", padx=20, pady=4)
            
            if i < 3:
                ctk.CTkLabel(step_frame, text="▼", font=("Inter", 20), text_color="#1a2540").pack(pady=10)
        
    def get_frame(self):
        return self.frame
    