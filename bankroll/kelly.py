def american_to_decimal(A):
    return 1 + (A/100.0) if A > 0 else 1 + (100.0/abs(A))

def kelly_fraction(p, american):
    b = american_to_decimal(american) - 1.0
    edge = p*b - (1-p)
    return max(0.0, edge / b) if b>0 else 0.0

def fractional_kelly(p, american, frac=0.5):
    return kelly_fraction(p, american) * float(frac)
