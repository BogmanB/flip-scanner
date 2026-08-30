from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Listing:
    source: str
    title: str
    price_czk: int
    url: str
    description: str = ""
    location: str = ""
    category: str = ""  # notebook / gpu / cpu / ram / ssd / set / pc
    manual_market_price_czk: Optional[int] = None

@dataclass
class RepairEstimate:
    defect_code: str = "none"
    defect_label: str = "Bez zjevné závady"
    parts_low_czk: int = 0
    parts_expected_czk: int = 0
    parts_high_czk: int = 0
    work_minutes: int = 10
    confidence: float = 1.0
    risk_level: str = "low"
    notes: List[str] = field(default_factory=list)

@dataclass
class DealAnalysis:
    listing: Listing
    market_price_czk: int
    repair: RepairEstimate
    other_costs_czk: int
    labor_cost_czk: int
    expected_net_profit_czk: int
    worst_reasonable_profit_czk: int
    max_buy_czk: int
    discount_pct: float
    profit_per_hour_czk: Optional[int]
    score: int
    mode: str
    verdict: str
    reasons: List[str] = field(default_factory=list)
