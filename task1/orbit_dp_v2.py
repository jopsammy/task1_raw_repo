# -*- coding: utf-8 -*-
"""H+Q recurrences with c-flag and x1 tracking for correct alice computation.

Key fixes:
1. Orbits split by c_flag: 0 (c=0, x1>=2) vs 1 (c>=1, x1=1)
2. For c=0 orbits, track x1 distribution
3. Primitive c=0 words handled separately: A=(T), wrap via T from H[k-1]
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
    return F_bf, pa, pb

def compute_total_H(N, a_val, pa):
    total_H = [0] * (N + 1)
    total_H[0] = 1
    total_H[1] = pa[1]
    for m in range(2, N + 1):
        s = 0
        for t in range(m):
            k = t + 1
            exp = m * k - t * t
            contrib = total_H[t] * total_H[m - 1 - t] % MOD
            s = (s + pa[exp] * contrib) % MOD
        total_H[m] = s
    return total_H

def compute_H_orbit_split(N, a_val, b_val):
    """Compute H/Q orbits split by c_flag and x1.
    
    For each k, alpha_H[k] is a dict: (bw, kw, c_flag) → (coeff, x1_sub if c_flag=0)
    where x1_sub maps x1 → coefficient for c=0 orbits.
    For c_flag=1: x1=1 always, no x1_sub needed.
    
    beta_Q[k] similarly.
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

    # alpha_H[k][(bw,kw,c_flag)] = (total_coeff, x1_dict if c_flag==0 else None)
    # beta_Q[k][(bp,kp,c_flag)] = similarly
    alpha_H = [{} for _ in range(N + 1)]
    beta_Q = [{} for _ in range(N + 1)]

    # H[0]: empty word wrapping = "()" → bobw=0, kw=1, alice=0
    alpha_H[0][(0, 1, 1)] = (1, None)
    beta_Q[0][(0, 0, 1)] = (1, None)

    for k in range(1, N + 1):
        ah = {}
        bq = {}

        # === H c=k (all 1's) ===
        t = k + 1
        if t % 2 == 0:
            u = t // 2
            exp_bw = u * (u - 1)
            exp_kw = u
        else:
            u = t // 2
            exp_bw = u * u
            exp_kw = u + 1
        alice_all = k + k*(k-1)//2
        key = (exp_bw, exp_kw, 1)  # c>=1 since all 1's and x1=1
        if key not in ah:
            ah[key] = (0, None)
        coeff, _ = ah[key]
        ah[key] = (coeff + pa[alice_all] % MOD, None)

        # === H c=0: non-primitive case (x1 >= 2, first block returns to height 0, rest_size > 0) ===
        for x1 in range(2, k):
            rest_size = k - x1
            if rest_size <= 0:
                continue
            for (bp, kp, c_q), (q_coeff, x1sub_q) in beta_Q[rest_size].items():
                bw = bp + (k - x1)
                kw = 1 + kp
                alice_contrib = 2 * x1 - 1 + x1 * (k - x1)
                contrib = pa[alice_contrib] * total_H[x1 - 1] % MOD * q_coeff % MOD
                
                key = (bw, kw, 0)
                if key not in ah:
                    ah[key] = (0, {})
                total_c, x1_dict = ah[key]
                x1_dict[x1] = (x1_dict.get(x1, 0) + contrib) % MOD
                ah[key] = ((total_c + contrib) % MOD, x1_dict)

        # === H c=0: primitive case (word is (T) where T has size k-1) ===
        # alice = alice(T) + 2*k - 1
        # X(A) = pair_seq([1] + X(T))
        # t1 = X(T)[0]
        for (bw_T, kw_T, c_T), (coeff_T, x1sub_T) in alpha_H[k-1].items():
            if c_T >= 1:
                t1_vals = [1]
            else:
                # c_T = 0: t1 >= 2, iterate over x1 values from x1sub_T
                t1_vals = list(x1sub_T.keys()) if x1sub_T else []
            
            for t1 in t1_vals:
                tail_size = k - 1 - t1
                if tail_size < 0:
                    continue
                
                # Contribution from T with this t1 value
                if c_T >= 1:
                    t_contrib = coeff_T  # all T words with c_T>=1 have x1=1
                else:
                    t_contrib = x1sub_T.get(t1, 0)
                if t_contrib == 0:
                    continue

                for (bp_tail, kp_tail, _), (q_coeff, _) in beta_Q[tail_size].items():
                    bw = bp_tail + tail_size
                    kw = 1 + kp_tail
                    alice_A = 2 * k - 1
                    contrib = pa[alice_A] * t_contrib % MOD
                    
                    key = (bw, kw, 0)  # primitive c=0 word
                    if key not in ah:
                        ah[key] = (0, {})
                    total_c, x1_dict = ah[key]
                    x1_A = 1 + t1  # x1 of primitive word A = (T)
                    x1_dict[x1_A] = (x1_dict.get(x1_A, 0) + contrib) % MOD
                    ah[key] = ((total_c + contrib) % MOD, x1_dict)

        # === H c=2p (even): rest must have c=0 (first non-1 after leading 1's) ===
        for p in range(1, k // 2 + 1):
            c = 2 * p
            rest_size = k - c
            if rest_size <= 0:
                continue
            for (bw_rest, kw_rest, c_rest), (coeff_rest, _) in alpha_H[rest_size].items():
                if c_rest != 0:
                    continue
                bw = p * (k - p) + bw_rest
                kw = p + kw_rest
                alice_prefix = p * (2 * p + 1) + 2 * p * rest_size
                contrib = pa[alice_prefix] * coeff_rest % MOD
                
                key = (bw, kw, 1)
                if key not in ah:
                    ah[key] = (0, None)
                total_c, _ = ah[key]
                ah[key] = ((total_c + contrib) % MOD, None)

        # === H c=2p+1 (odd): rest must have c=0 (first non-1 after leading 1's) ===
        for p in range(0, (k + 1) // 2):
            c = 2 * p + 1
            rest_size = k - c
            if rest_size <= 0:
                continue
            for (bw_rest, kw_rest, c_rest), (coeff_rest, _) in alpha_H[rest_size].items():
                if c_rest != 0:
                    continue
                bw = (p + 1) * (k - p - 1) + bw_rest
                kw = p + 1 + kw_rest
                alice_prefix = (2 * p + 1) * (p + 1) + (2 * p + 1) * rest_size
                contrib = pa[alice_prefix] * coeff_rest % MOD
                
                key = (bw, kw, 1)
                if key not in ah:
                    ah[key] = (0, None)
                total_c, _ = ah[key]
                ah[key] = ((total_c + contrib) % MOD, None)

        alpha_H[k] = ah

        # === Q c=k (all 1's) ===
        if k % 2 == 0:
            p = k // 2
            exp_bp = p * (p - 1)
            exp_kp = p
        else:
            p = k // 2
            exp_bp = p * p
            exp_kp = p + 1
        alice_all_q = k + k*(k-1)//2
        key = (exp_bp, exp_kp, 1)
        if key not in bq:
            bq[key] = (0, None)
        coeff, _ = bq[key]
        bq[key] = ((coeff + pa[alice_all_q]) % MOD, None)

        # === Q c=0: non-primitive (rest_size > 0) ===
        for x1 in range(2, k):
            rest_size = k - x1
            if rest_size <= 0:
                continue
            for (bp_rest, kp_rest, _), (q_coeff, _) in beta_Q[rest_size].items():
                bp = bp_rest + (k - x1)
                kp = 1 + kp_rest
                alice_contrib = 2 * x1 - 1 + x1 * (k - x1)
                contrib = pa[alice_contrib] * total_H[x1 - 1] % MOD * q_coeff % MOD
                
                key = (bp, kp, 0)
                if key not in bq:
                    bq[key] = (0, {})
                total_c, x1_dict = bq[key]
                x1_dict[x1] = (x1_dict.get(x1, 0) + contrib) % MOD
                bq[key] = ((total_c + contrib) % MOD, x1_dict)

        # === Q c=0: primitive ===
        if k-1 >= 0:
            for (bw_T, kw_T, c_T), (coeff_T, x1sub_T) in alpha_H[k-1].items():
                if c_T >= 1:
                    t1_vals = [1]
                else:
                    t1_vals = list(x1sub_T.keys()) if x1sub_T else []
                
                for t1 in t1_vals:
                    tail_size = k - 1 - t1
                    if tail_size < 0:
                        continue
                    
                    if c_T >= 1:
                        t_contrib = coeff_T
                    else:
                        t_contrib = x1sub_T.get(t1, 0)
                    if t_contrib == 0:
                        continue
                    
                    for (bp_tail, kp_tail, _), (q_coeff, _) in beta_Q[tail_size].items():
                        bp = bp_tail + tail_size
                        kp = 1 + kp_tail
                        alice_A = 2 * k - 1
                        contrib = pa[alice_A] * t_contrib % MOD
                        
                        key = (bp, kp, 0)
                        if key not in bq:
                            bq[key] = (0, {})
                        total_c, x1_dict = bq[key]
                        x1_A_Q = 1 + t1
                        x1_dict[x1_A_Q] = (x1_dict.get(x1_A_Q, 0) + contrib) % MOD
                        bq[key] = ((total_c + contrib) % MOD, x1_dict)

        # === Q c=2p (even): rest must have c=0 ===
        for p in range(1, k // 2 + 1):
            c = 2 * p
            rest_size = k - c
            if rest_size <= 0:
                continue
            for (bp_rest, kp_rest, c_rest), (q_coeff, _) in beta_Q[rest_size].items():
                if c_rest != 0:
                    continue
                bp = bp_rest + p * (k - p - 1)
                kp = p + kp_rest
                alice_prefix = p * (2 * p + 1) + 2 * p * rest_size
                contrib = pa[alice_prefix] * q_coeff % MOD
                
                key = (bp, kp, 1)
                if key not in bq:
                    bq[key] = (0, None)
                total_c, _ = bq[key]
                bq[key] = ((total_c + contrib) % MOD, None)

        # === Q c=2p+1 (odd) ===
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
                
                for (bp_rest, kp_rest, _), (q_coeff, _) in beta_Q[t].items():
                    bp = p * p + bp_rest + (p + 1) * (k - 2 * p - 1) - v
                    kp = p + 1 + kp_rest
                    contrib = full_factor * q_coeff % MOD
                    
                    key = (bp, kp, 1)
                    if key not in bq:
                        bq[key] = (0, None)
                    total_c, _ = bq[key]
                    bq[key] = ((total_c + contrib) % MOD, None)

        beta_Q[k] = bq

    return alpha_H, beta_Q, total_H, pa, pb

def compute_HkL_from_split(alpha_H, pb, N):
    H = [None] * (N + 1)
    for k in range(N + 1):
        Lmax = N - k
        Hk = [0] * (Lmax + 1)
        for (bw, kw, _), (coeff, _) in alpha_H[k].items():
            base = coeff * pb[bw] % MOD
            if Lmax >= 0:
                cur = base
                for L in range(Lmax + 1):
                    Hk[L] = (Hk[L] + cur) % MOD
                    cur = cur * pb[kw] % MOD
        H[k] = Hk
    return H

def compute_F_from_split(alpha_H, pa, pb, N):
    H = compute_HkL_from_split(alpha_H, pb, N)
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

if __name__ == '__main__':
    Nmax = 8
    a_val = 2
    b_val = 3
    
    print("Computing split-orbit DP...")
    alpha_H, beta_Q, total_H, pa, pb = compute_H_orbit_split(Nmax, a_val, b_val)
    
    print("\nOrbit counts (split by c_flag):")
    for k in range(0, Nmax + 1):
        if k == 0:
            print("k=%2d: H=%d Q=%d" % (k, len(alpha_H[k]), len(beta_Q[k])))
        else:
            c0_h = sum(1 for (_, _, c) in alpha_H[k] if c == 0)
            c1_h = sum(1 for (_, _, c) in alpha_H[k] if c == 1)
            c0_q = sum(1 for (_, _, c) in beta_Q[k] if c == 0)
            c1_q = sum(1 for (_, _, c) in beta_Q[k] if c == 1)
            print("k=%2d: H=%d(c0:%d,c1:%d) Q=%d(c0:%d,c1:%d)" % 
                  (k, len(alpha_H[k]), c0_h, c1_h, len(beta_Q[k]), c0_q, c1_q))
    
    print("\nComputing F via split-orbit DP...")
    F_orbit = compute_F_from_split(alpha_H, pa, pb, Nmax)
    
    print("Computing F via brute force...")
    F_bf, _, _ = solve_bruteforce(Nmax, a_val, b_val)
    
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
