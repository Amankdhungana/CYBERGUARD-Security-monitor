import customtkinter as ctk
from tkinter import Canvas
from datetime import datetime
from utils.helpers import get_attack_statistics, get_security_events, get_activity_logs, format_timestamp, get_severity_color
import random

class DashboardPage: 
    def __init__(self, parent): 
        self.parent = parent
        self.frame = None
        self.main_frame = None
        self.stats_labels = {}
        self.create_page()
        
    def create_page(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.load_data()
        
    def create_stat_card(self, parent, icon, value, label, sub, color, key): # Create a card to display a specific statistic with an icon, value, label, and subtext
        card = ctk.CTkFrame(parent, fg_color="#141b2d", corner_radius=12, border_width=1, border_color="#1a2540")
        card.pack(side="left", fill="x", expand=True, padx=6)
        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 0))
        
        ctk.CTkLabel(top, text=icon, font=("Inter", 22)).pack(side="left")
        val_label = ctk.CTkLabel(top, text=value, font=("Orbitron", 30, "bold"), text_color=color)
        val_label.pack(side="right")
        
        ctk.CTkLabel(card, text=label, font=("Inter", 11), text_color="#8892b0").pack(anchor="w", padx=20)
        ctk.CTkLabel(card, text=sub, font=("Inter", 10), text_color="#00d4aa" if "↑" in sub else "#8892b0").pack(anchor="w", padx=20, pady=(0, 15))
        
        self.stats_labels[key] = val_label
        return card
    
    def create_chart(self, parent, data): # Create a line chart to visualize attack trends over time using a Canvas widget
        canvas = Canvas(parent, bg="#0a0e1a", highlightthickness=1, highlightbackground="#1a2540", height=200)
        canvas.pack(fill="x", padx=20, pady=(10, 20))
        
        if not data: # Display a message if there is no data available for the chart
            canvas.create_text(300, 100, text="No data available", fill="#8892b0", font=("Inter", 12))
            return canvas
        
        width = canvas.winfo_width() if canvas.winfo_width() > 100 else 600 # Set a default width if the canvas width is too small
        height = 200
        padding = 30
        
        max_val = max(data) if data else 1
        
        points = []
        for i, val in enumerate(data): 
            x = padding + (width - 2*padding) * i / (len(data) - 1)
            y = height - padding - (height - 2*padding) * val / max_val
            points.extend([x, y])
        
        if len(points) >= 4: # Draw a smooth line connecting the data points on the canvas if there are enough points to form a line
            canvas.create_line(points, fill="#00d4ff", width=3, smooth=True)
            
            for i, val in enumerate(data):
                x = padding + (width - 2*padding) * i / (len(data) - 1)
                y = height - padding - (height - 2*padding) * val / max_val
                canvas.create_oval(x-4, y-4, x+4, y+4, fill="#00d4ff", outline="")
        
        return canvas
    
    def load_data(self): # Load and display the dashboard data, including statistics, recent events, and activity logs
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        stats = get_attack_statistics()
        events = get_security_events(6)
        
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="SECURITY DASHBOARD", font=("Orbitron", 22, "bold"), text_color="#00d4ff").pack(side="left")
        
        time_label = ctk.CTkLabel(header, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), font=("Inter", 12), text_color="#8892b0")
        time_label.pack(side="right")
        
        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        cards = [
            ("⚠️", str(stats.get('total_attacks', 0)), "TOTAL ATTACKS", "↑ 12% this week", "#00d4ff", "total"),
            ("🚨", str(stats.get('high_severity', 0)), "HIGH SEVERITY", "Critical", "#ff4757", "high"),
            ("⏳", str(stats.get('unresolved', 0)), "UNRESOLVED", "Pending", "#ffd93d", "unresolved"),
            ("🌐", str(len(stats.get('top_ips', []))), "ATTACK SOURCES", "Active", "#00d4aa", "sources")
        ]
        
        for icon, value, label, sub, color, key in cards:
            self.create_stat_card(stats_frame, icon, value, label, sub, color, key)
        
        chart_data = [random.randint(1, 15) for _ in range(30)]
        
        chart_frame = ctk.CTkFrame(self.main_frame, fg_color="#0a0e1a", corner_radius=12, border_width=1, border_color="#1a2540")
        chart_frame.pack(fill="x", pady=(0, 20))
        
        chart_header = ctk.CTkFrame(chart_frame, fg_color="transparent")
        chart_header.pack(fill="x", padx=20, pady=(15, 0))
        
        ctk.CTkLabel(chart_header, text="ATTACK TREND (30 DAYS)", font=("Inter", 14, "bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(chart_header, text="Live", font=("Inter", 10, "bold"), text_color="#00d4aa").pack(side="right")
        
        self.create_chart(chart_frame, chart_data)
        
        bottom = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom.pack(fill="both", expand=True)
        
        left = ctk.CTkFrame(bottom, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        events_frame = ctk.CTkFrame(left, fg_color="#0a0e1a", corner_radius=12, border_width=1, border_color="#1a2540")
        events_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(events_frame, text="RECENT EVENTS", font=("Inter", 14, "bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=15)
        
        events_container = ctk.CTkFrame(events_frame, fg_color="transparent")
        events_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        if events: # Display the most recent security events if available, otherwise show a message indicating no recent events
            for event in events[:5]:
                row = ctk.CTkFrame(events_container, fg_color="#141b2d", corner_radius=6)
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=format_timestamp(event['timestamp']), font=("Inter", 10), text_color="#8892b0", width=100).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(row, text=event['event_type'].replace('_', ' ').title()[:25], font=("Inter", 11), text_color="#ffffff", width=150).pack(side="left", padx=10, pady=6)
                
                color = get_severity_color(event['severity'])
                badge = ctk.CTkFrame(row, fg_color=color, corner_radius=10, height=20)
                badge.pack(side="left", padx=10)
                ctk.CTkLabel(badge, text=event['severity'].upper(), font=("Inter", 9, "bold"), text_color="#ffffff").pack(padx=8, pady=2)
                
                ctk.CTkLabel(row, text=event['source_ip'], font=("Orbitron", 10), text_color="#8892b0", width=100).pack(side="left", padx=10, pady=6)
                
                status_text = "RESOLVED" if event['resolved'] else "UNRESOLVED"
                status_color = "#00d4aa" if event['resolved'] else "#ff4757"
                ctk.CTkLabel(row, text=status_text, font=("Inter", 10, "bold"), text_color=status_color, width=80).pack(side="right", padx=10, pady=6)
        else:
            ctk.CTkLabel(events_container, text="No recent events", text_color="#8892b0").pack(pady=20)
        
        right = ctk.CTkFrame(bottom, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        logs_frame = ctk.CTkFrame(right, fg_color="#0a0e1a", corner_radius=12, border_width=1, border_color="#1a2540")
        logs_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(logs_frame, text="ACTIVITY LOGS", font=("Inter", 14, "bold"), text_color="#ffffff").pack(anchor="w", padx=20, pady=15)
        
        logs_container = ctk.CTkFrame(logs_frame, fg_color="transparent")
        logs_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        logs = get_activity_logs(5)
        if logs: # Display the most recent activity logs if available, otherwise show a message indicating no recent logs
            for log in logs:
                row = ctk.CTkFrame(logs_container, fg_color="#141b2d", corner_radius=6)
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=log['user'], font=("Inter", 11, "bold"), text_color="#00d4ff", width=80).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(row, text=log['action'].replace('_', ' ').title()[:20], font=("Inter", 11), text_color="#ffffff", width=120).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(row, text=log['ip_address'], font=("Orbitron", 10), text_color="#8892b0", width=100).pack(side="left", padx=10, pady=6)
                
                status_color = "#00d4aa" if log['status'] == 'success' else "#ff4757"
                ctk.CTkLabel(row, text=log['status'].upper(), font=("Inter", 10, "bold"), text_color=status_color, width=60).pack(side="right", padx=10, pady=6)
        else:
            ctk.CTkLabel(logs_container, text="No recent logs", text_color="#8892b0").pack(pady=20)
        
        self.frame.update()
        
    def get_frame(self):
        return self.frame
    