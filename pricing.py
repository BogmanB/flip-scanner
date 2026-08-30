import json
import re
from pathlib import Path
from models import Listing

PRICE_DB_PATH = Path(__file__).resolve().parent / "market_prices.json"

def load_price_db():
    with PRICE_DB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9á-ž]+", " ", text)
    return " ".join(text.split())

def estimate_market_price(listing: Listing) -> tuple[int | None, str]:
    """
    V1:
    1) pokud listing obsahuje ručně zadanou tržní cenu, použije ji;
    2) jinak hledá model/alias v lokální cenové DB.
    V dalším kroku připojíme automatické aktualizování DB z trhu.
    """
    if listing.manual_market_price_czk:
        return int(listing.manual_market_price_czk), "manual"

    db = load_price_db()
    haystack = normalize(f"{listing.title} {listing.description}")

    matches = []
    for item in db.get("items", []):
        aliases = [item.get("model", "")] + item.get("aliases", [])
        if any(normalize(a) in haystack for a in aliases if a):
            matches.append(item)

    if not matches:
        return None, "unknown"

    # Preferujeme nejdelší / nejkonkrétnější název.
    matches.sort(key=lambda x: len(normalize(x.get("model", ""))), reverse=True)
    price = int(matches[0]["conservative_sell_price_czk"])
    return price, matches[0]["model"]
