import yaml

def load_rsi_caps(path):
    y = yaml.safe_load(open(path,'r',encoding='utf-8'))
    return y['rsi_caps'], y['templates']

def cap_by_rsi(unit_mult, br_frac, rsi_level, caps):
    c = caps.get(rsi_level, caps['medium'])
    return min(unit_mult, c['unit_cap']), min(br_frac, c['br_cap'])
