import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "leads.json"

def load_leads():
    try:
        if DATA_FILE.exists():
            with DATA_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []
    return []

def save_leads(leads):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    temp_file.replace(DATA_FILE)

def upsert_lead(leads, lead):
    updated = [x for x in leads if x.get("id") != lead.get("id")]
    updated.append(lead)
    return updated

def update_lead(leads, lead):
    for index, item in enumerate(leads):
        if item.get("id") == lead.get("id"):
            leads[index] = lead
            return leads
    leads.append(lead)
    return leads

def delete_lead(leads, lead_id):
    return [x for x in leads if x.get("id") != lead_id]
