# Horse Racing Analyzer

Simple live analyzer for Australian racing using the free PuntersEdge demo API.

## What it does
- Fetches next races from the public demo endpoint (no API key needed).
- For each race, finds the best available odds across bookmakers.
- Calculates market-implied probability.
- Ranks horses from highest to lowest probability based on current market prices.

## Limitations (raw facts)
- Demo data is truncated (sample races/runners/prices).
- Uses market odds only. Does not include form, barrier, weight, track conditions, jockey stats, or other factors (those require a full API key or other sources).
- Market-implied probability is not the same as true win probability. Books build in margin.
- Not betting advice. For informational use only.

## Run it
```bash
python3 analyzer.py
```

Requires Python 3. No extra packages needed.

## Get more data
Sign up for a free PuntersEdge key (1,500 credits/month) at https://puntersedge.online/api for full next-to-go data, form, barriers, etc.
