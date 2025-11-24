import sys
import os
import argparse
from core.config_loader import load_config
from core.executor import execute_action

def main():
    parser = argparse.ArgumentParser(description="Gely Template Engine")
    parser.add_argument("action", help="The action to execute (e.g., add-reducer)")
    parser.add_argument("--config", default="gely/config.json", help="Path to config file")
    
    args = parser.parse_args()
    
    # Ensure we can find the config
    if not os.path.exists(args.config):
        print(f"Error: Config file not found at {args.config}")
        print("Please run this command from the root of your project or specify --config.")
        sys.exit(1)
        
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
        
    # Execute
    config_dir = os.path.dirname(args.config)
    execute_action(config, args.action, config_dir=config_dir)

if __name__ == "__main__":
    main()