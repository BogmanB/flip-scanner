from config import SETTINGS
from models import Listing, DealAnalysis
from repair import estimate_repair
from pricing import estimate_market_price

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def work_score(minutes: int) -> int:
    if minutes <= 15: return 20
    if minutes <= 30: return 18
    if minutes <= 60: return 15
    if minutes <= 120: return 10
    if minutes <= 180: return 5
    return 0

def discount_score(discount_pct: float) -> int:
    # 10 % sleva skoro nic; 50 %+ maximum.
    return int(clamp((discount_pct - 10) / 40 * 25, 0, 25))

def profit_score(profit: int) -> int:
    if profit < SETTINGS.min_net_profit_czk:
        return 0
    if profit >= 8000: return 25
    if profit >= 5000: return 22
    if profit >= 3000: return 18
    if profit >= 2000: return 14
    if profit >= 1500: return 11
    return 8

def liquidity_score(category: str) -> int:
    category = (category or "").lower()
    return {
        "gpu": 15,
        "notebook": 13,
        "cpu": 13,
        "set": 12,
        "ram": 10,
        "ssd": 9,
        "pc": 11,
    }.get(category, 8)

def risk_score(risk_level: str, confidence: float) -> int:
    base = {
        "low": 10,
        "medium": 7,
        "high": 3,
        "extreme": 0,
    }.get(risk_level, 5)
    return int(round(base * clamp(confidence, 0.0, 1.0)))

def logistics_score(location: str) -> int:
    # V1 neutrální. Později podle vzdálenosti od uživatele.
    return 4 if location else 3

def choose_mode(defect_code: str, risk_level: str) -> str:
    if defect_code == "none":
        return "DIRECT_FLIP"
    if risk_level in ("low", "medium"):
        return "REPAIR_FLIP"
    return "HIGH_RISK"

def verdict_for(score: int, profit: int, risk_level: str) -> str:
    if profit < SETTINGS.min_net_profit_czk:
        return "SKIP"
    if risk_level == "extreme":
        return "SKIP / ONLY FOR PARTS"
    if score >= 80:
        return "BUY"
    if score >= SETTINGS.min_score_to_send:
        return "CHECK"
    return "SKIP"

def analyze_listing(listing: Listing) -> DealAnalysis | None:
    market_price, price_source = estimate_market_price(listing)
    if not market_price:
        return None

    repair = estimate_repair(listing)
    labor_cost = round((repair.work_minutes / 60) * SETTINGS.labor_rate_czk_per_hour)
    other_costs = SETTINGS.default_shipping_czk

    expected_total_cost = (
        listing.price_czk
        + repair.parts_expected_czk
        + labor_cost
        + other_costs
    )
    worst_total_cost = (
        listing.price_czk
        + repair.parts_high_czk
        + labor_cost
        + other_costs
    )

    expected_profit = market_price - expected_total_cost
    worst_profit = market_price - worst_total_cost

    max_buy = max(
        0,
        market_price
        - repair.parts_expected_czk
        - labor_cost
        - other_costs
        - SETTINGS.min_net_profit_czk
    )

    discount_pct = ((market_price - listing.price_czk) / market_price) * 100
    pph = None
    if repair.work_minutes > 0 and expected_profit > 0:
        pph = round(expected_profit / (repair.work_minutes / 60))

    score = (
        discount_score(discount_pct)
        + profit_score(expected_profit)
        + liquidity_score(listing.category)
        + work_score(repair.work_minutes)
        + risk_score(repair.risk_level, repair.confidence)
        + logistics_score(listing.location)
    )
    score = int(clamp(score, 0, 100))

    mode = choose_mode(repair.defect_code, repair.risk_level)
    verdict = verdict_for(score, expected_profit, repair.risk_level)

    reasons = [f"Tržní cena: {market_price:,} Kč ({price_source})".replace(",", " ")]
    if repair.defect_code != "none":
        reasons.append(f"Závada: {repair.defect_label}")
    if repair.risk_level in ("high", "extreme"):
        reasons.append("Vysoké riziko nepřesné diagnózy.")

    return DealAnalysis(
        listing=listing,
        market_price_czk=market_price,
        repair=repair,
        other_costs_czk=other_costs,
        labor_cost_czk=labor_cost,
        expected_net_profit_czk=expected_profit,
        worst_reasonable_profit_czk=worst_profit,
        max_buy_czk=max_buy,
        discount_pct=round(discount_pct, 1),
        profit_per_hour_czk=pph,
        score=score,
        mode=mode,
        verdict=verdict,
        reasons=reasons,
    )
