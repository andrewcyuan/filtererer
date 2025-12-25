import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import subprocess
import sys
import plistlib
import shutil

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "blocked_sites.json")
START_SCRIPT = os.path.join(SCRIPT_DIR, "start_filter.sh")
STOP_SCRIPT = os.path.join(SCRIPT_DIR, "stop_filter.sh")
PLIST_NAME = "com.user.filtererer.plist"
PLIST_PATH = os.path.expanduser(f"~/Library/LaunchAgents/{PLIST_NAME}")

class FilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtererer Manager")
        self.root.geometry("500x450")
        
        # Site List
        lbl = tk.Label(root, text="Blocked URL Slugs:")
        lbl.pack(pady=(10, 0))
        
        self.sites = []
        self.listbox = tk.Listbox(root)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Buttons Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="Add Site", command=self.add_site).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_site).pack(side=tk.LEFT, padx=5)
        
        # Service Control Frame
        control_frame = tk.LabelFrame(root, text="Service Control", padx=10, pady=10)
        control_frame.pack(fill=tk.X, padx=10, pady=20)
        
        tk.Button(control_frame, text="1. Setup Permissions (Run Once)", command=self.setup_permissions).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="2. Install & Start Background Service", command=self.install_service).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="3. Stop & Uninstall Service", command=self.uninstall_service).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Emergency Stop Proxy", command=self.stop_proxy).pack(fill=tk.X, pady=2)

        self.load_sites()

    def load_sites(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.sites = json.load(f)
            except:
                self.sites = []
        self.refresh_list()

    def save_sites(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.sites, f, indent=4)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for site in self.sites:
            self.listbox.insert(tk.END, site)

    def add_site(self):
        site = simpledialog.askstring("Add Site", "Enter URL slug to block:")
        if site:
            self.sites.append(site)
            self.save_sites()

    def remove_site(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            del self.sites[idx]
            self.save_sites()

    def setup_permissions(self):
        """Adds networksetup to sudoers without password for current user"""
        user = os.getenv("USER")
        if not user:
            messagebox.showerror("Error", "Could not determine user")
            return
            
        sudoers_content = f"{user} ALL=(ALL) NOPASSWD: /usr/sbin/networksetup"
        temp_file = "/tmp/filtererer_sudoers"
        
        script = f"""
        do shell script "echo '{sudoers_content}' > {temp_file} && chmod 440 {temp_file} && chown root:wheel {temp_file} && mv {temp_file} /etc/sudoers.d/filtererer" with administrator privileges
        """
        
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            messagebox.showinfo("Success", "Permissions granted. You can now run the service in the background.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to set permissions: {e}")

    def install_service(self):
        self.fix_scripts()
        
        plist_content = {
            'Label': 'com.user.filtererer',
            'ProgramArguments': [START_SCRIPT],
            'RunAtLoad': True,
            'KeepAlive': True,
            'StandardOutPath': '/tmp/filtererer.log',
            'StandardErrorPath': '/tmp/filtererer.err'
        }
        
        try:
            with open(PLIST_PATH, 'wb') as f:
                plistlib.dump(plist_content, f)
            
            # Unload if exists then load
            subprocess.run(["launchctl", "unload", PLIST_PATH], check=False, capture_output=True)
            subprocess.run(["launchctl", "load", PLIST_PATH], check=True)
            messagebox.showinfo("Success", "Service installed and started! It will run on login.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install service: {e}")

    def uninstall_service(self):
        try:
            if os.path.exists(PLIST_PATH):
                subprocess.run(["launchctl", "unload", PLIST_PATH], check=False)
                os.remove(PLIST_PATH)
            
            self.stop_proxy()
            messagebox.showinfo("Success", "Service uninstalled.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to uninstall: {e}")

    def stop_proxy(self):
        try:
            subprocess.run([STOP_SCRIPT], check=True)
            messagebox.showinfo("Info", "Proxy settings reset.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop proxy: {e}")

    def fix_scripts(self):
        mitm_path = shutil.which("mitmdump")
        if not mitm_path:
            # Fallback or try to find it in likely places
            common_paths = [
                "/usr/local/bin/mitmdump",
                "/opt/homebrew/bin/mitmdump",
                os.path.expanduser("~/.local/bin/mitmdump"),
                # Add python script directory if it's a venv
                os.path.join(os.path.dirname(sys.executable), "mitmdump")
            ]
            for p in common_paths:
                if os.path.exists(p):
                    mitm_path = p
                    break
        
        if not mitm_path:
            mitm_path = "mitmdump" # Hope it's in path when run

        start_content = f"""#!/bin/bash
cd "{SCRIPT_DIR}"

# Cleanup function to restore proxy settings on exit
cleanup() {{
    echo "Cleaning up proxy settings..."
    sudo networksetup -setwebproxystate "Wi-Fi" off
    sudo networksetup -setsecurewebproxystate "Wi-Fi" off
    exit
}}

# Trap signals
trap cleanup SIGINT SIGTERM

# Set Web Proxy (HTTP)
sudo networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
# Set Secure Web Proxy (HTTPS)
sudo networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080

echo "Starting mitmdump..."
"{mitm_path}" -s traffic_control.py &
PID=$!
wait $PID
"""
        with open(START_SCRIPT, 'w') as f:
            f.write(start_content)
        os.chmod(START_SCRIPT, 0o755)

        # Also ensure stop script is correct/absolute just in case
        stop_content = f"""#!/bin/bash
sudo networksetup -setsecurewebproxystate "Wi-Fi" off              
sudo networksetup -setwebproxystate "Wi-Fi" off
"""
        with open(STOP_SCRIPT, 'w') as f:
            f.write(stop_content)
        os.chmod(STOP_SCRIPT, 0o755)

if __name__ == "__main__":
    root = tk.Tk()
    app = FilterApp(root)
    root.mainloop()

