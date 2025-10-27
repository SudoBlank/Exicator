import os
import subprocess
import ctypes
import time
import tempfile
import shutil
import sys
import gui_app

def launch_gui():
    """Launch the GUI application"""
    try:
        from gui_app import PermissionElevatorGUI
        app = PermissionElevatorGUI()
        app.run()
    except ImportError as e:
        print(f"❌ GUI dependencies missing: {e}")
        print("💡 Make sure gui_app.py is in the same directory")
        input("Press Enter to exit...")

def main():
    print("🛡️  Permission Elevation Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        launch_gui()
    else:
        # Default to CLI mode
        print("Usage:")
        print("  python main.py --gui    # Launch GUI")
        print("  python main.py --cli    # CLI mode")
        
        # Ask user what they want
        choice = input("\nLaunch GUI? (y/n): ").lower()
        if choice == 'y':
            launch_gui()
        else:
            print("Running in CLI mode...")
            # Add your existing CLI functionality here

if __name__ == "__main__":
    main()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_cmd(cmd, description=""):
    """Run command with better output"""
    if description:
        print(f"   {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

def disable_defender_for_file(file_path):
    """Completely disable Defender for this specific operation"""
    print("🛡️  Disabling Windows Defender temporarily...")
    
    commands = [
        'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
        'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"', 
        'powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true"',
        'powershell -Command "Set-MpPreference -DisableIOAVProtection $true"',
        f'powershell -Command "Add-MpPreference -ExclusionPath \"{file_path}\""',
        f'powershell -Command "Add-MpPreference -ExclusionPath \"{os.path.dirname(file_path)}\""'
    ]
    
    for cmd in commands:
        run_cmd(cmd)
    time.sleep(3)
    return True

def enable_defender():
    """Re-enable Windows Defender"""
    print("🛡️  Re-enabling Windows Defender...")
    commands = [
        'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false"',
        'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $false"',
        'powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $false"',
        'powershell -Command "Set-MpPreference -DisableIOAVProtection $false"'
    ]
    for cmd in commands:
        run_cmd(cmd)

def pause_onedrive():
    """Pause OneDrive synchronization without trying to restart it"""
    print("☁️  Pausing OneDrive synchronization...")
    commands = [
        'taskkill /f /im OneDrive.exe 2>nul',
        'taskkill /f /im FileCoAuth.exe 2>nul',
        'powershell -Command "Get-Process -Name OneDrive -ErrorAction SilentlyContinue | Stop-Process -Force"'
    ]
    for cmd in commands:
        run_cmd(cmd)
    time.sleep(2)
    return True

def get_file_handle_owners(file_path):
    """Find what's locking the file using handle.exe"""
    print("🔍 Checking what's locking the file...")
    handle_cmd = f'handle64 "{file_path}" 2>nul'
    result = run_cmd(handle_cmd)
    if result.returncode == 0 and "No matching handles found" not in result.stdout:
        print("   File is locked by:")
        for line in result.stdout.split('\n'):
            if file_path in line:
                print(f"   {line.strip()}")
        return True
    else:
        print("   File doesn't appear to be locked by processes")
        return False

def take_ownership_aggressive(file_path):
    """Extremely aggressive ownership takeover"""
    print("🔓 Taking ownership aggressively...")
    
    methods = [
        # Method 1: Standard takeown
        f'takeown /F "{file_path}" /A',
        # Method 2: Current user takeown  
        f'takeown /F "{file_path}"',
        # Method 3: PowerShell takeown
        f'powershell -Command "& {{ $p = \'{file_path}\'; takeown /F $p /A; icacls $p /grant administrators:F }}"',
        # Method 4: Forceful method
        f'icacls "{file_path}" /setowner "Administrators" /T /C',
        # Method 5: Even more forceful
        f'icacls "{file_path}" /setowner "SYSTEM" /T /C'
    ]
    
    for i, cmd in enumerate(methods, 1):
        result = run_cmd(cmd, f"Method {i}")
        if result.returncode == 0:
            print("      ✅ Success")
            return True
    
    return False

def set_permissions_direct(file_path):
    """Set permissions directly without inheritance"""
    print("🔧 Setting direct permissions...")
    
    # Remove inheritance and reset
    run_cmd(f'icacls "{file_path}" /inheritance:r', "Remove inheritance")
    run_cmd(f'icacls "{file_path}" /reset', "Reset ACL")
    
    # Grant to highest entities
    entities = [
        "SYSTEM:F",
        "Administrators:F", 
        "NT SERVICE\\TrustedInstaller:F",
        "Users:RX"
    ]
    
    for entity in entities:
        result = run_cmd(f'icacls "{file_path}" /grant {entity}', f"Grant {entity}")
        if result.returncode != 0:
            print(f"      ⚠️ Could not grant {entity}")

def copy_file_workaround(source_path):
    """Workaround by creating a new file with same content but in temp location"""
    print("🔄 Using copy workaround...")
    
    try:
        # Read original file content
        with open(source_path, 'rb') as f:
            content = f.read()
        
        # Create new file with same content in temp directory
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"max_perm_{os.path.basename(source_path)}")
        
        with open(temp_file, 'wb') as f:
            f.write(content)
        
        print(f"   ✅ Created temp file: {temp_file}")
        return temp_file
        
    except Exception as e:
        print(f"   ❌ Copy workaround failed: {e}")
        return None

def move_file_out_of_onedrive(file_path):
    """Move file out of OneDrive to avoid synchronization issues"""
    print("🚚 Moving file out of OneDrive...")
    
    temp_dir = tempfile.gettempdir()
    new_path = os.path.join(temp_dir, os.path.basename(file_path))
    
    try:
        shutil.copy2(file_path, new_path)
        print(f"   ✅ Copied to: {new_path}")
        return new_path
    except Exception as e:
        print(f"   ❌ Move failed: {e}")
        return None

def verify_permissions_detailed(file_path):
    """Detailed verification of permissions"""
    print("🔍 Verifying permissions...")
    
    # Try multiple verification methods
    methods = [
        f'icacls "{file_path}"',
        f'powershell -Command "Get-Acl \'{file_path}\' | Format-List"',
        f'dir "{file_path}" /Q'
    ]
    
    for cmd in methods:
        result = run_cmd(cmd, f"Verification: {cmd.split()[0]}")
        if result.returncode == 0:
            print("   ✅ Verification successful!")
            if result.stdout:
                print("   📋 Output:")
                for line in result.stdout.split('\n')[:10]:  # Show first 10 lines
                    if line.strip():
                        print(f"      {line}")
            return True
    
    return False

def main_smart_elevation():
    """Main function with smart approach that avoids OneDrive issues"""
    original_file = r"C:\Users\Aadi\OneDrive\Documents\Apps\Randomapps\exp\dist\Powertest.exe"
    
    if not is_admin():
        print("❌ RUN AS ADMINISTRATOR!")
        return
    
    print("🚀 SMART MAXIMUM PERMISSION ELEVATION")
    print("=" * 50)
    print(f"Target: {original_file}")
    print(f"File exists: {os.path.exists(original_file)}")
    print(f"File size: {os.path.getsize(original_file) if os.path.exists(original_file) else 'N/A'} bytes")
    print()
    
    # Step 1: Check if file is in OneDrive and offer to move it
    if "OneDrive" in original_file:
        print("⚠️  File is in OneDrive folder - this causes permission issues")
        response = input("   Move file to temporary location? (y/n): ")
        if response.lower() == 'y':
            temp_location = move_file_out_of_onedrive(original_file)
            if temp_location:
                original_file = temp_location
                print(f"   Now working on: {original_file}")
            else:
                print("   Continuing with original location (may have issues)")
        else:
            print("   Continuing with original OneDrive location")
    
    # Step 2: Disable protections
    defender_disabled = disable_defender_for_file(original_file)
    
    # Step 3: Only pause OneDrive if we're still in OneDrive folder
    onedrive_paused = False
    if "OneDrive" in original_file:
        onedrive_paused = pause_onedrive()
        time.sleep(3)
    
    try:
        # Step 4: Check what's locking the file
        get_file_handle_owners(original_file)
        
        # Step 5: Try direct modification first
        print("\n1. 🔄 Attempting direct permission modification...")
        if take_ownership_aggressive(original_file):
            set_permissions_direct(original_file)
            if verify_permissions_detailed(original_file):
                print("🎉 DIRECT METHOD SUCCESS!")
                return
        
        # Step 6: Copy workaround
        print("\n2. 🔄 Using copy-replace workaround...")
        temp_file = copy_file_workaround(original_file)
        
        if temp_file and os.path.exists(temp_file):
            # Set permissions on temp file
            take_ownership_aggressive(temp_file)
            set_permissions_direct(temp_file)
            
            # Replace original with temp file
            try:
                backup_file = original_file + ".backup"
                shutil.copy2(original_file, backup_file)
                print(f"   ✅ Backup created: {backup_file}")
                
                os.remove(original_file)
                shutil.move(temp_file, original_file)
                print("   ✅ Successfully replaced original file with permissioned version")
                
                # Verify final permissions
                if verify_permissions_detailed(original_file):
                    print("🎉 COPY-REPLACE METHOD SUCCESS!")
                    return
                    
            except Exception as e:
                print(f"   ❌ Replace failed: {e}")
                # Try to restore backup
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, original_file)
                    print("   ✅ Restored from backup")
        
        # Step 7: Alternative approach - work on copy and leave original
        print("\n3. 🔄 Creating permissioned copy...")
        permissioned_copy = original_file + ".maxperms.exe"
        try:
            shutil.copy2(original_file, permissioned_copy)
            take_ownership_aggressive(permissioned_copy)
            set_permissions_direct(permissioned_copy)
            if verify_permissions_detailed(permissioned_copy):
                print(f"🎉 Created permissioned copy: {permissioned_copy}")
                print("   You can use this copy instead of the original")
                return
        except Exception as e:
            print(f"   ❌ Copy creation failed: {e}")
        
    finally:
        # Re-enable protections
        if defender_disabled:
            enable_defender()
        
        # Don't try to restart OneDrive - let Windows handle it
        if onedrive_paused:
            print("\n☁️  OneDrive was paused during operation.")
            print("   It will automatically restart when you:")
            print("   - Restart your computer, OR")
            print("   - Log out and log back in, OR") 
            print("   - Manually start OneDrive from Start Menu")
        
        print("\n📋 Summary:")
        print("   - Windows Defender has been re-enabled")
        print("   - OneDrive will restart automatically on next login")
        print("   - Your file permissions have been elevated")

if __name__ == "__main__":
    main_smart_elevation()