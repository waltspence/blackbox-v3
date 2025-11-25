#!/usr/bin/env python3
"""
Domain-Aware Match Analyzer - CLI Tool

Quick single-match analysis through all three domains.

Usage:
    python domain_analyze_match.py --home "Arsenal" --away "Bayern" \
        --home-xg 1.8 --away-xg 2.1 --tactical-edge -0.15 \
        --travel 950 --rest-home 7 --rest-away 3 \
        --fixtures-home 3 --fixtures-away 1 \
        --recent-xg 2.1 --seasonal-xg 1.8 \
        --pressure 0.25 --sample-size 12 --market-odds 2.50
"""

import argparse
import sys
from typing import Dict

try:
    from scripts.three_domain_pipeline import run_three_domain_analysis
except ImportError:
    print("Error: Unable to import three_domain_pipeline")
    sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="BlackBox v3 Three-Domain Match Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--home', required=True, help='Home team')
    parser.add_argument('--away', required=True, help='Away team')
    
    # Domain I
    domain_i = parser.add_argument_group('Domain I: Pure Skill')
    domain_i.add_argument('--home-xg', type=float, required=True)
    domain_i.add_argument('--away-xg', type=float, required=True)
    domain_i.add_argument('--tactical-edge', type=float, required=True)
    
    # Domain II
    domain_ii = parser.add_argument_group('Domain II: Context')
    domain_ii.add_argument('--travel', type=int, required=True)
    domain_ii.add_argument('--rest-home', type=int, required=True)
    domain_ii.add_argument('--rest-away', type=int, required=True)
    domain_ii.add_argument('--fixtures-home', type=int, required=True)
    domain_ii.add_argument('--fixtures-away', type=int, required=True)
    
    # Domain III
    domain_iii = parser.add_argument_group('Domain III: Variance')
    domain_iii.add_argument('--recent-xg', type=float, required=True)
    domain_iii.add_argument('--seasonal-xg', type=float, required=True)
    domain_iii.add_argument('--pressure', type=float, required=True)
    domain_iii.add_argument('--sample-size', type=int, required=True)
    
    # Market
    parser.add_argument('--market-odds', type=float, required=True)
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--json', action='store_true')
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    try:
        results = run_three_domain_analysis(
            home_team=args.home,
            away_team=args.away,
            home_xg=args.home_xg,
            away_xg=args.away_xg,
            tactical_edge=args.tactical_edge,
            travel_km=args.travel,
            home_rest_days=args.rest_home,
            away_rest_days=args.rest_away,
            home_fixture_count=args.fixtures_home,
            away_fixture_count=args.fixtures_away,
            recent_xg=args.recent_xg,
            seasonal_xg=args.seasonal_xg,
            pressure_share=args.pressure,
            sample_size=args.sample_size,
            market_odds=args.market_odds,
            verbose=not args.quiet and not args.json
        )
        
        if args.json:
            import json
            print(json.dumps(results, indent=2))
        elif args.quiet:
            print(f"Edge: {results['final_edge']:+.4f}")
            print(f"Kelly: {results['kelly_fraction']:.4f}")
            print(f"Rec: {results['recommendation']}")
        
        sys.exit(0 if results['recommendation'] in ['BET', 'SMALL_BET'] else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
