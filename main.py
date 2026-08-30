import argparse
import json
from pathlib import Path

from config import SETTINGS
from models import Listing
from scoring import analyze_listing
from discord import format_analysis, send_to_discord

def load_listings(path: str):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Listing(**x) for x in raw]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="demo_listings.json")
    parser.add_argument("--send-discord", action="store_true")
    args = parser.parse_args()

    listings = load_listings(args.input)

    for listing in listings:
        analysis = analyze_listing(listing)
        if analysis is None:
            print(f"\n? NEEDS PRICE DATA: {listing.title}\n")
            continue

        print("\n" + "=" * 72)
        print(format_analysis(analysis))

        if (
            args.send_discord
            and analysis.expected_net_profit_czk >= SETTINGS.min_net_profit_czk
            and analysis.score >= SETTINGS.min_score_to_send
        ):
            send_to_discord(analysis)

if __name__ == "__main__":
    main()
