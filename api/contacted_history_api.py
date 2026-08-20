"""
Contacted History API
Manages records of previously contacted channels/sites
"""
import os
import json
from datetime import datetime

HISTORY_FILE = "contacted_history.json"

def get_contacted_history_records():
    """Get all contacted history records"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def add_contacted_history_record(record):
    """Add a new contacted history record"""
    try:
        records = get_contacted_history_records()
        record['timestamp'] = datetime.now().isoformat()
        records.append(record)

        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return {"success": True, "record": record}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_contacted_history_record(row_index):
    """Delete a contacted history record by index"""
    try:
        records = get_contacted_history_records()

        if 0 <= row_index < len(records):
            deleted = records.pop(row_index)

            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            return {"success": True, "deleted": deleted}
        else:
            return {"success": False, "error": "Invalid row index"}
    except Exception as e:
        return {"success": False, "error": str(e)}
