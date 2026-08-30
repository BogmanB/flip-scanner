import json
import re
from pathlib import Path
from models import Listing, RepairEstimate

DATA_PATH = Path(__file__).resolve().parent / "repair_costs.json"

with DATA_PATH.open("r", encoding="utf-8") as f:
    REPAIRS = json.load(f)

HIGH_RISK_PATTERNS = [
    (r"\bnejde\s+zapnout\b|\bnezapne\b|\bdead\b|\bno\s*power\b", "no_power"),
    (r"\bpolit[ýy]\b|\bzatečen|\btekutin", "liquid_damage"),
    (r"\bzákladní\s+deska\b|\bmotherboard\b|\bmainboard\b", "motherboard"),
]

REPAIR_PATTERNS = [
    (r"\bbez\s+(ssd|disku|hdd)\b|\bssd\s+(chybí|není)\b|\bvadn[ýé]\s+ssd\b", "ssd"),
    (r"\bbez\s+ram\b|\bram\s+(chybí|není)\b|\bvadn[áé]\s+ram\b", "ram"),
    (r"\bbaterie\s+(ko|vadn|nedrží|slab)|\bbez\s+baterie\b", "battery"),
    (r"\bpraskl[ýé]\s+(displej|lcd|display)\b|\bvadn[ýé]\s+(displej|lcd|display)\b|\bdisplej\s+nefung", "display"),
    (r"\bklávesnic[ea]\s+(nefung|vadn)|\bvadn[áé]\s+klávesnic", "keyboard"),
    (r"\bventilátor\b|\bvětrák\b|\bfan\b|\bpřehřív", "fan"),
    (r"\bpant\b|\bpanty\b|\bhinge\b|\bvíko\s+poškoz", "hinge"),
    (r"\bnabíječ(ka|ku)\b|\badaptér\b|\bcharger\b", "charger"),
]

def _to_estimate(code: str) -> RepairEstimate:
    d = REPAIRS[code]
    return RepairEstimate(
        defect_code=code,
        defect_label=d["label"],
        parts_low_czk=d["parts_low_czk"],
        parts_expected_czk=d["parts_expected_czk"],
        parts_high_czk=d["parts_high_czk"],
        work_minutes=d["work_minutes"],
        confidence=d["confidence"],
        risk_level=d["risk_level"],
        notes=d.get("notes", []),
    )

def estimate_repair(listing: Listing) -> RepairEstimate:
    text = f"{listing.title} {listing.description}".lower()

    for pattern, code in HIGH_RISK_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            est = _to_estimate(code)
            est.notes = est.notes + ["Nepotvrzená diagnóza: před nákupem nutno osobně otestovat."]
            return est

    for pattern, code in REPAIR_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            return _to_estimate(code)

    return _to_estimate("none")
