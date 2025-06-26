# slot_config.py

SLOT_METADATA = {
    "Morning Peak": {
        "db_names": ["Morning Peak"],
        "color": "#FB8C00",  # Bright Orange
        "order": 0,
        "time": "6am to 9am"
    },
    "Day (Normal)": {
        "db_names": ["Day (Normal)"],
        "color": "#0288D1",  # Sky Blue
        "order": 1,
        "time": "9am to 6pm"
    },
    "Evening Peak": {
        "db_names": ["Evening Peak"],
        "color": "#C62828",  # Crimson Red
        "order": 2,
        "time": "6pm to 10pm"
    },
    "Night Off-Peak": {
        "db_names": ["Off-Peak", "off-Peak", "Night Off-Peak"],
        "color": "#6A1B9A",  # Deep Purple
        "order": 3,
        "time": "10pm to 6am"
    }
}

def get_slot_order():
    return sorted(SLOT_METADATA.keys(), key=lambda x: SLOT_METADATA[x]["order"])

def get_slot_color_map():
    return {slot: SLOT_METADATA[slot]["color"] for slot in SLOT_METADATA}

def normalize_slot_name(raw_slot: str) -> str:
    raw_slot_lower = raw_slot.strip().lower()
    for display_name, metadata in SLOT_METADATA.items():
        for alias in metadata["db_names"]:
            if raw_slot_lower == alias.strip().lower():
                return display_name
    return raw_slot  # fallback if unknown

def add_slot_labels_with_time():
    return {
        slot: f"{slot} ({meta['time']})"
        for slot, meta in SLOT_METADATA.items()
    }
