import customtkinter as ctk
from utils.helpers import get_security_events, format_timestamp, can_resolve_attack, resolve_security_event
import sqlite3
import os
from tkinter import messagebox

def get_company_connection(): # Establish a connection to the company's database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../replicated_company_limited/database/company.db')
    if os.path.exists(db_path):
        return sqlite3.connect(db_path)
    return None

def get_event_id_by_details(event_type, source_ip, target_endpoint, timestamp): # Retrieve the event ID based on specific details from the database
    conn = get_company_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM security_events 
        WHERE event_type=? AND source_ip=? AND target_endpoint=? AND timestamp=?
        LIMIT 1
    ''', (event_type, source_ip, target_endpoint, timestamp))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

class AlertsPage: # does not inherit from ctk.CTkFrame, it manages its own frame
    def __init__(self, parent, refresh_callback=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.frame = None
        self.alerts_container = None
        self.create_page()
        
    def create_page(self): # Create the alerts page layout
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(title_frame, text="ACTIVE ALERTS", font=("Orbitron", 24, "bold"), text_color="#00d4ff").pack(side="left")
        
        refresh_btn = ctk.CTkButton(title_frame, text="⟳ REFRESH", fg_color="#1a2540", hover_color="#2a3550", 
                                   width=100, height=30, font=("Inter", 11),
                                   command=self.load_data)
        refresh_btn.pack(side="right")
        
        self.alerts_container = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.alerts_container.grid(row=1, column=0, sticky="nsew")
        
        self.load_data()
        
    def resolve_alert(self, alert, alert_frame): # Handle the resolution of an alert
        event_type = alert['event_type']
        verifiable = can_resolve_attack(event_type)
        
        if verifiable:
            is_resolved = verifiable['verify']()
            if not is_resolved:
                messagebox.showerror(
                    "Cannot Resolve",
                    f"❌ {verifiable['error']}\n\nPlease fix the vulnerability first, then try again." # Display an error message if the vulnerability cannot be resolved
                )
                return
            result = messagebox.askyesno(
                "Confirm Resolution",
                f"✅ The vulnerability has been fixed!\n\nEvent: {event_type.replace('_', ' ').title()}\nSource: {alert['source_ip']}\n\nMark this alert as resolved?"
            )
        else:
            result = messagebox.askyesno(
                "Confirm Resolution",
                f"Are you sure this alert is resolved?\n\nEvent: {event_type.replace('_', ' ').title()}\nSource: {alert['source_ip']}\nTarget: {alert['target_endpoint']}\n\nThis will move it to resolved status."
            )
        
        if result:
            event_id = get_event_id_by_details(
                alert['event_type'],
                alert['source_ip'],
                alert['target_endpoint'],
                alert['timestamp']
            )
            if event_id and resolve_security_event(event_id):
                alert_frame.destroy()
                if self.refresh_callback:
                    self.refresh_callback()
                messagebox.showinfo("Success", "Alert resolved successfully!")
            else:
                messagebox.showerror("Error", "Failed to resolve alert. Please try again.")
    
    def load_data(self):
        for widget in self.alerts_container.winfo_children(): # Clear the alerts container before loading new data
            widget.destroy()
        
        events = get_security_events(50)
        unresolved_alerts = [e for e in events if not e['resolved']]
        
        if unresolved_alerts: # Display unresolved alerts if any
            for alert in unresolved_alerts:
                if alert['severity'] == 'high':
                    border_color = "#ff4757"
                    bg_color = "#1a2540"
                    severity_text = "HIGH SEVERITY ALERT"
                    severity_color = "#ff4757"
                else:
                    border_color = "#00d4aa"
                    bg_color = "#0a1a1a"
                    severity_text = "LOW SEVERITY ALERT"
                    severity_color = "#00d4aa"
                
                alert_frame = ctk.CTkFrame(self.alerts_container, fg_color=bg_color, corner_radius=12, border_width=2, border_color=border_color)
                alert_frame.pack(fill="x", pady=8)
                
                header = ctk.CTkFrame(alert_frame, fg_color="transparent")
                header.pack(fill="x", padx=15, pady=(15, 5))
                
                ctk.CTkLabel(header, text=severity_text, font=("Inter", 14, "bold"), text_color=severity_color).pack(side="left")
                ctk.CTkLabel(header, text=format_timestamp(alert['timestamp']), font=("Inter", 11), text_color="#8892b0").pack(side="right")
                
                ctk.CTkLabel(alert_frame, text=alert['description'], font=("Inter", 13), text_color="#ffffff").pack(anchor="w", padx=15, pady=5)
                
                info = ctk.CTkFrame(alert_frame, fg_color="transparent")
                info.pack(fill="x", padx=15, pady=5)
                
                ctk.CTkLabel(info, text=f"Source: {alert['source_ip']}  |  Target: {alert['target_endpoint']}", 
                           font=("Inter", 11), text_color="#8892b0").pack(side="left")
                
                actions = ctk.CTkFrame(alert_frame, fg_color="transparent")
                actions.pack(fill="x", padx=15, pady=(10, 15))
                
                resolve_btn = ctk.CTkButton(actions, text="✓ RESOLVE", fg_color="#00d4aa", hover_color="#00b894", 
                                           width=120, font=("Inter", 12, "bold"),
                                           command=lambda a=alert, f=alert_frame: self.resolve_alert(a, f))
                resolve_btn.pack(side="left", padx=5)
                
                ctk.CTkButton(actions, text="🔍 INVESTIGATE", fg_color="#00d4ff", hover_color="#0099ff", 
                           width=120, font=("Inter", 12, "bold")).pack(side="left", padx=5)
                ctk.CTkButton(actions, text="🚫 BLOCK IP", fg_color="#ff4757", hover_color="#ff3838", 
                           width=120, font=("Inter", 12, "bold")).pack(side="left", padx=5)
        else:
            clear_frame = ctk.CTkFrame(self.alerts_container, fg_color="#141b2d", corner_radius=12)
            clear_frame.pack(fill="x", pady=40)
            
            ctk.CTkLabel(clear_frame, text="NO ACTIVE ALERTS", font=("Orbitron", 24, "bold"), text_color="#00d4aa").pack(pady=40)
            ctk.CTkLabel(clear_frame, text="All systems secure", font=("Inter", 14), text_color="#8892b0").pack(pady=(0, 40))
        
    def get_frame(self):
        return self.frame
    