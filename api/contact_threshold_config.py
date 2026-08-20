"""
Contact Threshold Configuration
Manages the threshold for contact frequency
"""
import os
import json

CONFIG_FILE = "contact_threshold.json"

def get_contact_threshold():
    """Get current contact threshold in days"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('threshold_days', 90)
    except Exception:
        pass
    return 90

def set_contact_threshold(threshold_days):
    """Set contact threshold in days"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'threshold_days': threshold_days}, f)
        return {"success": True, "threshold_days": threshold_days}
    except Exception as e:
        return {"success": False, "error": str(e)}
