import json
import os
import sys
import subprocess
import platform
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_done = False
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "version": "1.0.0",
            "author": "PrivilegeElevator User",
            "auto_setup": True,
            "paths": {
                "python_executable": "auto",
                "psexec_path": "auto",
                "project_directory": "auto",
                "temp_directory": "auto"
            },
            "security": {
                "require_admin": True,
                "max_integrity_level": "System",
                "enable_debug_privilege": True,
                "safe_mode": False
            },
            "tests": {
                "enable_sam_tests": True,
                "enable_registry_tests": True,
                "enable_process_tests": True,
                "enable_file_tests": True,
                "enable_network_tests": True,
                "test_timeout_seconds": 10,
                "max_process_scan": 50
            },
            "gui": {
                "theme": "dark",
                "show_live_stats": True,
                "auto_export_results": False,
                "results_directory": "results"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with default config
                    return self.merge_configs(default_config, user_config)
            except Exception as e:
                print(f"⚠️  Config load error: {e}, using defaults")
                return default_config
        else:
            return default_config
    
    def merge_configs(self, default, user):
        """Merge user config with defaults"""
        merged = default.copy()
        
        for key, value in user.items():
            if isinstance(value, dict) and key in merged:
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def auto_detect_paths(self):
        """Auto-detect system paths"""
        print("🔍 Auto-detecting system paths...")
        
        # Python detection
        python_path = self.config['paths']['python_executable']
        if python_path == "auto":
            python_candidates = [
                sys.executable,  # Current Python
                r"C:\Python313\python.exe",
                r"C:\Python312\python.exe", 
                r"C:\Python311\python.exe",
                r"C:\Program Files\Python313\python.exe",
                r"C:\Users\{}\AppData\Local\Programs\Python\Python313\python.exe".format(os.getenv('USERNAME')),
            ]
            
            for candidate in python_candidates:
                if os.path.exists(candidate):
                    self.config['paths']['python_executable'] = candidate
                    print(f"✅ Python found: {candidate}")
                    break
            else:
                # Use where command
                try:
                    result = subprocess.run('where python', shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.config['paths']['python_executable'] = result.stdout.strip().split('\n')[0]
                        print(f"✅ Python found via 'where': {self.config['paths']['python_executable']}")
                except:
                    pass
        
        # PsExec detection
        psexec_path = self.config['paths']['psexec_path']
        if psexec_path == "auto":
            psexec_candidates = [
                r"C:\Tools\PsExec64.exe",
                r"C:\Tools\PsExec.exe",
                os.path.join(os.getcwd(), "PsExec64.exe"),
                os.path.join(os.path.dirname(os.getcwd()), "Tools", "PsExec64.exe"),
            ]
            
            for candidate in psexec_candidates:
                if os.path.exists(candidate):
                    self.config['paths']['psexec_path'] = candidate
                    print(f"✅ PsExec found: {candidate}")
                    break
            else:
                print("⚠️  PsExec not found - download from Microsoft Sysinternals")
        
        # Project directory
        if self.config['paths']['project_directory'] == "auto":
            self.config['paths']['project_directory'] = os.getcwd()
        
        # Temp directory
        if self.config['paths']['temp_directory'] == "auto":
            self.config['paths']['temp_directory'] = os.path.join(os.getenv('TEMP'), "PrivilegeElevator")
            os.makedirs(self.config['paths']['temp_directory'], exist_ok=True)
        
        self.save_config()
        return True
    
    def validate_system(self):
        """Validate system requirements"""
        print("🔧 Validating system requirements...")
        
        issues = []
        
        # Check Windows version
        win_version = platform.version()
        if not (platform.system() == "Windows" and (platform.release() in ["10", "11"] or "10." in win_version or "11." in win_version)):
            issues.append("❌ Requires Windows 10 or 11")
        
        # Check architecture
        if platform.architecture()[0] != "64bit":
            issues.append("⚠️  64-bit Windows recommended for full functionality")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            issues.append(f"❌ Python 3.8+ required (current: {python_version.major}.{python_version.minor})")
        
        # Check admin privileges
        if self.config['security']['require_admin']:
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    issues.append("⚠️  Administrator privileges recommended")
            except:
                issues.append("⚠️  Could not verify admin privileges")
        
        if issues:
            print("System validation issues:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ System validation passed!")
        
        return len(issues) == 0
    
    def setup_environment(self):
        """Setup the environment for first-time users"""
        print("🚀 Setting up PrivilegeElevator environment...")
        
        # Create required directories
        os.makedirs("results", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Auto-detect paths
        self.auto_detect_paths()
        
        # Validate system
        self.validate_system()
        
        # Check for required packages
        required_packages = ['psutil']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"📦 Installing missing packages: {', '.join(missing_packages)}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
                print("✅ Packages installed successfully!")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install packages. Please run: pip install {' '.join(missing_packages)}")
        
        self.setup_done = True
        self.save_config()
        print("🎉 Setup completed successfully!")
        return True
    
    def get(self, key, default=None):
        """Get config value using dot notation"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
    
    def set(self, key, value):
        """Set config value using dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config()

# Global config instance
config = ConfigManager()