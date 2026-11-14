#!/usr/bin/env python3
"""
Live Horse Racing Analyzer
Uses free PuntersEdge demo API for Australian racing.
Ranks runners by market-implied probability from best available odds.
"""

import json
import urllib.request
from datetime import datetime

DEMO_URL = "https://api.puntersedge.online/v1/demo/racing/next-to-go"

def fetch_races():
    try:
        with urllib.request.urlopen(DEMO_URL, timeout=15) as response:
            data = json.loads(response.read().decode())
        return data.get("races", [])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def implied_probability(odds):
    """Convert decimal odds to implied probability (0-1)."""
    if odds is None or odds <= 1:
        return 0.0
    return 1.0 / odds

def analyze_race(race):
    runners = race.get("runners", [])
    results = []
    for runner in runners:
        bookmakers = runner.get("bookmakers", [])
        prices = [b.get("win_price") for b in bookmakers if b.get("win_price")]
        if not prices:
            continue
        best_odds = min(prices)  # lowest odds = highest probability
        best_book = next((b["key"] for b in bookmakers if b.get("win_price") == best_odds), "unknown")
        prob = implied_probability(best_odds)
        results.append({
            "name": runner.get("name", "Unknown"),
            "number": runner.get("number"),
            "best_odds": best_odds,
            "best_book": best_book,
            "implied_prob": prob,
            "books_quoting": len(prices)
        })
    # Sort by highest probability (lowest odds)
    results.sort(key=lambda x: x["implied_prob"], reverse=True)
    return results

def main():
    print("=" * 70)
    print("LIVE HORSE RACING ANALYZER")
    print(f"Data source: PuntersEdge free demo | Fetched: {datetime.utcnow().isoformat()}Z")
    print("Note: Demo data is truncated. Market odds only — not a tip or guarantee.")
    print("=" * 70)
    
    races = fetch_races()
    if not races:
        print("No race data available right now.")
        return
    
    for race in races:
        venue = race.get("venue", "Unknown")
        race_num = race.get("race_number", "?")
        category = race.get("category", "unknown")
        start = race.get("start_time", "")
        country = race.get("country", "")
        
        print(f"\n{venue} R{race_num} ({category}) | {country} | Start: {start}")
        print("-" * 60)
        
        analyzed = analyze_race(race)
        if not analyzed:
            print("  No priced runners.")
            continue
        
        print(f"{'Rank':<6}{'No':<4}{'Horse':<25}{'Best Odds':<12}{'Prob %':<10}{'Book'}")
        for i, r in enumerate(analyzed, 1):
            prob_pct = r["implied_prob"] * 100
            print(f"{i:<6}{r['number'] or '-':<4}{r['name'][:24]:<25}{r['best_odds']:<12.2f}{prob_pct:<10.1f}{r['best_book']}")
        
        if analyzed:
            top = analyzed[0]
            print(f"\n  Highest probability (market): {top['name']} @ {top['best_odds']} ({top['implied_prob']*100:.1f}%)")

if __name__ == "__main__":
    main()
