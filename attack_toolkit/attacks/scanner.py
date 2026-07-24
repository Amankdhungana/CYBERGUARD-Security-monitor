#!/usr/bin/env python3
"""
Automated Directory/Endpoint Scanner
Simulates real attackers scanning for hidden/admin pages
"""

import requests
import time
import random
from datetime import datetime
from colorama import Fore, Style

class ScannerAttack:
    def __init__(self, target_url):
        self.target_url = target_url
        self.results = []
        self.found_endpoints = []
        
        # Common admin and sensitive paths
        self.directories = [
            # Admin paths
            "/admin",
            "/administrator",
            "/admin/login",
            "/admin/dashboard",
            "/adminpanel",
            "/manage",
            "/manager",
            "/admin/",
            "/admin/index.html",
            "/admin.php",
            "/wp-admin",
            "/cpanel",
            
            # Employee/User paths
            "/employee",
            "/employee/dashboard",
            "/user",
            "/users",
            "/dashboard",
            "/profile",
            "/account",
            "/myaccount",
            
            # Authentication paths
            "/login",
            "/auth",
            "/auth/login",
            "/auth/employee-login",
            "/auth/admin-login",
            "/register",
            "/signup",
            "/signin",
            
            # Sensitive files
            "/.env",
            "/.git",
            "/.git/config",
            "/config",
            "/config.php",
            "/config.json",
            "/settings",
            "/settings.json",
            "/database",
            "/db",
            "/backup",
            "/backups",
            "/.backup",
            
            # Logs and data
            "/logs",
            "/log",
            "/debug",
            "/trace",
            "/info",
            "/status",
            "/health",
            "/stats",
            "/statistics",
            
            # API endpoints
            "/api",
            "/api/",
            "/api/v1",
            "/api/v2",
            "/rest",
            "/restapi",
            "/graphql",
            "/swagger",
            
            # File paths
            "/files",
            "/downloads",
            "/uploads",
            "/media",
            "/assets",
            "/static",
            "/public",
            
            # Common vulnerabilities
            "/phpmyadmin",
            "/mysql",
            "/dbadmin",
            "/sqladmin",
            "/webmail",
            "/mail",
            "/email",
            "/cgi-bin",
            "/shell",
            "/cmd",
            "/exec",
            
            # Hidden/backup files
            "/.htaccess",
            "/.htpasswd",
            "/.ssh",
            "/.aws",
            "/.env.local",
            "/composer.json",
            "/package.json",
            "/yarn.lock",
            "/Gemfile",
            
            # Development paths
            "/dev",
            "/test",
            "/testing",
            "/staging",
            "/stage",
            "/demo",
            "/sample",
            
            # Company-specific paths
            "/replicated",
            "/company",
            "/corporate",
            "/internal",
            "/confidential",
            "/secret",
            "/secure"
        ]
        
        # User-Agent rotation to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        ]
    
    def scan_endpoint(self, path):
        """Scan a single endpoint"""
        try:
            url = f"{self.target_url}{path}"
            
            # Random delay to avoid rate limiting
            time.sleep(random.uniform(0.1, 0.3))
            
            response = requests.get(
                url,
                timeout=5,
                headers={
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive'
                },
                allow_redirects=False,
                verify=False
            )
            
            # Determine status
            if response.status_code == 200:
                status = "FOUND 🔍"
                color = Fore.RED
                self.found_endpoints.append({
                    'path': path,
                    'status': response.status_code,
                    'size': len(response.content)
                })
                print(f"{color}   ✅ {path} - {response.status_code} (FOUND)")
                
            elif response.status_code == 403:
                status = "FORBIDDEN 🚫"
                color = Fore.YELLOW
                print(f"{color}   🔒 {path} - {response.status_code} (Blocked)")
                
            elif response.status_code == 302 or response.status_code == 301:
                status = "REDIRECT ➡️"
                color = Fore.YELLOW
                print(f"{color}   🔄 {path} - {response.status_code} (Redirect)")
                
            elif response.status_code == 404:
                status = "NOT FOUND"
                color = Fore.GREEN
                print(f"{color}   ❌ {path} - {response.status_code} (Not Found)")
                
            else:
                status = f"Status {response.status_code}"
                color = Fore.YELLOW
                print(f"{color}   ℹ️  {path} - {response.status_code}")
            
            self.results.append({
                'path': path,
                'status_code': response.status_code,
                'status': status,
                'size': len(response.content) if response.status_code == 200 else 0,
                'timestamp': datetime.now().isoformat()
            })
            
            return response.status_code
            
        except requests.exceptions.ConnectionError:
            print(Fore.RED + f"   ❌ {path} - Connection error")
            self.results.append({
                'path': path,
                'status_code': 'ERROR',
                'status': 'Connection Error',
                'timestamp': datetime.now().isoformat()
            })
            return None
            
        except Exception as e:
            print(Fore.RED + f"   ❌ {path} - Error: {str(e)[:30]}")
            self.results.append({
                'path': path,
                'status_code': 'ERROR',
                'status': str(e)[:30],
                'timestamp': datetime.now().isoformat()
            })
            return None
    
    def execute(self, max_paths=None, delay=0.1):
        """Execute directory scanner attack"""
        print(Fore.RED + "\n" + "="*70)
        print(Fore.RED + "🔍 AUTOMATED DIRECTORY SCANNER")
        print(Fore.RED + "   Simulating real attacker scanning for hidden/admin paths")
        print(Fore.RED + "="*70 + "\n")
        
        print(Fore.YELLOW + f"🎯 Target: {self.target_url}")
        print(Fore.YELLOW + f"📁 Total paths to scan: {len(self.directories) if not max_paths else max_paths}")
        print(Fore.YELLOW + f"⏱️  Delay between requests: {delay}s")
        print(Fore.CYAN + "\n" + "="*70 + "\n")
        
        
        paths = self.directories
        if max_paths:
            paths = paths[:max_paths]
        
        start_time = time.time()
        
        # Scan each path
        for i, path in enumerate(paths, 1):
            print(Fore.CYAN + f"[{i}/{len(paths)}] Scanning: {path}")
            self.scan_endpoint(path)
        
        elapsed = time.time() - start_time
        
        # Print summary
        print(Fore.CYAN + "\n" + "="*70)
        print(Fore.CYAN + "📊 SCAN RESULTS SUMMARY")
        print(Fore.CYAN + "="*70)
        
        found = [r for r in self.results if r['status_code'] == 200]
        forbidden = [r for r in self.results if r['status_code'] == 403]
        redirected = [r for r in self.results if r['status_code'] in [301, 302]]
        errors = [r for r in self.results if r['status_code'] == 'ERROR']
        
        print(Fore.RED + f"🔍 Found (200 OK): {len(found)}")
        for f in found:
            print(Fore.RED + f"   → {f['path']} (Size: {f['size']} bytes)")
        
        print(Fore.YELLOW + f"🚫 Forbidden (403): {len(forbidden)}")
        print(Fore.YELLOW + f"🔄 Redirects (301/302): {len(redirected)}")
        print(Fore.RED + f"❌ Errors: {len(errors)}")
        print(Fore.CYAN + f"📊 Total scanned: {len(self.results)}")
        print(Fore.CYAN + f"⏱️  Time taken: {elapsed:.2f} seconds")
        
        if found:
            print(Fore.RED + "\n⚠️  WARNING: Found accessible endpoints!")
            print(Fore.RED + "   These should be protected or removed!")
        else:
            print(Fore.GREEN + "\n✅ No accessible endpoints found - strong security!")
        
        print(Fore.CYAN + "="*70 + "\n")
        
        return {
            'total_scanned': len(self.results),
            'found': len(found),
            'found_paths': [f['path'] for f in found],
            'forbidden': len(forbidden),
            'redirected': len(redirected),
            'errors': len(errors),
            'elapsed': elapsed,
            'results': self.results
        }
    