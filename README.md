# Flip Scanner V1

První jádro bota pro hledání flipů výpočetní techniky.

## V1 cíle
- notebooky + PC komponenty
- minimální očekávaný čistý zisk 1 000 Kč
- cena práce 250 Kč/h
- penalizace za pracnost
- rozpoznání běžných závad notebooků
- očekávaná / worst reasonable cena opravy
- MAX BUY
- DEAL SCORE 0–100
- Discord výstup

## Spuštění
```bash
pip install -r requirements.txt
python main.py
```

Discord:
```bash
# Windows PowerShell
$env:DISCORD_WEBHOOK_URL="TVUJ_WEBHOOK"
python main.py --send-discord
```

## Co ještě není ve V1 jádru
`market_prices.json` je zatím testovací lokální cenová databáze.

Další krok projektu:
1. source konektor pro nové inzeráty,
2. ukládání cenové historie,
3. automatický odhad konzervativní prodejní ceny z trhu,
4. přesnější hledání cen konkrétních náhradních dílů,
5. později PC BUILD MODE.
