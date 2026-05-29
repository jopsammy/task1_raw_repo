# -*- coding: utf-8 -*-
"""Trace DP branch contributions to H[4] (2,2) vs (3,2)"""
import sys

MOD = 998244353

def generate_dyck(n):
    res = []
    def bt(s, op, cl):
        if cl > op or op > n: return
        if len(s) == 2*n:
            if op == n and cl == n: res.append(s)
            return
        bt(s + '(', op+1, cl)
        bt(s + ')', op, cl+1)
    bt('', 0, 0)
    return res

def x_seq_and_bob(s):
    n = len(s)//2
    h = [0]*(2*n+1)
    for i in range(2*n): h[i+1] = h[i] + (1 if s[i]=='(' else -1)
    l = 0; X = []
    while l < n:
        pos = 2*l; t = 1; best_x = 0
        while pos + t <= 2*n:
            if h[pos + t] == t: best_x = t; t += 1
            elif h[pos + t] > t: t += 1
            else: break
        if best_x == 0: best_x = 1
        X.append(best_x); l += best_x
    bob = sum(j * X[j] for j in range(len(X)))
    return X, bob

def pair_seq(seq):
    res = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq): res.append(1 + seq[i + 1]); i += 2
        else: res.append(seq[i]); i += 1
    return res

def alice_of(s):
    n = len(s)//2; cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')': cnt += 1
    return cnt

a_val = 2; b_val = 3
pa = [1]*100
for i in range(1, 100): pa[i] = pa[i-1]*a_val % MOD

def compute_total_H(N, pa_val):
    total_H = [0]*(N+1); total_H[0] = 1; total_H[1] = pa_val[1]
    for m in range(2, N+1):
        s = 0
        for t in range(m):
            k = t+1; exp = m*k - t*t
            contrib = total_H[t]*total_H[m-1-t] % MOD
            s = (s + pa_val[exp]*contrib) % MOD
        total_H[m] = s
    return total_H

total_H = compute_total_H(4, pa)
print("total_H:", [total_H[i] for i in range(5)])

# Recompute alpha_H and beta_Q up to k=4 with tracing
def make_H_key(bw, kw, c_flag, all1, c_tail):
    return (bw, kw, c_flag, all1, c_tail)

def make_Q_key(bp, kp, c_flag, all1):
    return (bp, kp, c_flag, all1)

# Build alpha_H recursively up to k=3 first
alpha_H = [{} for _ in range(5)]
beta_Q = [{} for _ in range(5)]

alpha_H[0][make_H_key(0, 1, 1, 0, None)] = (1, None)
beta_Q[0][make_Q_key(0, 0, 1, 0)] = (1, None)

for k in range(1, 4):
    ah = {}; bq = {}
    
    # H c=k
    t = k + 1
    if t % 2 == 0: u = t//2; exp_bw = u*(u-1); exp_kw = u
    else: u = t//2; exp_bw = u*u; exp_kw = u+1
    alice_all = k + k*(k-1)//2
    key = make_H_key(exp_bw, exp_kw, 1, 1, None)
    ah[key] = (pa[alice_all] % MOD, None)
    
    # H c=0 non-primitive
    for s in range(1, k-1):
        rest_size = k - s - 1
        if rest_size <= 0: continue
        for hkey, (coeff_A1, x1sub_A1) in alpha_H[s].items():
            bw_A1, kw_A1, c_A1, all1_A1, ct_A1 = hkey
            if c_A1 >= 1: x1A_vals = [(1, coeff_A1)]
            else: x1A_vals = [(x1, c) for (x1, _), c in x1sub_A1.items()] if x1sub_A1 else []
            for x1_A1, a1c in x1A_vals:
                if a1c == 0: continue
                x1_word = 1 + x1_A1; tail_size = k - x1_word
                if tail_size < 0: continue
                ct_new = 0
                for qkey, (q_coeff, _) in beta_Q[tail_size].items():
                    bp_t, kp_t, c_tail_q, _ = qkey
                    bw = bp_t + tail_size; kw = 1 + kp_t
                    alice_extra = 2*s + 1 + (s+1)*rest_size
                    contrib = pa[alice_extra]*a1c%MOD*total_H[rest_size]%MOD
                    ct_new = c_tail_q
                    key = make_H_key(bw, kw, 0, 0, ct_new)
                    if key not in ah: ah[key] = (0, {})
                    tc, xd = ah[key]
                    prev = xd.get((x1_word, ct_new), 0)
                    xd[(x1_word, ct_new)] = (prev+contrib)%MOD
                    ah[key] = ((tc+contrib)%MOD, xd)
    
    # H c=0 primitive
    if k-1 >= 0:
        for hkey, (coeff_T, x1sub_T) in alpha_H[k-1].items():
            bw_T, kw_T, c_T, all1_T, ct_T = hkey
            if c_T >= 1: t1_vals = [(1, coeff_T, None)]
            else: t1_vals = [(x1, c, ct) for (x1, ct), c in x1sub_T.items()] if x1sub_T else []
            for t1, tc, ct_T_val in t1_vals:
                if tc == 0: continue
                tail_size = k - 1 - t1
                if tail_size < 0: continue
                if c_T >= 1:
                    c_tail_group = 1 if all1_T == 1 else 0
                    use_filter = True
                else:
                    c_tail_group = ct_T_val if ct_T_val is not None else 0
                    use_filter = True
                for qkey, (q_coeff, _) in beta_Q[tail_size].items():
                    bp_t, kp_t, cq, aq = qkey
                    if use_filter and cq != c_tail_group: continue
                    bw = bp_t + tail_size; kw = 1 + kp_t
                    alice_A = 2*k - 1
                    contrib = pa[alice_A]*tc%MOD
                    ct_new = c_tail_group
                    key = make_H_key(bw, kw, 0, 0, ct_new)
                    if key not in ah: ah[key] = (0, {})
                    tc2, xd = ah[key]; x1_A = 1 + t1
                    prev = xd.get((x1_A, ct_new), 0)
                    xd[(x1_A, ct_new)] = (prev+contrib)%MOD
                    ah[key] = ((tc2+contrib)%MOD, xd)
    
    # H c=2p
    for p in range(1, k//2+1):
        c = 2*p; rest_size = k-c
        if rest_size <= 0: continue
        for hkey, (coeff_r, _) in alpha_H[rest_size].items():
            bw_r, kw_r, c_r, a_r, ct_r = hkey
            if c_r != 0 or a_r != 0: continue
            bw = p*(k-p) + bw_r; kw = p + kw_r
            alice_prefix = p*(2*p+1) + 2*p*rest_size
            contrib = pa[alice_prefix]*coeff_r%MOD
            key = make_H_key(bw, kw, 1, 0, None)
            if key not in ah: ah[key] = (0, None)
            tc, _ = ah[key]; ah[key] = ((tc+contrib)%MOD, None)
    
    # H c=2p+1
    for p in range(0, (k+1)//2):
        c = 2*p+1; rest_size = k-c
        if rest_size <= 0: continue
        for hkey, (coeff_r, _) in alpha_H[rest_size].items():
            bw_r, kw_r, c_r, a_r, ct_r = hkey
            if c_r != 0 or a_r != 0: continue
            bw = (p+1)*(k-p-1) + bw_r; kw = p+1 + kw_r
            alice_prefix = (2*p+1)*(p+1) + (2*p+1)*rest_size
            contrib = pa[alice_prefix]*coeff_r%MOD
            key = make_H_key(bw, kw, 1, 0, None)
            if key not in ah: ah[key] = (0, None)
            tc, _ = ah[key]; ah[key] = ((tc+contrib)%MOD, None)
    
    alpha_H[k] = ah
    
    # Q c=k
    if k % 2 == 0: p = k//2; exp_bp = p*(p-1); exp_kp = p
    else: p = k//2; exp_bp = p*p; exp_kp = p+1
    alice_all_q = k + k*(k-1)//2
    key = make_Q_key(exp_bp, exp_kp, 1, 1)
    bq[key] = (pa[alice_all_q]%MOD, None)
    
    # Q c=0 non-primitive
    for s in range(1, k-1):
        rest_size = k - s - 1
        if rest_size <= 0: continue
        for hkey, (coeff_A1, x1sub_A1) in alpha_H[s].items():
            bw_A1, kw_A1, c_A1, all1_A1, ct_A1 = hkey
            if c_A1 >= 1: x1A_vals = [(1, coeff_A1)]
            else: x1A_vals = [(x1, c) for (x1, _), c in x1sub_A1.items()] if x1sub_A1 else []
            for x1_A1, a1c in x1A_vals:
                if a1c == 0: continue
                x1_word = 1 + x1_A1; tail_size = k - x1_word
                if tail_size < 0: continue
                for qkey, (q_coeff, _) in beta_Q[tail_size].items():
                    bp_t, kp_t, _, _ = qkey
                    bp = bp_t + tail_size; kp = 1 + kp_t
                    alice_extra = 2*s + 1 + (s+1)*rest_size
                    contrib = pa[alice_extra]*a1c%MOD*total_H[rest_size]%MOD
                    key = make_Q_key(bp, kp, 0, 0)
                    if key not in bq: bq[key] = (0, {})
                    tc, xd = bq[key]
                    prev = xd.get(x1_word, 0)
                    xd[x1_word] = (prev+contrib)%MOD
                    bq[key] = ((tc+contrib)%MOD, xd)
    
    # Q c=0 primitive
    if k-1 >= 0:
        for hkey, (coeff_T, x1sub_T) in alpha_H[k-1].items():
            bw_T, kw_T, c_T, all1_T, ct_T = hkey
            if c_T >= 1: t1_vals = [(1, coeff_T, None)]
            else: t1_vals = [(x1, c, ct) for (x1, ct), c in x1sub_T.items()] if x1sub_T else []
            for t1, tc, ct_T_val in t1_vals:
                if tc == 0: continue
                tail_size = k - 1 - t1
                if tail_size < 0: continue
                if c_T >= 1:
                    c_tail_group = 1 if all1_T == 1 else 0
                    use_filter = True
                else:
                    c_tail_group = ct_T_val if ct_T_val is not None else 0
                    use_filter = True
                for qkey, (q_coeff, _) in beta_Q[tail_size].items():
                    bp_t, kp_t, cq, aq = qkey
                    if use_filter and cq != c_tail_group: continue
                    bp = bp_t + tail_size; kp = 1 + kp_t
                    alice_A = 2*k - 1
                    contrib = pa[alice_A]*tc%MOD
                    key = make_Q_key(bp, kp, 0, 0)
                    if key not in bq: bq[key] = (0, {})
                    tc2, xd = bq[key]; x1_A = 1 + t1
                    prev = xd.get(x1_A, 0)
                    xd[x1_A] = (prev+contrib)%MOD
                    bq[key] = ((tc2+contrib)%MOD, xd)
    
    # Q c=2p
    for p in range(1, k//2+1):
        c = 2*p; rest_size = k-c
        if rest_size <= 0: continue
        for qkey, (q_coeff, _) in beta_Q[rest_size].items():
            bp_r, kp_r, c_r, a_r = qkey
            if c_r != 0 or a_r != 0: continue
            bp = bp_r + p*(k-p-1); kp = p + kp_r
            alice_prefix = p*(2*p+1) + 2*p*rest_size
            contrib = pa[alice_prefix]*q_coeff%MOD
            key = make_Q_key(bp, kp, 1, 0)
            if key not in bq: bq[key] = (0, None)
            tc, _ = bq[key]; bq[key] = ((tc+contrib)%MOD, None)
    
    beta_Q[k] = bq

# Print H[1]-H[3]
print("\n=== Built H[1]-H[3] ===")
for k in range(1, 4):
    for hkey, (coeff, x1sub) in sorted(alpha_H[k].items()):
        extra = ""
        if x1sub:
            extra = " x1sub=%s" % sorted(x1sub.items())
        print("H[%d] %s: coeff=%d%s" % (k, hkey, coeff, extra))

print("\n=== Built Q[0]-Q[3] ===")
for k in range(4):
    for qkey, (coeff, x1sub) in sorted(beta_Q[k].items()):
        extra = ""
        if x1sub:
            extra = " x1sub=%s" % sorted(x1sub.items())
        print("Q[%d] %s: coeff=%d%s" % (k, qkey, coeff, extra))

# Now compute H[4] with tracing
print("\n=== Computing H[4] with trace ===")
k = 4
ah = {}
contrib_log = []

def log_contrib(branch, hkey, contrib, details=""):
    contrib_log.append((branch, hkey, contrib, details))

# H c=k (all 1s)
t = k + 1  # 5
u = t//2  # 2
exp_bw = u*u; exp_kw = u+1  # 4,3
alice_all = k + k*(k-1)//2  # 4+6=10
key = make_H_key(4, 3, 1, 1, None)
ah[key] = (pa[10] % MOD, None)
log_contrib("c=k", key, pa[10], "alice=10")

# H c=0 non-primitive: s=1..2
for s in range(1, k-1):
    rest_size = k - s - 1
    if rest_size <= 0: continue
    print("\n  c=0 non-prim: s=%d rest=%d" % (s, rest_size))
    for hkey, (coeff_A1, x1sub_A1) in alpha_H[s].items():
        bw_A1, kw_A1, c_A1, all1_A1, ct_A1 = hkey
        print("    A1 orbit: %s coeff=%d" % (hkey, coeff_A1))
        if c_A1 >= 1: x1A_vals = [(1, coeff_A1)]
        else: x1A_vals = [(x1, c) for (x1, _), c in x1sub_A1.items()] if x1sub_A1 else []
        for x1_A1, a1c in x1A_vals:
            if a1c == 0: continue
            x1_word = 1 + x1_A1; tail_size = k - x1_word
            print("      x1_A1=%d a1c=%d x1_word=%d tail=%d" % (x1_A1, a1c, x1_word, tail_size))
            if tail_size < 0: continue
            for qkey, (q_coeff, _) in beta_Q[tail_size].items():
                bp_t, kp_t, c_tail_q, _ = qkey
                bw = bp_t + tail_size; kw = 1 + kp_t
                alice_extra = 2*s + 1 + (s+1)*rest_size
                contrib = pa[alice_extra]*a1c%MOD*total_H[rest_size]%MOD
                ct_new = c_tail_q
                key = make_H_key(bw, kw, 0, 0, ct_new)
                print("        Q[%d]: %s -> key=%s contrib=%d" % (tail_size, qkey, key, contrib))
                if key not in ah: ah[key] = (0, {})
                tc, xd = ah[key]
                prev = xd.get((x1_word, ct_new), 0)
                xd[(x1_word, ct_new)] = (prev+contrib)%MOD
                ah[key] = ((tc+contrib)%MOD, xd)
                log_contrib("c=0 non-prim s=%d" % s, key, contrib,
                    "A1=%s x1=%d tailQ=%d alice_extra=%d" % (hkey, x1_A1, tail_size, alice_extra))

# H c=0 primitive
print("\n  c=0 primitive:")
if k-1 >= 0:
    for hkey, (coeff_T, x1sub_T) in alpha_H[k-1].items():
        bw_T, kw_T, c_T, all1_T, ct_T = hkey
        print("    T orbit: %s coeff=%d" % (hkey, coeff_T))
        if c_T >= 1: t1_vals = [(1, coeff_T, None)]
        else: t1_vals = [(x1, c, ct) for (x1, ct), c in x1sub_T.items()] if x1sub_T else []
        for t1, tc, ct_T_val in t1_vals:
            if tc == 0: continue
            tail_size = k - 1 - t1
            print("      t1=%d tc=%d ct_T=%s tail=%d" % (t1, tc, ct_T_val, tail_size))
            if tail_size < 0: continue
            if c_T >= 1:
                c_tail_group = 1 if all1_T == 1 else 0
                use_filter = True
            else:
                c_tail_group = ct_T_val if ct_T_val is not None else 0
                use_filter = True
            print("      c_tail_group=%d use_filter=%d" % (c_tail_group, use_filter))
            for qkey, (q_coeff, _) in beta_Q[tail_size].items():
                bp_t, kp_t, cq, aq = qkey
                if use_filter and cq != c_tail_group: 
                    print("        FILTER: Q[%d] %s cq=%d != %d" % (tail_size, qkey, cq, c_tail_group))
                    continue
                bw = bp_t + tail_size; kw = 1 + kp_t
                alice_A = 2*k - 1  # 7
                contrib = pa[alice_A]*tc%MOD
                ct_new = c_tail_group
                key = make_H_key(bw, kw, 0, 0, ct_new)
                print("        Q[%d] %s -> key=%s contrib=%d" % (tail_size, qkey, key, contrib))
                if key not in ah: ah[key] = (0, {})
                tc2, xd = ah[key]; x1_A = 1 + t1
                prev = xd.get((x1_A, ct_new), 0)
                xd[(x1_A, ct_new)] = (prev+contrib)%MOD
                ah[key] = ((tc2+contrib)%MOD, xd)
                log_contrib("c=0 prim", key, contrib,
                    "T=%s t1=%d Q=%s" % (hkey, t1, qkey))

# H c=2p
print("\n  c=2p (even):")
for p in range(1, k//2+1):
    c = 2*p; rest_size = k-c
    if rest_size <= 0: continue
    print("    p=%d c=%d rest=%d" % (p, c, rest_size))
    for hkey, (coeff_r, _) in alpha_H[rest_size].items():
        bw_r, kw_r, c_r, a_r, ct_r = hkey
        if c_r != 0 or a_r != 0:
            print("      REST FILTER: %s rejected" % (hkey,))
            continue
        bw = p*(k-p) + bw_r; kw = p + kw_r
        alice_prefix = p*(2*p+1) + 2*p*rest_size
        contrib = pa[alice_prefix]*coeff_r%MOD
        key = make_H_key(bw, kw, 1, 0, None)
        print("      rest=%s -> bw=%d kw=%d alice_p=%d contrib=%d key=%s" % (
            hkey, bw, kw, alice_prefix, contrib, key))
        if key not in ah: ah[key] = (0, None)
        tc, _ = ah[key]; ah[key] = ((tc+contrib)%MOD, None)
        log_contrib("c=2p p=%d" % p, key, contrib, "rest=%s" % (hkey,))

# H c=2p+1
print("\n  c=2p+1 (odd):")
for p in range(0, (k+1)//2):
    c = 2*p+1; rest_size = k-c
    if rest_size <= 0: continue
    print("    p=%d c=%d rest=%d" % (p, c, rest_size))
    for hkey, (coeff_r, _) in alpha_H[rest_size].items():
        bw_r, kw_r, c_r, a_r, ct_r = hkey
        if c_r != 0 or a_r != 0:
            print("      REST FILTER: %s rejected" % (hkey,))
            continue
        bw = (p+1)*(k-p-1) + bw_r; kw = p+1 + kw_r
        alice_prefix = (2*p+1)*(p+1) + (2*p+1)*rest_size
        contrib = pa[alice_prefix]*coeff_r%MOD
        key = make_H_key(bw, kw, 1, 0, None)
        print("      rest=%s -> bw=%d kw=%d alice_p=%d contrib=%d key=%s" % (
            hkey, bw, kw, alice_prefix, contrib, key))
        if key not in ah: ah[key] = (0, None)
        tc, _ = ah[key]; ah[key] = ((tc+contrib)%MOD, None)
        log_contrib("c=2p+1 p=%d" % p, key, contrib, "rest=%s" % (hkey,))

print("\n=== H[4] DP results ===")
for hkey, (coeff, x1sub) in sorted(ah.items()):
    extra = ""
    if x1sub:
        extra = " x1sub=%s" % sorted(x1sub.items())
    print("  %s: coeff=%d%s" % (hkey, coeff, extra))

# Aggregate by (bw,kw)
print("\n=== Aggregated by (bw,kw) ===")
agg = {}
for hkey, (coeff, _) in ah.items():
    bk = (hkey[0], hkey[1])
    agg[bk] = (agg.get(bk, 0) + coeff) % MOD
for bk, v in sorted(agg.items()):
    print("  %s: %d" % (bk, v))

# Compare with BF
print("\n=== BF ===")
words = generate_dyck(4)
bf_map = {}
for s in words:
    X, _ = x_seq_and_bob(s)
    Xw = pair_seq([1]+X)
    bw = sum(j*Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    al = alice_of(s)
    bk = (bw, kw)
    bf_map[bk] = (bf_map.get(bk, 0) + pa[al]) % MOD
for bk, v in sorted(bf_map.items()):
    dpv = agg.get(bk, 0)
    ok = "OK" if dpv == v else "DIFF=%d" % ((dpv-v)%MOD)
    print("  %s: BF=%d DP=%d %s" % (bk, v, dpv, ok))
