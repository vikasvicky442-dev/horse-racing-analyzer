#!/usr/bin/env python3
"""
Live Horse Racing Analyzer - Full free API version
Uses PuntersEdge free key for complete Australian racing data.
Ranks by market odds + barrier + form + weight.
"""

import json
import urllib.request
from datetime import datetime

API_KEY = "086da9f9-5317-44da-acaf-745ac78aff70"
URL = "https://api.puntersedge.online/v1/racing/next-to-go?num_races=8&categories=horse&country=AU"

def fetch_races():
    req = urllib.request.Request(URL, headers={"X-API-Key": API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def implied_probability(odds):
    if not odds or odds <= 1:
        return 0.0
    return 1.0 / odds

def form_score(form_str):
    """Simple form score from recent runs string (e.g. '123' or '08'). Higher = better recent form."""
    if not form_str:
        return 0.5
    score = 0.0
    count = 0
    for ch in str(form_str)[:6]:
        if ch.isdigit():
            pos = int(ch)
            if pos == 0:
                score += 0.1  # unplaced
            elif pos <= 3:
                score += 1.0 - (pos - 1) * 0.2
            else:
                score += 0.3
            count += 1
    return score / count if count else 0.5

def barrier_score(barrier, distance=None):
    """Lower barriers generally better, especially in shorter races."""
    if not barrier or barrier <= 0:
        return 0.5
    # Normalize: barrier 1 = 1.0, barrier 20+ = ~0.2
    return max(0.2, 1.0 - (barrier - 1) * 0.04)

def analyze_race(race):
    runners = race.get("runners", [])
    results = []
    distance = race.get("distance_m")
    for runner in runners:
        if runner.get("scratched"):
            continue
        bookmakers = runner.get("bookmakers", [])
        prices = [b.get("win_price") for b in bookmakers if b.get("win_price")]
        if not prices:
            continue
        best_odds = min(prices)
        best_book = next((b["key"] for b in bookmakers if b.get("win_price") == best_odds), "unknown")
        market_prob = implied_probability(best_odds)
        form = form_score(runner.get("form"))
        barrier = barrier_score(runner.get("barrier"), distance)
        # Combined score: 70% market, 15% form, 15% barrier
        combined = (market_prob * 0.70) + (form * 0.15) + (barrier * 0.15)
        results.append({
            "name": runner.get("name", "Unknown"),
            "number": runner.get("number"),
            "best_odds": best_odds,
            "best_book": best_book,
            "market_prob": market_prob,
            "barrier": runner.get("barrier"),
            "weight": runner.get("weight"),
            "form": runner.get("form"),
            "jockey": runner.get("jockey"),
            "combined": combined
        })
    results.sort(key=lambda x: x["combined"], reverse=True)
    return results

def main():
    print("=" * 78)
    print("LIVE HORSE RACING ANALYZER (Full API)")
    print(f"Fetched: {datetime.utcnow().isoformat()}Z | Source: PuntersEdge free key")
    print("Ranking: 70% market odds + 15% form + 15% barrier. Not a guarantee.")
    print("=" * 78)
    
    races = fetch_races()
    if not races:
        print("No race data available.")
        return
    
    for race in races:
        venue = race.get("venue", "Unknown")
        rnum = race.get("race_number", "?")
        dist = race.get("distance_m", "?")
        track = race.get("track_condition", "")
        weather = race.get("weather", "")
        print(f"\n{venue} R{rnum} | {dist}m | {track} | {weather}")
        print("-" * 70)
        
        analyzed = analyze_race(race)
        if not analyzed:
            print("  No priced runners.")
            continue
        
        print(f"{'Rk':<4}{'No':<4}{'Horse':<22}{'Odds':<8}{'Barr':<6}{'Form':<8}{'Score'}")
        for i, r in enumerate(analyzed[:8], 1):
            print(f"{i:<4}{r['number'] or '-':<4}{r['name'][:21]:<22}{r['best_odds']:<8.2f}{str(r['barrier'] or '-'):<6}{str(r['form'] or '-'):<8}{r['combined']:.3f}")
        
        top = analyzed[0]
        print(f"\n  Top pick: {top['name']} @ {top['best_odds']} (barrier {top['barrier']}, form {top['form']})")

if __name__ == "__main__":
    main()
