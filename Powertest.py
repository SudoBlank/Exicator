import subprocess
import re
import time

# Dictionary of well-known SIDs with descriptions
KNOWN_SIDS = {
    "S-1-0-0": "Nobody - No security principal",
    "S-1-1-0": "Everyone - A group that includes all users",
    "S-1-2-0": "Local - Users who log on to terminals locally connected to the computer",
    "S-1-2-1": "Console Logon - Users who are logged on to the physical console",
    "S-1-3-0": "Creator Owner - A placeholder in an inheritable access control entry (ACE)",
    "S-1-5-1": "Dialup - Users who log on using a dial-up connection",
    "S-1-5-2": "Network - Users who log on across a network",
    "S-1-5-3": "Batch - Users who log on using a batch queue facility",
    "S-1-5-4": "Interactive - Users who log on for interactive operation",
    "S-1-5-6": "Service - A group for security principals that are services",
    "S-1-5-7": "Anonymous Logon - Users logged on anonymously",
    "S-1-5-9": "Enterprise Domain Controllers - A group that includes all domain controllers in a forest",
    "S-1-5-10": "Self - Represents the object itself",
    "S-1-5-11": "Authenticated Users - Includes all users whose identities were authenticated",
    "S-1-5-12": "Restricted Code - Code running in a restricted security context",
    "S-1-5-13": "Terminal Server User - Users who log on to a Terminal Server",
    "S-1-5-14": "Remote Interactive Logon - Users who log on remotely using Terminal Services",
    "S-1-5-18": "System (LocalSystem) - A service account that is used by the operating system",
    "S-1-5-19": "Local Service - A service account with limited privileges",
    "S-1-5-20": "Network Service - A service account with limited privileges for network access",
    "S-1-5-32-544": "BUILTIN\\Administrators - Administrators group",
    "S-1-5-32-545": "BUILTIN\\Users - Users group",
    "S-1-5-32-546": "BUILTIN\\Guests - Guests group",
    "S-1-5-32-547": "BUILTIN\\Power Users - Power Users group",
    "S-1-5-32-548": "BUILTIN\\Account Operators - Account Operators group",
    "S-1-5-32-549": "BUILTIN\\Server Operators - Server Operators group",
    "S-1-5-32-550": "BUILTIN\\Print Operators - Print Operators group",
    "S-1-5-32-551": "BUILTIN\\Backup Operators - Backup Operators group",
    "S-1-5-32-552": "BUILTIN\\Replicator - Replicator group",
    "S-1-5-32-555": "BUILTIN\\Remote Desktop Users - Remote Desktop Users group",
    "S-1-5-64-10": "NTLM Authentication - Used for NTLM authentication",
    "S-1-5-64-14": "SChannel Authentication - Used for SChannel authentication",
    "S-1-5-64-21": "Digest Authentication - Used for Digest authentication",
    "S-1-5-80-0": "NT SERVICES\\ALL SERVICES - Group for all service processes",
    "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464": "NT SERVICE\\TrustedInstaller - TrustedInstaller service",
    "S-1-5-113": "NT AUTHORITY\\Local account - Local account",
    "S-1-5-114": "NT AUTHORITY\\Local account and member of Administrators group",
    # Integrity Levels
    "S-1-16-0": "Untrusted Mandatory Level",
    "S-1-16-4096": "Low Mandatory Level",
    "S-1-16-8192": "Medium Mandatory Level",
    "S-1-16-8448": "Medium Plus Mandatory Level",
    "S-1-16-12288": "High Mandatory Level (Administrator)",
    "S-1-16-16384": "System Mandatory Level",
    "S-1-16-20480": "Protected Process Mandatory Level",
    "S-1-16-28672": "Secure Process Mandatory Level",
}

def parse_whoami_groups(output):
    """
    Parses the output of 'whoami /groups' into a list of dictionaries.
    """
    groups = []
    parsing = False
    pattern = re.compile(r'^(.+?)\s{2,}(Well-known group|Alias|Label|Group|Unknown SID type|SID)\s{2,}(S-1-[\d-]+|None)?\s{2,}(.+)$', re.IGNORECASE)
    
    for line in output.splitlines():
        if "=====" in line:
            parsing = True
            continue
        if parsing and line.strip():
            match = pattern.match(line)
            if match:
                group_name, type_, sid, attributes = match.groups()
                if sid is None:
                    sid = "None"
                desc = KNOWN_SIDS.get(sid.strip(), "Custom/Unknown SID")
                groups.append({
                    "Group Name": group_name.strip(),
                    "Type": type_.strip(),
                    "SID": sid.strip(),
                    "Description": desc,
                    "Attributes": attributes.strip()
                })
    return groups

def print_table(data, headers):
    """
    Prints a formatted ASCII table.
    """
    if not data:
        return
    
    # Calculate max widths
    widths = {header: len(header) for header in headers}
    for row in data:
        for header in headers:
            widths[header] = max(widths[header], len(str(row.get(header, ""))))
    
    # Print header
    print(" + " + " + ".join("-" * widths[h] for h in headers) + " + ")
    print(" | " + " | ".join(str(h).ljust(widths[h]) for h in headers) + " | ")
    print(" + " + " + ".join("-" * widths[h] for h in headers) + " + ")
    
    # Print rows
    for row in data:
        print(" | " + " | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers) + " | ")
    print(" + " + " + ".join("-" * widths[h] for h in headers) + " + ")

def get_summary(groups, principal):
    """
    Generates a summary of key privilege indicators.
    """
    summary = []
    
    # Integrity Level
    integrity = next((g for g in groups if g["Type"] == "Label"), None)
    integrity_level = integrity["Description"] if integrity else "Unknown"
    summary.append({"Indicator": "Integrity Level", "Value": integrity_level, "SID": integrity["SID"] if integrity else "N/A"})
    
    # Principal
    summary.append({"Indicator": "Security Principal", "Value": principal, "SID": "N/A"})  # Principal doesn't have SID in whoami
    
    # Check for Administrators group
    admin_group = next((g for g in groups if g["SID"] == "S-1-5-32-544"), None)
    is_admin = "Yes" if admin_group else "No"
    admin_enabled = "Enabled" in admin_group["Attributes"] if admin_group else "N/A"
    summary.append({"Indicator": "Administrators Group", "Value": f"{is_admin} (Enabled: {admin_enabled})", "SID": "S-1-5-32-544"})
    
    # Check for System
    is_system = "Yes" if "system" in principal.lower() else "No"
    summary.append({"Indicator": "System Level", "Value": is_system, "SID": "S-1-5-18"})
    
    # Check for TrustedInstaller
    is_trustedinstaller = "Yes" if "trustedinstaller" in principal.lower() else "No"
    trusted_sid = next((g["SID"] for g in groups if "TrustedInstaller" in g["Description"]), "N/A")
    summary.append({"Indicator": "TrustedInstaller", "Value": is_trustedinstaller, "SID": trusted_sid})
    
    # Check for All Services
    all_services = next((g for g in groups if g["SID"] == "S-1-5-80-0"), None)
    is_service = "Yes" if all_services else "No"
    summary.append({"Indicator": "All Services Group", "Value": is_service, "SID": "S-1-5-80-0"})
    
    return summary

def check_elevation_level():
    try:
        # Get current security principal
        whoami_result = subprocess.run('whoami', shell=True, capture_output=True, text=True)
        principal = whoami_result.stdout.strip()
        print(f"Current Security Principal: {principal}\n")
        
        # Get groups
        groups_result = subprocess.run('whoami /groups', shell=True, capture_output=True, text=True)
        if groups_result.stderr:
            print("Error in groups:", groups_result.stderr)
        
        groups = parse_whoami_groups(groups_result.stdout)
        
        # Print summary table
        print("Privilege Level Summary:")
        summary_headers = ["Indicator", "Value", "SID"]
        summary_data = get_summary(groups, principal)
        print_table(summary_data, summary_headers)
        
        # Print full groups table
        print("\nDetailed Groups Table:")
        groups_headers = ["Group Name", "Type", "SID", "Description", "Attributes"]
        print_table(groups, groups_headers)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(25)

# Run the check
check_elevation_level()