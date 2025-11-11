from ..config import get_config
import sys

def set_config(key, value):
    """Set configuration value"""
    config = get_config()
    
    # Convert value to appropriate type
    if key in ['max_retries', 'backoff_base']:
        try:
            value = int(value)
        except ValueError:
            print(f"Error: {key} must be an integer")
            return
    
    config.set(key, value)
    checkmark = "OK" if sys.platform == 'win32' else "✓"
    print(f"{checkmark} Configuration updated: {key} = {value}")
