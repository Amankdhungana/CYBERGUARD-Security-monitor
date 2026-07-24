# CYBERGUARD-Security-monitor
Cyber Attack Simulation & Monitoring System

It is a complete cybersecurity training environment consisting of a simulated enterprise web application and an attack simulation toolkit. The system generates realistic logs and attack patterns for security monitoring training.


Company System
It is a fully functional web application simulating a real company environment with employee and admin portals, document management, and comprehensive logging capabilities.


Key Features

Role-based access control (Admin/Employee)
Employee and Admin authentication portals
Company file repository with role-based access
Activity logging for all user actions
Security event logging for unauthorized access
Session management and account lockout
Professional UI resembling a real business website


Attack Toolkit
This is a collection of Python scripts that simulate real-world cyber attacks in a controlled environment.


Attack Types

Endpoint Scanner – Directory enumeration to find hidden/admin pages
Brute Force – Password guessing attacks targeting admin portals
DDoS – Distributed denial of service with IP spoofing
DoS – Single-source denial of service

Monitoring System
Collects and analyzes logs from the company system and attack toolkit to provide security visibility.


Key Features

Real-time attack detection
Attack classification and severity assessment
Behavioral monitoring from activity logs
Visual dashboards with charts and graphs
Incident response recommendations
Automated alert generation
IP tracking and threat intelligence


Tools Used

Component	           Tools
Company System	     Python 3, Flask, SQLAlchemy, SQLite, HTML/CSS
Attack Toolkit	     Python 3, Requests, Aiohttp, Colorama
Monitoring System    Python, customtkinter, sqlite3


Key Considerations

Educational Purpose Only – Designed for training and controlled testing

Authorized Testing – Only use on systems you own or have explicit permission to test

Local Environment – Keep testing within your isolated network

Legal Compliance – Unauthorized access is illegal in most jurisdictions


