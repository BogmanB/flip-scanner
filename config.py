from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    min_net_profit_czk: int = int(os.getenv("MIN_NET_PROFIT_CZK", "1000"))
    labor_rate_czk_per_hour: int = int(os.getenv("LABOR_RATE_CZK_PER_HOUR", "250"))
    default_shipping_czk: int = int(os.getenv("DEFAULT_SHIPPING_CZK", "150"))
    min_score_to_send: int = int(os.getenv("MIN_SCORE_TO_SEND", "65"))
    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")

SETTINGS = Settings()
