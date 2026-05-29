# -*- coding: utf-8 -*-
"""H+Q recurrences v4 - fixed c=0 non-primitive with correct x1_word = 1+x1_A1.

Key fix: In c=0 non-primitive, A = (A1)·Rest.
  x1_word = X((A1))[0] = 1 + x1_A1.
  tail = X((A1))[1:] ++ X(Rest), sum = k - x1_word.
  bw = Q_bp + (k - x1_word), kw = 1 + Q_kp.
  where Q from Q[k - x1_word].
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
        key = (exp_bw, exp_kw, 1)
        if key not in ah:
            ah[key] = (0, None)
        coeff, _ = ah[key]
        ah[key] = (coeff + pa[alice_all] % MOD, None)

        # === H c=0: non-primitive A=(A1)·Rest, use x1_word = 1+x1_A1 ===
        for s in range(1, k - 1):  # s = |A1| >= 1, rest_size >= 1
            rest_size = k - s - 1
            if rest_size <= 0:
                continue
            
            for (bw_A1, kw_A1, c_A1), (coeff_A1, x1sub_A1) in alpha_H[s].items():
                if c_A1 >= 1:
                    x1_A1_vals = [(1, coeff_A1)]
                else:
                    x1_A1_vals = [(x1, c) for x1, c in x1sub_A1.items()] if x1sub_A1 else []
                
                for x1_A1, a1_contrib in x1_A1_vals:
                    if a1_contrib == 0:
                        continue
                    
                    x1_word = 1 + x1_A1  # actual first x_seq element
                    tail_size = k - x1_word
                    if tail_size < 0:
                        continue
                    
                    for (bp_tail, kp_tail, c_t), (q_coeff, _) in beta_Q[tail_size].items():
                        bw = bp_tail + tail_size  # = bp_tail + (k - x1_word)
                        kw = 1 + kp_tail
                        
                        alice_extra = 2 * s + 1 + (s + 1) * rest_size
                        contrib = pa[alice_extra] * a1_contrib % MOD * q_coeff % MOD
                        
                        key = (bw, kw, 0)
                        if key not in ah:
                            ah[key] = (0, {})
                        total_c, x1_dict = ah[key]
                        x1_dict[x1_word] = (x1_dict.get(x1_word, 0) + contrib) % MOD
                        ah[key] = ((total_c + contrib) % MOD, x1_dict)

        # === H c=0: primitive A=(T), x1_word = 1+t1 ===
        if k - 1 >= 0:
            for (bw_T, kw_T, c_T), (coeff_T, x1sub_T) in alpha_H[k-1].items():
                if c_T >= 1:
                    t1_vals = [(1, coeff_T)]
                else:
                    t1_vals = [(t1, c) for t1, c in x1sub_T.items()] if x1sub_T else []
                
                for t1, t_contrib in t1_vals:
                    if t_contrib == 0:
                        continue
                    tail_size = k - 1 - t1
                    if tail_size < 0:
                        continue
                    
                    # For c_T >= 1: determine c_tail to filter Q entries
                    if c_T >= 1:
                        if k - 1 == c_T:
                            c_tail_group = 1  # all 1's: c_tail >= 1
                        else:
                            c_tail_group = 0  # rest word has c=0
                        use_filter = True
                    else:
                        use_filter = False  # c_T=0: need c_tail tracking (not yet)
                    
                    for (bp_tail, kp_tail, c_t), (q_coeff, _) in beta_Q[tail_size].items():
                        if use_filter and c_t != c_tail_group:
                            continue
                        bw = bp_tail + tail_size
                        kw = 1 + kp_tail
                        alice_A = 2 * k - 1
                        contrib = pa[alice_A] * t_contrib % MOD
                        
                        key = (bw, kw, 0)
                        if key not in ah:
                            ah[key] = (0, {})
                        total_c, x1_dict = ah[key]
                        x1_A = 1 + t1
                        x1_dict[x1_A] = (x1_dict.get(x1_A, 0) + contrib) % MOD
                        ah[key] = ((total_c + contrib) % MOD, x1_dict)

        # === H c=2p (even): rest must have c=0 ===
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

        # === H c=2p+1 (odd): rest must have c=0 ===
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

        # === Q c=0: non-primitive with correct x1_word ===
        for s in range(1, k - 1):
            rest_size = k - s - 1
            if rest_size <= 0:
                continue
            for (bw_A1, kw_A1, c_A1), (coeff_A1, x1sub_A1) in alpha_H[s].items():
                if c_A1 >= 1:
                    x1_A1_vals = [(1, coeff_A1)]
                else:
                    x1_A1_vals = [(x1, c) for x1, c in x1sub_A1.items()] if x1sub_A1 else []
                
                for x1_A1, a1_contrib in x1_A1_vals:
                    if a1_contrib == 0:
                        continue
                    x1_word_q = 1 + x1_A1
                    tail_size = k - x1_word_q
                    if tail_size < 0:
                        continue
                    for (bp_tail, kp_tail, _), (q_coeff, _) in beta_Q[tail_size].items():
                        bp = bp_tail + tail_size
                        kp = 1 + kp_tail
                        alice_extra = 2 * s + 1 + (s + 1) * rest_size
                        contrib = pa[alice_extra] * a1_contrib % MOD * q_coeff % MOD
                        
                        key = (bp, kp, 0)
                        if key not in bq:
                            bq[key] = (0, {})
                        total_c, x1_dict = bq[key]
                        x1_dict[x1_word_q] = (x1_dict.get(x1_word_q, 0) + contrib) % MOD
                        bq[key] = ((total_c + contrib) % MOD, x1_dict)

        # === Q c=0: primitive ===
        if k - 1 >= 0:
            for (bw_T, kw_T, c_T), (coeff_T, x1sub_T) in alpha_H[k-1].items():
                if c_T >= 1:
                    t1_vals = [(1, coeff_T)]
                else:
                    t1_vals = [(t1, c) for t1, c in x1sub_T.items()] if x1sub_T else []
                
                for t1, t_contrib in t1_vals:
                    if t_contrib == 0:
                        continue
                    tail_size = k - 1 - t1
                    if tail_size < 0:
                        continue
                    
                    if c_T >= 1:
                        if k - 1 == c_T:
                            c_tail_group = 1
                        else:
                            c_tail_group = 0
                        use_filter = True
                    else:
                        use_filter = False
                    
                    for (bp_tail, kp_tail, c_t), (q_coeff, _) in beta_Q[tail_size].items():
                        if use_filter and c_t != c_tail_group:
                            continue
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
    
    print("Computing split-orbit DP v4 (fixed c=0 x1_word)...")
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
    
    print("\nVerifying H[k] against brute force:")
    all_h_ok = True
    for k in range(1, Nmax + 1):
        words = generate_dyck(k)
        Hbf = {}
        for A in words:
            X, _ = x_seq_and_bob(A)
            Xw = pair_seq([1]+X)
            bw = sum((j-1)*Xw[j-1] for j in range(1,len(Xw)+1))
            kw = len(Xw)
            al = alice_of(A)
            Hbf[(bw,kw)] = Hbf.get((bw,kw),0) + pa[al]
        
        Hdp_comb = {}
        for (bw,kw,_), (coeff,_) in alpha_H[k].items():
            Hdp_comb[(bw,kw)] = Hdp_comb.get((bw,kw),0) + coeff
        
        h_ok = True
        for (bw,kw), bfv in sorted(Hbf.items()):
            dpv = Hdp_comb.get((bw,kw),0)%MOD
            if dpv != bfv%MOD:
                if h_ok:
                    print("k=%d FAILS:" % k)
                h_ok = False
                all_h_ok = False
                print("  bw=%d kw=%d: DP=%d BF=%d diff=%d" % (bw,kw,dpv,bfv%MOD,(dpv-bfv)%MOD))
        if h_ok:
            print("k=%d: ALL OK" % k)
    
    if all_h_ok:
        print("\nAll H[k] orbits correct!")

    print("\nComputing F...")
    F_orbit = compute_F_from_split(alpha_H, pa, pb, Nmax)
    F_bf, _, _ = solve_bruteforce(Nmax, a_val, b_val)
    
    print("\nF comparison:")
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
