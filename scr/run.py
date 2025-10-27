#!/usr/bin/env python3
"""
PrivilegeElevator - Main Entry Point
A comprehensive system privilege analysis and elevation tool.
"""

import os
import sys
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import config

def main():
    parser = argparse.ArgumentParser(
        description="PrivilegeElevator - System Privilege Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --gui                    # Launch GUI
  python run.py --cli                    # Command line interface
  python run.py --setup                  # Run setup wizard
  python run.py --demo                   # Run privilege demo
  python run.py --config                 # Show current configuration
        """
    )
    
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    parser.add_argument('--cli', action='store_true', help='Use command line interface')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--demo', action='store_true', help='Run privilege demonstration')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    parser.add_argument('--system', action='store_true', help='Run as SYSTEM (requires PsExec)')
    parser.add_argument('--output', type=str, help='Output file for results')
    
    args = parser.parse_args()
    
    print("🛡️  PrivilegeElevator v1.0.0")
    print("=" * 50)
    
    # Auto-setup if first run
    if not config.setup_done and config.get('auto_setup', True):
        config.setup_environment()
    
    # Handle arguments
    if args.setup:
        config.setup_environment()
    
    elif args.config:
        import json
        print("Current Configuration:")
        print(json.dumps(config.config, indent=2))
    
    elif args.demo:
        from privilege_tests import run_privilege_demo
        run_privilege_demo(system_mode=args.system, output_file=args.output)
    
    elif args.cli:
        from core import PrivilegeAnalyzer
        analyzer = PrivilegeAnalyzer()
        analyzer.run_cli_analysis()
    
    elif args.gui or not any(vars(args).values()):
        try:
            from gui import PrivilegeDemoGUI
            app = PrivilegeDemoGUI()
            app.run()
        except ImportError as e:
            print(f"❌ GUI dependencies missing: {e}")
            print("💡 Try: pip install tkinter")
            from core import PrivilegeAnalyzer
            analyzer = PrivilegeAnalyzer()
            analyzer.run_cli_analysis()

if __name__ == "__main__":
    main()