import math, statistics as stats

def sigmoid(x):
    return 1.0/(1.0+math.exp(-x))

def logit(p):
    p = min(max(p, 1e-6), 1-1e-6)
    return math.log(p/(1-p))

def hb_blend(p_model, mean_crowd, sigma_model=1.0, sigma_crowd=1.0):
    th0 = logit(p_model)
    thc = logit(mean_crowd)
    w0 = 1.0/(sigma_model**2)
    wc = 1.0/(sigma_crowd**2)
    th_star = (th0*w0 + thc*wc)/(w0+wc)
    return sigmoid(th_star)

def dispersion(ps):
    if not ps: return 0.0
    if len(ps)==1: return 0.0
    return float(stats.pstdev(ps))
