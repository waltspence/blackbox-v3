#!/usr/bin/env python3
import json, argparse, itertools

def check_safety_policy(leg, bcfi_data, policy_rules):
    """
    Evaluates a leg against the No Anchor Policy.
    Returns: (bool is_allowed, str reason)
    """
    team_id = leg.get('team_id')
    market = leg.get('market')
    line = float(leg.get('line', 0.0))

    # If no BCFI data for this team, assume safety (or default to caution)
    if team_id not in bcfi_data:
        return True, "no_bcfi_data"

    stats = bcfi_data[team_id]
    bcfi_score = stats.get('bcfi', 0.0)
    venue = stats.get('venue')

    # Iterate through active policy rules
    for rule in policy_rules:
        # 1. Evaluate Condition (Simplified for demo)
        triggered = False
        if rule['name'] == 'EliteAwayFade' and venue == 'away' and bcfi_score >= 0.58:
            triggered = True
        elif rule['name'] == 'EliteHomeFade' and venue == 'home' and bcfi_score >= 0.60:
            triggered = True

        if triggered:
            action = rule['action']
            # Check if this specific market is forbidden
            if market == action.get('forbid_market', 'moneyline'):
                return False, f"Forbidden by {rule['name']} (BCFI {bcfi_score})"

            # Check if this is an attempted "Escape Hatch" leg
            # The user might be submitting an AH leg directly
            alt = action.get('allow_alternative')
            if alt and market == alt['market']:
                # Verify the line meets the safety threshold
                # Logic: We want the line to be MORE positive than min_line
                # e.g., +1.5 >= 1.5 is Good. +0.5 < 1.5 is Bad.
                if line >= alt['min_line']:
                    return True, f"Allowed via Escape Hatch (Line {line} >= {alt['min_line']})"
                else:
                    return False, f"AH Line {line} too risky (Needs {alt['min_line']})"

    return True, "pass"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--legs', required=True)
    ap.add_argument('--bcfi', required=True, help="Path to BCFI scores json")
    ap.add_argument('--policy', default="guards/no_anchor_policy_v1_2.yaml")
    ap.add_argument('--out', default='outputs/slips.json')
    args = ap.parse_args()

    # Load Inputs
    legs = json.load(open(args.legs, 'r', encoding='utf-8'))
    bcfi_data = json.load(open(args.bcfi, 'r', encoding='utf-8'))

    # Load Policy (Mock loading from YAML structure defined above)
    # In production: policy = yaml.safe_load(open(args.policy))
    policy_rules = [
        {"name": "EliteAwayFade", "action": {"forbid_market": "moneyline", "allow_alternative": {"market": "asian_handicap", "min_line": 1.5}}},
        {"name": "EliteHomeFade", "action": {"forbid_market": "moneyline", "allow_alternative": {"market": "asian_handicap", "min_line": 1.0}}}
    ]

    approved_legs = []
    dropped_legs = []

    for leg in legs:
        is_safe, reason = check_safety_policy(leg, bcfi_data, policy_rules)
        if is_safe:
            leg['policy_note'] = reason
            approved_legs.append(leg)
        else:
            dropped_legs.append({'id': leg['leg_id'], 'reason': reason})

    # Proceed to Composition (Simple combination for demo)
    slips = []
    ids = [l['leg_id'] for l in approved_legs]
    for i, combo in enumerate(itertools.combinations(ids, 2)):
        slips.append({'slip_id': f'S{i+1:03d}', 'legs': list(combo)})
        if len(slips) >= 10: break

    with open(args.out, 'w', encoding='utf-8') as jf:
        json.dump({"slips": slips, "dropped": dropped_legs}, jf, indent=2)

if __name__ == '__main__':
    main()
