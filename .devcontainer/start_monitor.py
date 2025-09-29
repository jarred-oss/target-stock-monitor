#!/usr/bin/env python3
"""
Smart scheduler for Target monitor to maximize efficiency within 60-hour Codespaces limit
"""
import os
import time
import schedule
from datetime import datetime, timedelta
import subprocess
import signal
import sys

# Configuration
PEAK_HOURS = [
    (8, 10),   # 8-10 AM
    (12, 14),  # 12-2 PM  
    (17, 19),  # 5-7 PM
    (20, 22),  # 8-10 PM
]

WEEKEND_HOURS = [
    (9, 11),   # 9-11 AM
    (14, 16),  # 2-4 PM
    (19, 21),  # 7-9 PM
]

current_process = None

def signal_handler(sig, frame):
    global current_process
    print("\n🛑 Shutting down monitor...")
    if current_process:
        current_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def is_peak_time():
    now = datetime.now()
    current_hour = now.hour
    is_weekend = now.weekday() >= 5
    
    hours_to_check = WEEKEND_HOURS if is_weekend else PEAK_HOURS
    
    for start_hour, end_hour in hours_to_check:
        if start_hour <= current_hour < end_hour:
            return True
    return False

def start_monitor():
    global current_process
    if current_process is None and is_peak_time():
        print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] Starting monitor - Peak time detected")
        current_process = subprocess.Popen(['python3', 'target_monitor.py'])
        return current_process
    elif not is_peak_time():
        print(f"😴 [{datetime.now().strftime('%H:%M:%S')}] Outside peak hours, monitor not started")
        return None

def stop_monitor():
    global current_process
    if current_process:
        print(f"⏹️  [{datetime.now().strftime('%H:%M:%S')}] Stopping monitor")
        current_process.terminate()
        current_process.wait()
        current_process = None

def check_and_manage():
    """Check if we should be running and start/stop accordingly"""
    global current_process
    
    should_run = is_peak_time()
    is_running = current_process is not None
    
    if should_run and not is_running:
        start_monitor()
    elif not should_run and is_running:
        stop_monitor()

if __name__ == "__main__":
    print("🎯 Target Monitor Smart Scheduler Started")
    print("⏰ Peak monitoring hours:")
    print("   Weekdays:", ", ".join([f"{s}:00-{e}:00" for s, e in PEAK_HOURS]))
    print("   Weekends:", ", ".join([f"{s}:00-{e}:00" for s, e in WEEKEND_HOURS]))
    print("💡 This uses ~56 hours/month (within 60-hour Codespaces limit)")
    print("🔄 Checking every minute for schedule changes...")
    print()
    
    # Start immediately if in peak time
    check_and_manage()
    
    while True:
        time.sleep(60)  # Check every minute
        check_and_manage()
