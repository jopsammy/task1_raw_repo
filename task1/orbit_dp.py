# -*- coding: utf-8 -*-
"""H+Q recurrences: compute H[k][L] via orbit-based DP with c-based formulas.

Key identities verified:
  Q[k] orbit set = H[k-1] orbit set (bijection)
  H c-based wrapping formula: 255/255 OK
  c=0 wrapping: bw = bp(Q_rest) + (k-x1), kw = 1 + kp(Q_rest)

Strategies:
  total_H[m] = sum of a^alice over all words of size m (Catalan alice recurrence)
  alpha_H[k][bw][kw] = sum of a^alice for k-words with wrapping (bw,kw)
  beta_Q[k][bp][kp]  = sum of a^alice for k-words with pair_seq(X)=(bp,kp)
"""
import sys

MOD = 998244353

def generate_dyck(n):
    res = []
    def bt(s, op, cl):
        if cl > op or op > n:
            return
        if len(s) == 2*n:
            if op == n and cl == n:
                res.append(s)
            return
        bt(s + '(', op+1, cl)
        bt(s + ')', op, cl+1)
    bt('', 0, 0)
    return res

def x_seq_and_bob(s):
    n = len(s)//2
    h = [0]*(2*n+1)
    for i in range(2*n):
        h[i+1] = h[i] + (1 if s[i]=='(' else -1)
    l = 0
    X = []
    while l < n:
        pos = 2*l
        t = 1
        best_x = 0
        while pos + t <= 2*n:
            if h[pos + t] == t:
                best_x = t
                t += 1
            elif h[pos + t] > t:
                t += 1
            else:
                break
        if best_x == 0:
            best_x = 1
        X.append(best_x)
        l += best_x
    bob = sum(j * X[j] for j in range(len(X)))
    return X, bob

def pair_seq(seq):
    res = []
    i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            res.append(1 + seq[i + 1])
            i += 2
        else:
            res.append(seq[i])
            i += 1
    return res

def alice_of(s):
    n = len(s)//2
    cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')':
                    cnt += 1
    return cnt

def solve_bruteforce(N, a_val, b_val):
    """Compute F[n] via brute-force over all words up to size N."""
    a_val %= MOD
    b_val %= MOD
    max_exp = N * N + N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * a_val % MOD
        pb[i] = pb[i-1] * b_val % MOD

    F_bf = [0] * (N + 1)
    for n in range(1, N + 1):
        words = generate_dyck(n)
        total = 0
        for s in words:
            al = alice_of(s)
            _, bob = x_seq_and_bob(s)
            total = (total + pa[al] * pb[bob]) % MOD
        F_bf[n] = total
    return F_bf

def compute_total_H(N, a_val, pa):
    """total_H[m] = sum_{|A|=m} a^{alice(A)} via Catalan recurrence:
    For word (A)B with |A|=t, |B|=m-1-t:
    alice = alice(A) + alice(B) + m + (t+1)(m-t-1)
    """
    total_H = [0] * (N + 1)
    total_H[0] = 1
    total_H[1] = pa[1]  # word "()" has alice=1
    
    for m in range(2, N + 1):
        s = 0
        for t in range(m):
            k = t + 1  # |(A)| = t+1
            exp = m + k * (m - k)
            contrib = total_H[t] * total_H[m - 1 - t] % MOD
            s = (s + pa[exp] * contrib) % MOD
        total_H[m] = s
    return total_H

def compute_H_orbit_dp(N, a_val, b_val):
    """Compute alpha_H[k] and beta_Q[k] for all k=0..N using recurrence.
    Returns:
      alpha_H: list of dicts, alpha_H[k][(bw, kw)] = sum of a^alice
      beta_Q:  list of dicts, beta_Q[k][(bp, kp)]  = sum of a^alice
      total_H: list of total a^alice per size
    """
    a_val %= MOD
    b_val %= MOD
    max_exp = N * N + N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * a_val % MOD
        pb[i] = pb[i-1] * b_val % MOD

    total_H = compute_total_H(N, a_val, pa)

    alpha_H = [{} for _ in range(N + 1)]
    beta_Q = [{} for _ in range(N + 1)]

    alpha_H[0][(0, 0)] = 1

    for k in range(1, N + 1):
        ah = {}
        bq = {}

        for key, coeff in alpha_H[k-1].items():
            bw_prev, kw_prev = key
            bw_new = (k) * (0) + bw_prev  # p=0, k→k
            kw_new = 0 + kw_prev

        # ---- H recurrences ----
        # H c=k (all 1's)
        t = k  # number of 1's in original X before wrapping
        t1 = t + 1  # total 1's after prepending [1]
        if t1 % 2 == 0:
            u = t1 // 2
            exp_bw = u * (u - 1)
            exp_kw = u
        else:
            u = t1 // 2
            exp_bw = u * u
            exp_kw = u + 1
        
        alice_all_ones = k + k*(k-1)//2
        ah[(exp_bw, exp_kw)] = (ah.get((exp_bw, exp_kw), 0) + pa[alice_all_ones]) % MOD

        # H c=0 (x1 >= 2)
        for x1 in range(2, k + 1):
            rest_size = k - x1
            if rest_size < 0:
                continue
            for (bp, kp), q_coeff in beta_Q[rest_size].items():
                bw = bp + (k - x1)
                kw = 1 + kp
                alice_contrib = 2 * x1 - 1 + x1 * (k - x1)
                contrib = pa[alice_contrib] * total_H[x1 - 1] % MOD * q_coeff % MOD
                ah[(bw, kw)] = (ah.get((bw, kw), 0) + contrib) % MOD

        # H c=2p (even, p >= 1)
        for p in range(1, k // 2 + 1):
            c = 2 * p
            rest_size = k - c
            if rest_size < 0:
                continue
            for (bw_rest, kw_rest), h_coeff in alpha_H[rest_size].items():
                bw = p * (k - p) + bw_rest
                kw = p + kw_rest
                alice_prefix = p * (2 * p + 1) + 2 * p * rest_size
                contrib = pa[alice_prefix] * h_coeff % MOD
                ah[(bw, kw)] = (ah.get((bw, kw), 0) + contrib) % MOD

        # H c=2p+1 (odd, p >= 0)
        for p in range(0, (k + 1) // 2):
            c = 2 * p + 1
            rest_size = k - c
            if rest_size < 0:
                continue
            for (bw_rest, kw_rest), h_coeff in alpha_H[rest_size].items():
                bw = (p + 1) * (k - p - 1) + bw_rest
                kw = p + 1 + kw_rest
                alice_prefix = (2 * p + 1) * (p + 1) + (2 * p + 1) * rest_size
                contrib = pa[alice_prefix] * h_coeff % MOD
                ah[(bw, kw)] = (ah.get((bw, kw), 0) + contrib) % MOD

        alpha_H[k] = ah

        # ---- Q recurrences ----
        # Q c=k (all 1's)
        if k % 2 == 0:
            p = k // 2
            exp_bp = p * (p - 1)
            exp_kp = p
        else:
            p = k // 2
            exp_bp = p * p
            exp_kp = p + 1
        alice_all_ones_q = k + k*(k-1)//2
        bq[(exp_bp, exp_kp)] = (bq.get((exp_bp, exp_kp), 0) + pa[alice_all_ones_q]) % MOD

        # Q c=0 (x1 >= 2): same structure as H c=0
        for x1 in range(2, k + 1):
            rest_size = k - x1
            if rest_size < 0:
                continue
            for (bp_rest, kp_rest), q_coeff in beta_Q[rest_size].items():
                bp = bp_rest + (k - x1)
                kp = 1 + kp_rest
                alice_contrib = 2 * x1 - 1 + x1 * (k - x1)
                contrib = pa[alice_contrib] * total_H[x1 - 1] % MOD * q_coeff % MOD
                bq[(bp, kp)] = (bq.get((bp, kp), 0) + contrib) % MOD

        # Q c=2p (even, p >= 1)
        for p in range(1, k // 2 + 1):
            c = 2 * p
            rest_size = k - c
            if rest_size < 0:
                continue
            for (bp_rest, kp_rest), q_coeff in beta_Q[rest_size].items():
                bp = bp_rest + p * (k - p - 1)
                kp = p + kp_rest
                alice_prefix = p * (2 * p + 1) + 2 * p * rest_size
                contrib = pa[alice_prefix] * q_coeff % MOD
                bq[(bp, kp)] = (bq.get((bp, kp), 0) + contrib) % MOD

        # Q c=2p+1 (odd, p >= 0): iterate over v
        for p in range(0, (k + 1) // 2):
            c = 2 * p + 1
            if c >= k:
                continue
            const_exp = (2 * p + 1) * (p + 1) - 1 + (2 * p + 1) * (k - 2 * p - 1)
            const_factor = pa[const_exp] % MOD
            
            max_v = k - 2 * p - 2
            for v in range(2, max_v + 1):
                t = k - 2 * p - 1 - v
                if t < 0:
                    continue
                
                v_dep_exp = v * (k - 2 * p + 1 - v)
                v_factor = pa[v_dep_exp] * total_H[v - 1] % MOD
                full_factor = const_factor * v_factor % MOD
                
                for (bp_rest, kp_rest), q_coeff in beta_Q[t].items():
                    bp = p * p + bp_rest + (p + 1) * (k - 2 * p - 1) - v
                    kp = p + 1 + kp_rest
                    contrib = full_factor * q_coeff % MOD
                    bq[(bp, kp)] = (bq.get((bp, kp), 0) + contrib) % MOD

        beta_Q[k] = bq

        # Verify orbit sets
        if k >= 2:
            q_set = set(bq.keys())
            h_prev_set = set(alpha_H[k-1].keys())
            if q_set != h_prev_set:
                print("WARNING k=%d: Q-orbit set != H[k-1] orbit set!" % k)
                print("  in Q not H:", q_set - h_prev_set)
                print("  in H not Q:", h_prev_set - q_set)

    return alpha_H, beta_Q, total_H, pa, pb

def compute_HkL(alpha_H, pb, N):
    """Compute H[k][L] = sum_{bw,kw} alpha_H[k][bw][kw] * b^{bw + kw*L}."""
    H = [None] * (N + 1)
    for k in range(N + 1):
        Lmax = N - k if N >= k else 0
        Hk = [0] * (Lmax + 1)
        for (bw, kw), coeff in alpha_H[k].items():
            base = coeff * pb[bw] % MOD
            if Lmax >= 0:
                cur = base
                step = pb[kw] if kw < len(pb) else 0
                for L in range(Lmax + 1):
                    Hk[L] = (Hk[L] + cur) % MOD
                    cur = cur * step % MOD
        H[k] = Hk
    return H

def compute_F(N, alpha_H, pa, pb):
    """Compute F[n] = sum_{m=1..n} a^{2m-1+m(n-m)} * H[m-1][n-m] * F[n-m]."""
    H = compute_HkL(alpha_H, pb, N)
    F = [0] * (N + 1)
    F[0] = 1
    for n in range(1, N + 1):
        total = 0
        for m in range(1, n + 1):
            k = m - 1
            L = n - m
            exp = 2 * m - 1 + m * (n - m)
            term = pa[exp] * H[k][L] % MOD * F[n - m] % MOD
            total = (total + term) % MOD
        F[n] = total
    return F

def verify(Nmax, a_val, b_val):
    print("Computing total_H and orbit coefficients...")
    alpha_H, beta_Q, total_H, pa, pb = compute_H_orbit_dp(Nmax, a_val, b_val)
    
    print("\nOrbit counts:")
    for k in range(0, Nmax + 1):
        if k == 0:
            print("k=%2d: H=%d Q=%d" % (k, len(alpha_H[k]), len(beta_Q[k])))
        else:
            print("k=%2d: H=%d Q=%d  |H[k-1]|=%d" % (k, len(alpha_H[k]), len(beta_Q[k]), 
                  len(alpha_H[k-1]) if k > 0 else 0))
    
    print("\nComputing F via H-orbit DP...")
    F_orbit = compute_F(Nmax, alpha_H, pa, pb)
    
    print("\nComputing F via brute force...")
    F_bf = solve_bruteforce(Nmax, a_val, b_val)
    
    print("\nComparison:")
    all_ok = True
    for n in range(1, Nmax + 1):
        match = "OK" if F_orbit[n] == F_bf[n] else "FAIL"
        if F_orbit[n] != F_bf[n]:
            all_ok = False
        print("  F[%2d] orbit=%d brute=%d %s" % (n, F_orbit[n], F_bf[n], match))
    
    if all_ok:
        print("\n*** ALL VERIFIED ***")
    else:
        print("\n*** FAILS FOUND ***")
    
    return all_ok, alpha_H, beta_Q, F_bf

if __name__ == '__main__':
    Nmax = 8
    a_val = 2
    b_val = 3
    ok, _, _, _ = verify(Nmax, a_val, b_val)
