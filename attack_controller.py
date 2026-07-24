#!/usr/bin/env python3
"""
Attack Simulation Toolkit - NOW CREATES ALERTS DIRECTLY
"""

import sys
import time
import argparse
import sqlite3
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class AttackController:
    def __init__(self):
        self.target_url = "http://192.168.101.12:5001"
        
    def create_alert_direct(self, event_type, severity, source_ip, target_endpoint, description):
        """Directly insert alert into database"""
        try:
            db_path = os.path.expanduser("~/Desktop/replicated_company_limited/database/company.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if unresolved alert exists for this type
            cursor.execute('''
                SELECT COUNT(*) FROM security_events 
                WHERE event_type = ? AND resolved = 0
            ''', (event_type,))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                print(f"⏳ Alert already exists for {event_type}")
                return False
            
            cursor.execute('''
                INSERT INTO security_events 
                (event_type, severity, source_ip, target_endpoint, description, timestamp, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_type,
                severity,
                source_ip,
                target_endpoint,
                description,
                datetime.now().isoformat(),
                0
            ))
            conn.commit()
            conn.close()
            print(f"✅ Alert created: {event_type}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def banner(self):
        print(Fore.CYAN + "="*70)
        print(Fore.RED + "  █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗")
        print(Fore.RED + " ██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝")
        print(Fore.RED + " ███████║   ██║      ██║   ███████║██║     █████╔╝ ")
        print(Fore.RED + " ██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗ ")
        print(Fore.RED + " ██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗")
        print(Fore.RED + " ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝")
        print(Fore.CYAN + "="*70)
        print(Fore.RED + "🎯 ATTACK SIMULATION TOOLKIT")
        print(Fore.YELLOW + f"Target: {self.target_url}")
        print(Fore.CYAN + "="*70 + "\n")
    
    def run_attack(self, attack_type, **kwargs):
        """Execute attack and create alerts"""
        
        if attack_type == "request_flood":
            from attacks.request_flood import RequestFlood
            attack = RequestFlood(self.target_url)
            print(Fore.YELLOW + "🚨 REQUEST FLOOD ATTACK")
            print(Fore.YELLOW + f"   Requests: {kwargs.get('requests', 10)}\n")
            
            # Run attack
            result = attack.execute(
                requests=kwargs.get('requests', 10),
                delay=kwargs.get('delay', 0.05)
            )
            
            # Create alert IMMEDIATELY
            self.create_alert_direct(
                'request_flood_detected',
                'medium',
                '127.0.0.1',
                '/',
                f'🟡 Request Flood Attack detected. {kwargs.get("requests", 10)} requests sent.'
            )
            return result
            
        elif attack_type == "simulated_ddos":
            from attacks.ddos import DDOSAttack
            attack = DDOSAttack(self.target_url)
            print(Fore.RED + "🚨 DDoS ATTACK")
            print(Fore.RED + f"   Requests: {kwargs.get('requests', 20)}\n")
            
            result = attack.execute(
                requests=kwargs.get('requests', 20),
                threads=kwargs.get('threads', 3),
                delay=kwargs.get('delay', 0.05)
            )
            
            # Create alert IMMEDIATELY
            self.create_alert_direct(
                'ddos_attack_detected',
                'high',
                '127.0.0.1',
                '/',
                f'🔴 DDoS Attack detected. {kwargs.get("requests", 20)} requests sent.'
            )
            return result
            
        elif attack_type == "endpoint_scanner":
            from attacks.scanner import ScannerAttack
            attack = ScannerAttack(self.target_url)
            print(Fore.RED + "🔍 ENDPOINT SCANNER")
            print(Fore.RED + f"   Paths: {kwargs.get('max_paths', 20)}\n")
            
            result = attack.execute(
                max_paths=kwargs.get('max_paths', 20),
                delay=kwargs.get('delay', 0.2)
            )
            
            # Create alert IMMEDIATELY
            self.create_alert_direct(
                'endpoint_scanner_detected',
                'medium',
                '127.0.0.1',
                '/',
                f'🟡 Endpoint Scanner detected. Scanned {kwargs.get("max_paths", 20)} paths.'
            )
            return result
            
        elif attack_type == "bruteforce":
            from attacks.bruteforce import BruteForceAttack
            attack = BruteForceAttack(self.target_url)
            print(Fore.RED + "🔑 BRUTE FORCE ATTACK")
            print(Fore.RED + f"   Target: {kwargs.get('username', 'john.smith')}\n")
            
            result = attack.execute(
                username=kwargs.get('username', 'john.smith'),
                max_attempts=kwargs.get('max_attempts', 10),
                delay=kwargs.get('delay', 0.01)
            )
            
            # Create alert IMMEDIATELY
            self.create_alert_direct(
                'bruteforce_attack_detected',
                'high',
                '127.0.0.1',
                '/auth/admin-login',
                f'🔴 Brute Force Attack detected on {kwargs.get("username", "john.smith")}. {kwargs.get("max_attempts", 10)} attempts made.'
            )
            return result
            
        elif attack_type == "all":
            return self.run_all_attacks()
        else:
            print(Fore.RED + f"❌ Unknown attack type: {attack_type}")
            return False
    
    def run_all_attacks(self):
        """Run all attacks"""
        print(Fore.RED + "\n" + "="*70)
        print(Fore.RED + "🔥 STARTING FULL ATTACK SUITE")
        print(Fore.RED + "="*70 + "\n")
        
        attacks = [
            ("endpoint_scanner", {"max_paths": 10, "delay": 0.2}),
            ("request_flood", {"requests": 8, "delay": 0.05}),
            ("simulated_ddos", {"requests": 15, "threads": 3}),
            ("bruteforce", {"username": "john.smith", "max_attempts": 10})
        ]
        
        for attack_type, kwargs in attacks:
            print(Fore.CYAN + f"\n[+] Running {attack_type.upper()}...")
            self.run_attack(attack_type, **kwargs)
            time.sleep(2)
            
        print(Fore.GREEN + "\n[+] All attacks completed!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Attack Simulation Toolkit')
    parser.add_argument('--target', help='Target URL')
    parser.add_argument('--attack', choices=['bruteforce', 'simulated_ddos', 
                                            'request_flood', 'endpoint_scanner', 'all'],
                       required=True, help='Type of attack')
    parser.add_argument('--username', default='john.smith', help='Username for brute force')
    parser.add_argument('--max_attempts', type=int, default=10, help='Max attempts')
    parser.add_argument('--threads', type=int, default=3, help='Threads for DDoS')
    parser.add_argument('--requests', type=int, default=15, help='Number of requests')
    parser.add_argument('--max_paths', type=int, default=10, help='Max paths to scan')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between requests')
    
    args = parser.parse_args()
    
    controller = AttackController()
    if args.target:
        controller.target_url = args.target
        
    kwargs = {
        'username': args.username,
        'max_attempts': args.max_attempts,
        'threads': args.threads,
        'requests': args.requests,
        'max_paths': args.max_paths,
        'delay': args.delay
    }
    
    controller.run_attack(args.attack, **kwargs)

if __name__ == "__main__":
    main()
