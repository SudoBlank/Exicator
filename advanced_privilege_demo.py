import os
import subprocess
import ctypes
import winreg
import psutil
import time
from datetime import datetime

class AdvancedPrivilegeDemonstrator:
    def __init__(self):
        self.results = []
        self.is_admin = self.check_admin()
        self.start_time = time.time()
    
    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def log_result(self, test_name, success, details=""):
        status = "✅" if success else "❌"
        self.results.append(f"{status} {test_name}: {details}")
        return success
    
    def run_command_with_timeout(self, command, timeout=10):
        """Run a command with timeout to prevent hanging"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            return None  # Signal timeout
        except Exception as e:
            return type('obj', (object,), {'returncode': -1, 'stdout': '', 'stderr': str(e)})
    
    def demonstrate_restricted_operations(self):
        """Test operations that require SYSTEM or higher privileges - FIXED VERSION"""
        print("🛡️  ADVANCED PRIVILEGE DEMONSTRATION (FAST VERSION)")
        print("=" * 60)
        print(f"Running as Admin: {self.is_admin}")
        print(f"Start Time: {datetime.now()}")
        print("Using faster, non-blocking tests...")
        print()
        
        # Test 1: Quick SAM Access Tests
        self.test_sam_access_quick()
        
        # Test 2: Process Access
        self.test_process_access_quick()
        
        # Test 3: Registry Access
        self.test_registry_access_quick()
        
        # Test 4: File System Access
        self.test_file_system_access()
        
        # Test 5: Security Information
        self.test_security_info_quick()
        
        # Test 6: Quick TrustedInstaller Tests
        self.test_trustedinstaller_quick()
        
        # Display Results
        self.display_advanced_results()
    
    def test_sam_access_quick(self):
        """Quick SAM access tests without blocking operations"""
        print("🔐 QUICK SAM ACCESS TESTS")
        print("-" * 30)
        
        sam_tests = [
            ("Check SAM Registry Exists", 'reg query "HKLM\\SAM" /f "" 2>&1 | find "HKEY"'),
            ("Check SAM File Exists", 'dir "C:\\Windows\\System32\\config\\SAM" 2>&1 | find "SAM"'),
            ("Check SECURITY Registry", 'reg query "HKLM\\SECURITY" /f "" 2>&1 | find "HKEY"'),
        ]
        
        for test_name, command in sam_tests:
            try:
                result = self.run_command_with_timeout(command, 5)
                if result is None:
                    print(f"  ⏱️  {test_name}: Timed out")
                    self.log_result(test_name, False, "Timed out")
                elif result.returncode == 0:
                    print(f"  ✅ {test_name}: Access granted")
                    self.log_result(test_name, True, "Access granted")
                else:
                    print(f"  ❌ {test_name}: Access denied")
                    self.log_result(test_name, False, "Access denied")
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")
                self.log_result(test_name, False, str(e))
    
    def test_process_access_quick(self):
        """Quick process access tests"""
        print("\n⚙️  PROCESS ACCESS")
        print("-" * 30)
        
        try:
            # Get system processes quickly
            system_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    if 'SYSTEM' in str(proc.info['username']):
                        system_procs.append(proc.info)
                        if len(system_procs) >= 10:  # Limit to 10 for speed
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print(f"  ✅ Found {len(system_procs)} SYSTEM processes")
            self.log_result("System Process Enumeration", True, f"Found {len(system_procs)} processes")
            
            # Test access to specific critical processes
            critical_processes = [
                ("LSASS", "lsass.exe"),
                ("CSRSS", "csrss.exe"), 
                ("Winlogon", "winlogon.exe"),
                ("Services", "services.exe"),
            ]
            
            for proc_name, proc_exe in critical_processes:
                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        if proc.info['name'] and proc_exe in proc.info['name'].lower():
                            # Try minimal query access
                            result = self.run_command_with_timeout(f'tasklist /fi "PID eq {proc.info["pid"]}"', 3)
                            if result and result.returncode == 0:
                                print(f"  ✅ Can query {proc_name} (PID: {proc.info['pid']})")
                                self.log_result(f"Query {proc_name}", True, f"PID {proc.info['pid']}")
                            else:
                                print(f"  ❌ Cannot query {proc_name}")
                                self.log_result(f"Query {proc_name}", False, "Access denied")
                            break
                except Exception as e:
                    print(f"  ❌ {proc_name} test failed: {str(e)}")
                    self.log_result(f"Query {proc_name}", False, str(e))
                    
        except Exception as e:
            print(f"  ❌ Process tests failed: {str(e)}")
            self.log_result("Process Tests", False, str(e))
    
    def test_registry_access_quick(self):
        """Quick registry access tests"""
        print("\n🔐 REGISTRY ACCESS")
        print("-" * 30)
        
        registry_tests = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion", "Windows Version"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control", "System Control"),
            (winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System", "Hardware Info"),
            (winreg.HKEY_LOCAL_MACHINE, r"SAM\SAM", "SAM Registry"),  # This often fails
        ]
        
        for hive, path, description in registry_tests:
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    # Try to read first value
                    try:
                        value_name, value_data, value_type = winreg.EnumValue(key, 0)
                        print(f"  ✅ {description}: Read access")
                        self.log_result(f"Registry: {description}", True, "Read access")
                    except:
                        print(f"  ✅ {description}: Key access (no values)")
                        self.log_result(f"Registry: {description}", True, "Key access")
            except Exception as e:
                if "Access is denied" in str(e):
                    print(f"  ❌ {description}: Access denied")
                    self.log_result(f"Registry: {description}", False, "Access denied")
                else:
                    print(f"  ❌ {description}: {str(e)}")
                    self.log_result(f"Registry: {description}", False, str(e))
    
    def test_file_system_access(self):
        """Test file system access"""
        print("\n📁 FILE SYSTEM ACCESS")
        print("-" * 30)
        
        file_tests = [
            (r"C:\Windows\System32\config", "System32 config directory"),
            (r"C:\Windows\System32\drivers\etc\hosts", "System hosts file"),
            (r"C:\Program Files", "Program Files directory"),
            (r"C:\Windows\System32\cmd.exe", "System command processor"),
        ]
        
        for path, description in file_tests:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        # Try to read file
                        with open(path, 'rb') as f:
                            header = f.read(100)  # Read just the header
                        print(f"  ✅ {description}: Can read file ({len(header)} bytes)")
                        self.log_result(f"File: {description}", True, f"Read {len(header)} bytes")
                    else:
                        # Try to list directory
                        files = os.listdir(path)
                        print(f"  ✅ {description}: Can list {len(files)} items")
                        self.log_result(f"Directory: {description}", True, f"{len(files)} items")
                else:
                    print(f"  ❌ {description}: Path not found")
                    self.log_result(f"Path: {description}", False, "Not found")
            except Exception as e:
                print(f"  ❌ {description}: {str(e)}")
                self.log_result(f"Access: {description}", False, str(e))
    
    def test_security_info_quick(self):
        """Quick security information tests"""
        print("\n🔒 SECURITY INFORMATION")
        print("-" * 30)
        
        security_tests = [
            ("Current User", 'whoami'),
            ("User Privileges", 'whoami /priv | find /c ":"'),
            ("Group Membership", 'whoami /groups | find /c "Group"'),
            ("Integrity Level", 'whoami /groups | findstr Mandatory'),
        ]
        
        for test_name, command in security_tests:
            try:
                result = self.run_command_with_timeout(command, 5)
                if result and result.returncode == 0:
                    output = result.stdout.strip()
                    print(f"  ✅ {test_name}: {output}")
                    self.log_result(test_name, True, output)
                else:
                    print(f"  ❌ {test_name}: Failed")
                    self.log_result(test_name, False, "Failed")
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")
                self.log_result(test_name, False, str(e))
    
    def test_trustedinstaller_quick(self):
        """Quick TrustedInstaller tests"""
        print("\n👑 TRUSTEDINSTALLER OPERATIONS")
        print("-" * 30)
        
        ti_tests = [
            ("List WinSxS", 'dir "C:\\Windows\\WinSxS" 2>&1 | find "File(s)"'),
            ("Check System32 Ownership", 'icacls "C:\\Windows\\System32\\kernel32.dll" 2>&1 | find "TrustedInstaller"'),
            ("Try System32 Write", 'echo test > "C:\\Windows\\System32\\test_temp.txt" 2>&1 && del "C:\\Windows\\System32\\test_temp.txt" && echo success'),
        ]
        
        for test_name, command in ti_tests:
            try:
                result = self.run_command_with_timeout(command, 5)
                if result is None:
                    print(f"  ⏱️  {test_name}: Timed out")
                    self.log_result(test_name, False, "Timed out")
                elif result.returncode == 0:
                    if "success" in result.stdout.lower():
                        print(f"  ✅ {test_name}: Success (unexpected!)")
                        self.log_result(test_name, True, "Unexpected success!")
                    else:
                        print(f"  ✅ {test_name}: Access granted")
                        self.log_result(test_name, True, "Access granted")
                else:
                    if "Access is denied" in result.stdout or "Access is denied" in result.stderr:
                        print(f"  ❌ {test_name}: Access denied (requires TrustedInstaller)")
                        self.log_result(test_name, False, "Requires TrustedInstaller")
                    else:
                        print(f"  ❌ {test_name}: Failed")
                        self.log_result(test_name, False, "Failed")
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")
                self.log_result(test_name, False, str(e))
    
    def display_advanced_results(self):
        """Display summary of advanced tests"""
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 60)
        print("📊 ADVANCED PRIVILEGE SUMMARY")
        print("=" * 60)
        
        successful = sum(1 for result in self.results if "✅" in result)
        total = len(self.results)
        
        print(f"Tests Completed: {successful}/{total} ({successful/total*100:.1f}%)")
        print(f"Time Elapsed: {elapsed:.1f} seconds")
        print()
        
        for result in self.results:
            print(result)
        
        print("\n💡 INTERPRETATION:")
        if successful == total:
            print("   🎉 SYSTEM-LEVEL ACCESS - You have exceptional privileges!")
        elif successful > total * 0.7:
            print("   ⚡ HIGH DEBUG ACCESS - Most protected operations work!")
        elif successful > total * 0.4:
            print("   🔧 ADMINISTRATOR ACCESS - Standard admin privileges")
        else:
            print("   🔒 LIMITED ACCESS - Basic user privileges")

def main():
    print("🚀 FAST ADVANCED PRIVILEGE DEMONSTRATION")
    print("This version uses quick, non-blocking tests.")
    print()
    
    input("Press Enter to start fast demonstration...")
    print()
    
    demo = AdvancedPrivilegeDemonstrator()
    demo.demonstrate_restricted_operations()
    
    print("\n" + "=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()