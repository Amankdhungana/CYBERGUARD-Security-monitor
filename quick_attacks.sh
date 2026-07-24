#!/bin/bash
# Quick attack scripts for testing

TARGET="http://192.168.101.12:5001"

echo "=== ATTACK SIMULATION SCRIPTS ==="
echo ""
echo "1. Brute Force (50 attempts)"
echo "python3 attack_controller.py --attack bruteforce --username john.smith --attempts 50"
echo ""
echo "2. DDoS (200 requests, 10 threads)"
echo "python3 attack_controller.py --attack ddos --requests 200 --threads 10"
echo ""
echo "3. Request Flood (100 requests, 0.05s delay)"
echo "python3 attack_controller.py --attack request_flood --requests 100 --delay 0.05"
echo ""
echo "4. Unauthorized Access"
echo "python3 attack_controller.py --attack unauthorized_access"
echo ""
echo "5. Password Cracking (30 attempts)"
echo "python3 attack_controller.py --attack password_cracking --username john.smith --attempts 30"
echo ""
echo "6. ALL ATTACKS (Full Suite)"
echo "python3 attack_controller.py --attack all"
