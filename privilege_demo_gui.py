import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import subprocess
import os
import ctypes
import psutil
import winreg
from datetime import datetime

class PrivilegeDemoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ System Privilege Analyzer")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Style configuration
        self.setup_styles()
        self.setup_ui()
        
        self.is_running = False
        self.results = []
        self.start_time = None
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Custom.TFrame', background='#2b2b2b')
        style.configure('Custom.TLabel', background='#2b2b2b', foreground='white', font=('Segoe UI', 10))
        style.configure('Title.TLabel', background='#2b2b2b', foreground='#00ff00', font=('Segoe UI', 16, 'bold'))
        style.configure('Success.TLabel', background='#2b2b2b', foreground='#00ff00')
        style.configure('Warning.TLabel', background='#2b2b2b', foreground='#ffff00')
        style.configure('Error.TLabel', background='#2b2b2b', foreground='#ff4444')
        
        # Button styles
        style.configure('Accent.TButton', background='#007acc', foreground='white', font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton', background=[('active', '#005a9e')])
        
        # Progress bar style
        style.configure('Custom.Horizontal.TProgressbar', background='#007acc', troughcolor='#3c3c3c')
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Custom.TFrame', padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🛡️ SYSTEM PRIVILEGE ANALYZER", style='Title.TLabel')
        title_label.pack()
        
        desc_label = ttk.Label(header_frame, 
                              text="Comprehensive analysis of your system access privileges and security context",
                              style='Custom.TLabel')
        desc_label.pack(pady=(5, 0))
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 REAL-TIME STATISTICS", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Stats grid
        self.stats_vars = {
            'privilege_level': tk.StringVar(value="🔍 Analyzing..."),
            'integrity_level': tk.StringVar(value="Unknown"),
            'tests_completed': tk.StringVar(value="0/0"),
            'success_rate': tk.StringVar(value="0%"),
            'elapsed_time': tk.StringVar(value="0.0s")
        }
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        stats_data = [
            ("Privilege Level", "privilege_level"),
            ("Integrity Level", "integrity_level"), 
            ("Tests Completed", "tests_completed"),
            ("Success Rate", "success_rate"),
            ("Elapsed Time", "elapsed_time")
        ]
        
        for i, (label, key) in enumerate(stats_data):
            ttk.Label(stats_grid, text=f"{label}:", style='Custom.TLabel').grid(row=i//3, column=(i%3)*2, sticky=tk.W, padx=(0, 5))
            ttk.Label(stats_grid, textvariable=self.stats_vars[key], style='Custom.TLabel', font=('Segoe UI', 9, 'bold')).grid(row=i//3, column=(i%3)*2+1, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        self.start_btn = ttk.Button(control_frame, text="🚀 Start Privilege Analysis", 
                                   command=self.start_analysis, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_btn = ttk.Button(control_frame, text="💾 Export Results", 
                                    command=self.export_results, state='disabled')
        self.export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="🗑️ Clear", command=self.clear_output).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, style='Custom.Horizontal.TProgressbar', mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="🔍 PRIVILEGE ANALYSIS RESULTS", padding="5")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for organized results
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(summary_frame, text="📊 Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=15, width=80, 
                                                     font=('Consolas', 9), bg='#1e1e1e', fg='white',
                                                     insertbackground='white')
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Detailed tab
        detailed_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(detailed_frame, text="📋 Detailed")
        
        self.detailed_text = scrolledtext.ScrolledText(detailed_frame, height=15, width=80,
                                                      font=('Consolas', 9), bg='#1e1e1e', fg='white',
                                                      insertbackground='white')
        self.detailed_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to start privilege analysis")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, style='Custom.TLabel')
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def log_output(self, message, widget='summary'):
        """Add message to output widget"""
        text_widget = self.summary_text if widget == 'summary' else self.detailed_text
        
        # Color coding
        if '✅' in message:
            tag = 'success'
        elif '❌' in message:
            tag = 'error'
        elif '⚠️' in message:
            tag = 'warning'
        else:
            tag = 'normal'
        
        text_widget.configure(state='normal')
        text_widget.insert(tk.END, message + '\n', tag)
        text_widget.see(tk.END)
        text_widget.configure(state='disabled')
        
        self.root.update()
    
    def clear_output(self):
        """Clear all output widgets"""
        for widget in [self.summary_text, self.detailed_text]:
            widget.configure(state='normal')
            widget.delete(1.0, tk.END)
            widget.configure(state='disabled')
        
        self.results = []
        self.export_btn.config(state='disabled')
        self.update_stats(0, 0)
    
    def start_analysis(self):
        """Start the privilege analysis in a separate thread"""
        if self.is_running:
            return
        
        self.clear_output()
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.export_btn.config(state='disabled')
        self.start_time = time.time()
        self.progress.config(mode='indeterminate')
        self.progress.start()
        
        # Configure text tags for color
        for widget in [self.summary_text, self.detailed_text]:
            widget.configure(state='normal')
            widget.tag_config('success', foreground='#00ff00')
            widget.tag_config('error', foreground='#ff4444')
            widget.tag_config('warning', foreground='#ffff00')
            widget.tag_config('normal', foreground='#ffffff')
            widget.configure(state='disabled')
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_privilege_analysis)
        thread.daemon = True
        thread.start()
    
    def run_privilege_analysis(self):
        """Run the comprehensive privilege analysis"""
        try:
            self.status_var.set("Starting privilege analysis...")
            self.log_output("🛡️ SYSTEM PRIVILEGE ANALYSIS STARTED")
            self.log_output("=" * 60)
            self.log_output(f"Start Time: {datetime.now()}")
            self.log_output("")
            
            # Run all test categories
            test_categories = [
                ("🔐 Security Context", self.test_security_context),
                ("📁 File System Access", self.test_file_system),
                ("🔐 Registry Access", self.test_registry_access),
                ("⚙️ Process Management", self.test_process_management),
                ("🌐 Network Information", self.test_network_info),
                ("👑 TrustedInstaller Operations", self.test_trustedinstaller_ops)
            ]
            
            total_tests = 0
            completed_tests = 0
            
            for category_name, test_func in test_categories:
                self.status_var.set(f"Running: {category_name}")
                self.log_output(f"\n{category_name}")
                self.log_output("-" * 40)
                
                try:
                    success_count, total_count = test_func()
                    completed_tests += success_count
                    total_tests += total_count
                    
                    # Update progress
                    if total_tests > 0:
                        self.update_stats(completed_tests, total_tests)
                    
                except Exception as e:
                    self.log_output(f"❌ Error in {category_name}: {str(e)}")
            
            # Final summary
            self.complete_analysis(completed_tests, total_tests)
            
        except Exception as e:
            self.log_output(f"❌ Analysis failed: {str(e)}")
            self.status_var.set("Analysis failed")
        finally:
            self.is_running = False
            self.progress.stop()
            self.start_btn.config(state='normal')
            self.export_btn.config(state='normal')
    
    def test_security_context(self):
        """Test security context and privileges"""
        success = 0
        total = 0
        
        try:
            # Current user
            result = subprocess.run('whoami', shell=True, capture_output=True, text=True)
            user = result.stdout.strip()
            self.log_output(f"✅ Current User: {user}")
            self.log_output(f"   (Running as SYSTEM)", 'detailed')
            success += 1
            total += 1
            
            # Integrity level
            result = subprocess.run('whoami /groups | findstr Mandatory', shell=True, capture_output=True, text=True)
            if 'System Mandatory Level' in result.stdout:
                self.log_output("✅ Integrity Level: System Mandatory Level (Highest)")
                self.stats_vars['integrity_level'].set("System (Highest)")
                success += 1
            else:
                self.log_output("❌ Integrity Level: Not System Level")
            total += 1
            
            # Privileges
            result = subprocess.run('whoami /priv', shell=True, capture_output=True, text=True)
            privilege_count = result.stdout.count('Enabled')
            self.log_output(f"✅ Enabled Privileges: {privilege_count}")
            self.log_output(f"   {privilege_count} privileges enabled", 'detailed')
            success += 1
            total += 1
            
        except Exception as e:
            self.log_output(f"❌ Security Context Error: {str(e)}")
            total += 3
        
        return success, total
    
    def test_file_system(self):
        """Test file system access"""
        success = 0
        total = 0
        
        file_tests = [
            (r"C:\Windows\System32\config", "System32 config directory"),
            (r"C:\Windows\System32\drivers\etc\hosts", "System hosts file"),
            (r"C:\Program Files", "Program Files directory"),
            (r"C:\Windows\System32\kernel32.dll", "System DLL access"),
        ]
        
        for path, description in file_tests:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        with open(path, 'rb') as f:
                            header = f.read(100)
                        self.log_output(f"✅ {description}: Read access ({len(header)} bytes)")
                        self.log_output(f"   Can read system file: {path}", 'detailed')
                    else:
                        files = os.listdir(path)
                        self.log_output(f"✅ {description}: List access ({len(files)} items)")
                        self.log_output(f"   Can list directory: {path}", 'detailed')
                    success += 1
                else:
                    self.log_output(f"❌ {description}: Not found")
                total += 1
            except Exception as e:
                self.log_output(f"❌ {description}: {str(e)}")
                total += 1
        
        return success, total
    
    def test_registry_access(self):
        """Test registry access"""
        success = 0
        total = 0
        
        registry_tests = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion", "Windows Version"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control", "System Control"),
            (winreg.HKEY_LOCAL_MACHINE, r"SAM\SAM", "SAM Database"),
            (winreg.HKEY_LOCAL_MACHINE, r"SECURITY", "Security Database"),
        ]
        
        for hive, path, description in registry_tests:
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    self.log_output(f"✅ {description}: Registry access")
                    self.log_output(f"   Can access: HKLM\\{path}", 'detailed')
                    success += 1
            except Exception as e:
                if "Access is denied" in str(e):
                    self.log_output(f"❌ {description}: Access denied")
                else:
                    self.log_output(f"❌ {description}: {str(e)}")
            total += 1
        
        return success, total
    
    def test_process_management(self):
        """Test process management capabilities"""
        success = 0
        total = 0
        
        try:
            # System processes
            system_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    if 'SYSTEM' in str(proc.info['username']):
                        system_procs.append(proc.info)
                        if len(system_procs) >= 5:
                            break
                except:
                    continue
            
            self.log_output(f"✅ System Processes: Found {len(system_procs)}")
            self.log_output(f"   Can enumerate SYSTEM processes", 'detailed')
            success += 1
            total += 1
            
            # Critical process access
            critical_procs = ['lsass.exe', 'csrss.exe', 'winlogon.exe']
            for proc_name in critical_procs:
                found = False
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and proc_name in proc.info['name'].lower():
                        self.log_output(f"✅ Can access {proc_name} (PID: {proc.info['pid']})")
                        self.log_output(f"   Can query critical process: {proc_name}", 'detailed')
                        success += 1
                        found = True
                        break
                if not found:
                    self.log_output(f"❌ Cannot access {proc_name}")
                total += 1
                
        except Exception as e:
            self.log_output(f"❌ Process Management Error: {str(e)}")
            total += 4
        
        return success, total
    
    def test_network_info(self):
        """Test network information access"""
        success = 0
        total = 0
        
        try:
            # Network connections
            connections = psutil.net_connections()
            listening = [c for c in connections if c.status == 'LISTEN']
            self.log_output(f"✅ Network: {len(listening)} listening ports")
            self.log_output(f"   Can access network connection information", 'detailed')
            success += 1
            total += 1
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            self.log_output(f"✅ Network: {len(interfaces)} interfaces")
            self.log_output(f"   Can access network interface information", 'detailed')
            success += 1
            total += 1
            
        except Exception as e:
            self.log_output(f"❌ Network Info Error: {str(e)}")
            total += 2
        
        return success, total
    
    def test_trustedinstaller_ops(self):
        """Test TrustedInstaller-level operations"""
        success = 0
        total = 0
        
        ti_tests = [
            ('Write to System32', 'echo TEST > "C:\\Windows\\System32\\test_priv.txt" 2>nul && del "C:\\Windows\\System32\\test_priv.txt" && echo success'),
            ('List WinSxS', 'dir "C:\\Windows\\WinSxS" >nul 2>&1 && echo success'),
            ('Check Ownership', 'icacls "C:\\Windows\\System32\\kernel32.dll" | find "TrustedInstaller" >nul && echo success'),
        ]
        
        for test_name, command in ti_tests:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_output(f"✅ {test_name}: Success")
                    self.log_output(f"   Can perform TrustedInstaller operation", 'detailed')
                    success += 1
                else:
                    self.log_output(f"❌ {test_name}: Failed")
                total += 1
            except Exception as e:
                self.log_output(f"❌ {test_name}: {str(e)}")
                total += 1
        
        return success, total
    
    def update_stats(self, completed, total):
        """Update statistics display"""
        if total > 0:
            success_rate = (completed / total) * 100
            self.stats_vars['tests_completed'].set(f"{completed}/{total}")
            self.stats_vars['success_rate'].set(f"{success_rate:.1f}%")
            
            # Update privilege level based on success rate
            if success_rate >= 90:
                level = "SYSTEM Level 🎉"
                color = "#00ff00"
            elif success_rate >= 70:
                level = "High Admin ⚡"
                color = "#ffff00"
            elif success_rate >= 40:
                level = "Admin 🔧"
                color = "#ffaa00"
            else:
                level = "Limited 🔒"
                color = "#ff4444"
            
            self.stats_vars['privilege_level'].set(level)
            
            # Update progress bar
            self.progress.config(mode='determinate', maximum=total, value=completed)
        
        # Update elapsed time
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.stats_vars['elapsed_time'].set(f"{elapsed:.1f}s")
    
    def complete_analysis(self, completed, total):
        """Complete the analysis and show final results"""
        success_rate = (completed / total) * 100 if total > 0 else 0
        
        self.log_output("\n" + "=" * 60)
        self.log_output("📊 ANALYSIS COMPLETE")
        self.log_output("=" * 60)
        self.log_output(f"Final Success Rate: {success_rate:.1f}%")
        self.log_output(f"Tests Completed: {completed}/{total}")
        
        # Interpretation
        if success_rate >= 90:
            self.log_output("💡 INTERPRETATION: 🎉 SYSTEM-LEVEL ACCESS")
            self.log_output("   You have maximum system privileges!")
            self.status_var.set("Analysis Complete: SYSTEM Level Access Achieved!")
        elif success_rate >= 70:
            self.log_output("💡 INTERPRETATION: ⚡ HIGH ADMIN ACCESS")
            self.log_output("   Most protected operations work!")
            self.status_var.set("Analysis Complete: High Admin Access")
        elif success_rate >= 40:
            self.log_output("💡 INTERPRETATION: 🔧 ADMINISTRATOR ACCESS")
            self.log_output("   Standard administrator privileges")
            self.status_var.set("Analysis Complete: Administrator Access")
        else:
            self.log_output("💡 INTERPRETATION: 🔒 LIMITED ACCESS")
            self.log_output("   Basic user privileges")
            self.status_var.set("Analysis Complete: Limited Access")
        
        # Enable export
        self.export_btn.config(state='normal')
    
    def export_results(self):
        """Export results to a text file"""
        try:
            filename = f"privilege_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("SYSTEM PRIVILEGE ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Get summary text
                summary = self.summary_text.get(1.0, tk.END)
                f.write(summary)
                
                f.write("\n" + "=" * 50 + "\n")
                f.write("DETAILED RESULTS\n")
                f.write("=" * 50 + "\n\n")
                
                # Get detailed text
                detailed = self.detailed_text.get(1.0, tk.END)
                f.write(detailed)
            
            self.status_var.set(f"Results exported to: {filename}")
            self.log_output(f"💾 Results exported to: {filename}")
            
        except Exception as e:
            self.status_var.set(f"Export failed: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    # Check if running as admin
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    
    if not is_admin:
        print("⚠️  For best results, run this application as Administrator!")
        print("   Right-click and select 'Run as administrator'")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    app = PrivilegeDemoGUI()
    app.run()

if __name__ == "__main__":
    main()