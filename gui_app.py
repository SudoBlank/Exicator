import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import ctypes
import sys

class PermissionElevatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Permission Elevator 🛡️")
        self.root.geometry("700x500")
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🛡️ Permission Elevator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(file_frame, text="Target File:").grid(row=0, column=0, sticky=tk.W)
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=60)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=(5, 0))
        
        # Permission options
        perm_frame = ttk.LabelFrame(main_frame, text="Permission Options", padding="10")
        perm_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.permission_level = tk.StringVar(value="administrator")
        ttk.Radiobutton(perm_frame, text="Administrator Level (Standard)", 
                       variable=self.permission_level, value="administrator").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(perm_frame, text="Current User (Full Control)", 
                       variable=self.permission_level, value="user").grid(row=1, column=0, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 15))
        
        ttk.Button(button_frame, text="🔧 Elevate Permissions", 
                  command=self.elevate_permissions, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Check Current Permissions", 
                  command=self.check_permissions, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.root.quit, width=10).pack(side=tk.LEFT)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80, font=("Consolas", 9))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Select a file to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select file to elevate permissions",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.update_status(f"Selected: {os.path.basename(filename)}")
    
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()
    
    def log_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def elevate_permissions(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
        
        self.clear_output()
        self.update_status("Starting permission elevation...")
        
        # Fix path formatting
        file_path_fixed = os.path.normpath(file_path)
        
        self.log_output("🚀 Starting permission elevation process...")
        self.log_output(f"📁 Target: {file_path_fixed}")
        
        if not self.is_admin():
            self.log_output("⚠️  Not running as administrator")
            self.log_output("💡 Some operations may fail without admin rights")
        
        try:
            # Step 1: Take ownership with multiple attempts
            self.log_output("\n1. Taking ownership...")
            ownership_commands = [
                f'takeown /F "{file_path_fixed}" /A',  # Give to Administrators
                f'takeown /F "{file_path_fixed}"',      # Give to current user
            ]
            
            ownership_success = False
            for i, cmd in enumerate(ownership_commands, 1):
                self.log_output(f"   Attempt {i}: {cmd.split()[0]}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_output("   ✅ Ownership acquired successfully")
                    ownership_success = True
                    break
                else:
                    error_msg = result.stderr.strip()
                    if "Access is denied" in error_msg:
                        self.log_output("   ❌ Access denied - need admin rights")
                    elif "File or Directory not found" in error_msg:
                        self.log_output("   ❌ Path not found - check path formatting")
                    else:
                        self.log_output(f"   ⚠️  {error_msg}")
            
            # Step 2: Set permissions
            self.log_output("\n2. Setting maximum permissions...")
            
            permission_commands = [
                f'icacls "{file_path_fixed}" /inheritance:r',  # Remove inheritance
                f'icacls "{file_path_fixed}" /grant:r *S-1-5-32-544:F',  # Administrators
                f'icacls "{file_path_fixed}" /grant:r *S-1-5-18:F',       # SYSTEM
                f'icacls "{file_path_fixed}" /grant:r *S-1-5-32-545:RX',  # Users
            ]
            
            for cmd in permission_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_output(f"   ✅ {cmd.split()[0]} successful")
                else:
                    self.log_output(f"   ⚠️  {cmd.split()[0]}: {result.stderr.strip()}")
            
            self.log_output("\n🎉 Permission elevation process completed!")
            self.update_status("Process completed - check output for details")
            
            # Show final permissions
            self.log_output("\n📋 Final permissions:")
            self.show_current_permissions(file_path)
            
        except Exception as e:
            self.log_output(f"❌ Unexpected error: {str(e)}")
            self.update_status("Error occurred during permission elevation")
    
    def check_permissions(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
        
        self.clear_output()
        self.update_status("Checking current permissions...")
        self.show_current_permissions(file_path)
    
    def show_current_permissions(self, file_path):
        try:
            self.log_output(f"📊 Permission report for: {file_path}")
            self.log_output("=" * 50)
            
            # Get file info
            file_stats = os.stat(file_path)
            self.log_output(f"File Size: {file_stats.st_size} bytes")
            self.log_output(f"Modified: {file_stats.st_mtime}")
            
            # Get detailed permissions
            result = subprocess.run(f'icacls "{file_path}"', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_output("\nCurrent ACL:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log_output(f"  {line}")
            else:
                self.log_output(f"❌ Error reading permissions: {result.stderr}")
                
            self.update_status("Permission check completed")
            
        except Exception as e:
            self.log_output(f"❌ Error checking permissions: {str(e)}")
    
    def run(self):
        self.root.mainloop()

def main():
    # Check if we should run GUI or CLI
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Run in CLI mode
        print("Running in CLI mode...")
        # You can add CLI functionality here
    else:
        # Run GUI
        app = PermissionElevatorGUI()
        app.run()

if __name__ == "__main__":
    main()