import requests
from config import SETTINGS
from models import DealAnalysis

def money(v: int) -> str:
    return f"{v:,} Kč".replace(",", " ")

def work_label(minutes: int) -> str:
    if minutes <= 15: return "⚡ EASY FLIP"
    if minutes <= 60: return "🔧 LIGHT WORK"
    if minutes <= 120: return "🛠️ WORK REQUIRED"
    return "☠️ PROJECT"

def format_analysis(a: DealAnalysis) -> str:
    r = a.repair
    lines = [
        f"🔥 **{a.verdict} — DEAL {a.score}/100**",
        f"**{a.listing.title}**",
        f"🏷 Nákup: **{money(a.listing.price_czk)}**",
        f"💰 Konzervativní prodej: **{money(a.market_price_czk)}**",
        f"🎯 MAX BUY pro min. 1 000 Kč zisk: **{money(a.max_buy_czk)}**",
        "",
        f"🔁 Režim: **{a.mode}**",
        f"{work_label(r.work_minutes)} · ~{r.work_minutes} min",
    ]

    if r.defect_code != "none":
        lines += [
            "",
            f"❌ Závada: **{r.defect_label}**",
            f"🧩 Díly: {money(r.parts_low_czk)}–{money(r.parts_high_czk)} "
            f"(expected {money(r.parts_expected_czk)})",
            f"🎯 Jistota diagnózy: **{round(r.confidence*100)} %**",
            f"⚠️ Riziko: **{r.risk_level.upper()}**",
        ]

    lines += [
        "",
        f"💸 Odhad práce: **{money(a.labor_cost_czk)}**",
        f"📦 Ostatní náklady: **{money(a.other_costs_czk)}**",
        f"📈 Expected čistý zisk: **{money(a.expected_net_profit_czk)}**",
        f"🧯 Worst reasonable: **{money(a.worst_reasonable_profit_czk)}**",
    ]

    if a.profit_per_hour_czk:
        lines.append(f"⏱ Profit / hod.: **{money(a.profit_per_hour_czk)}**")

    if a.listing.location:
        lines.append(f"📍 {a.listing.location}")

    lines.append(f"🔗 {a.listing.url}")
    return "\n".join(lines)

def send_to_discord(a: DealAnalysis) -> None:
    if not SETTINGS.discord_webhook_url:
        return
    response = requests.post(
        SETTINGS.discord_webhook_url,
        json={"content": format_analysis(a)},
        timeout=20,
    )
    response.raise_for_status()
