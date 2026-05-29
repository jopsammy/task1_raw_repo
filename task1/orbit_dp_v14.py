# -*- coding: utf-8 -*-
"""H+Q recurrences v14: Fix primitive c=0 xs[0] filter: use t1+1 (wrapping offset).

KEY: H entries store X((A)) (wrapped x_seq). x₁ of X((A)) = x₁ of X(A) + 1.
So when filtering by t1 (= x₁ of X(T)), compare xs[0] with t1+1.
"""
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

def dyck_from_xseq(X):
    s = ''
    for xx in X:
        s += '(' * xx + ')' * xx
    return s

def solve_bruteforce(N, a_val, b_val):
    a_val %= MOD; b_val %= MOD
    max_exp = N * N + N + 5
    pa = [1] * (max_exp + 1); pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1): pa[i] = pa[i-1] * a_val % MOD; pb[i] = pb[i-1] * b_val % MOD
    F_bf = [0] * (N + 1)
    for n in range(1, N + 1):
        words = generate_dyck(n); total = 0
        for s in words:
            al = alice_of(s); _, bob = x_seq_and_bob(s)
            total = (total + pa[al] * pb[bob]) % MOD
        F_bf[n] = total
    return F_bf, pa, pb

def compute_total_H(N, a_val, pa):
    total_H = [0] * (N + 1); total_H[0] = 1; total_H[1] = pa[1]
    for m in range(2, N + 1):
        s = 0
        for t in range(m):
            k = t + 1; exp = m * k - t * t
            contrib = total_H[t] * total_H[m - 1 - t] % MOD
            s = (s + pa[exp] * contrib) % MOD
        total_H[m] = s
    return total_H

def make_H_key(bw, kw, c_flag, all1, c_tail):
    return (bw, kw, c_flag, all1, c_tail)

def make_Q_key(bp, kp, c_flag, all1):
    return (bp, kp, c_flag, all1)

def compute_XwT_real(x_seq_T):
    s_T = dyck_from_xseq(x_seq_T)
    T_wrapped = '(' + s_T + ')'
    X_real, _ = x_seq_and_bob(T_wrapped)
    return tuple(X_real)

def all1_wrapped_xseq(k):
    """Compute X((A)) for A = '()'*k (all leading 1s)."""
    t = k + 1
    if t % 2 == 0:
        return tuple([2] * (t // 2))
    else:
        return tuple([2] * (t // 2) + [1])

def add_to_orbit(orbit_dict, key, contrib, x1_val, ct_val, xseq_tuple=None):
    if key not in orbit_dict:
        orbit_dict[key] = (0, {}, [])
    tc, xd, xs_l = orbit_dict[key]
    xd[(x1_val, ct_val)] = (xd.get((x1_val, ct_val), 0) + contrib) % MOD
    if xseq_tuple is not None:
        found = False
        for i, (xt, cc) in enumerate(xs_l):
            if xt == xseq_tuple:
                xs_l[i] = (xt, (cc + contrib) % MOD)
                found = True
                break
        if not found:
            xs_l.append((xseq_tuple, contrib % MOD))
    orbit_dict[key] = ((tc + contrib) % MOD, xd, xs_l)

def compute_H_real_BF(N, a_val, b_val):
    a_val %= MOD; b_val %= MOD
    max_exp = N * N + N + 5
    pa = [1] * (max_exp + 1); pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1): pa[i] = pa[i-1] * a_val % MOD; pb[i] = pb[i-1] * b_val % MOD
    H_bf = [{} for _ in range(N + 1)]
    for k in range(N + 1):
        words = generate_dyck(k)
        for A in words:
            al = alice_of(A)
            Xw_real, _ = x_seq_and_bob('(' + A + ')')
            bw = sum(j * Xw_real[j] for j in range(len(Xw_real)))
            kw = len(Xw_real)
            H_bf[k][(bw, kw)] = (H_bf[k].get((bw, kw), 0) + pa[al]) % MOD
    return H_bf, pa, pb

def compute_H_orbit_split(N, a_val, b_val):
    a_val %= MOD; b_val %= MOD
    max_exp = N * N + N + 5
    pa = [1] * (max_exp + 1); pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1): pa[i] = pa[i-1] * a_val % MOD; pb[i] = pb[i-1] * b_val % MOD
    total_H = compute_total_H(N, a_val, pa)

    alpha_H = [{} for _ in range(N + 1)]
    beta_Q = [{} for _ in range(N + 1)]

    alpha_H[0][make_H_key(0, 1, 1, 0, None)] = (1, None, [(tuple(), 1)])
    beta_Q[0][make_Q_key(0, 0, 0, 0)] = (1, None, [(tuple(), 1)])
    beta_Q[0][make_Q_key(0, 0, 1, 0)] = (1, None, [(tuple(), 1)])

    for k in range(1, N + 1):
        ah = {}; bq = {}

        # === H c=k (all 1's): xseq = X((A)) ===
        t = k + 1
        if t % 2 == 0: u = t // 2; exp_bw = u * (u - 1); exp_kw = u
        else: u = t // 2; exp_bw = u * u; exp_kw = u + 1
        alice_all = k + k*(k-1)//2
        key = make_H_key(exp_bw, exp_kw, 1, 1, None)
        xseq_wrapped = all1_wrapped_xseq(k)
        if key not in ah: ah[key] = (0, None, [])
        c, _, xs = ah[key]; xs.append((xseq_wrapped, pa[alice_all] % MOD))
        ah[key] = (c + pa[alice_all] % MOD, None, xs)

        # === H c=0: non-primitive ===
        for s in range(1, k - 1):
            rest_size = k - s - 1
            if rest_size <= 0: continue
            for hkey, (coeff_A1, x1sub_A1, xseqs_A1) in alpha_H[s].items():
                bw_A1, kw_A1, c_A1, all1_A1, ct_A1 = hkey
                if c_A1 >= 1: x1A_vals = [(1, coeff_A1)]
                else: x1A_vals = [(x1, c) for (x1, _), c in x1sub_A1.items()] if x1sub_A1 else []
                for x1_A1, a1c in x1A_vals:
                    if a1c == 0: continue
                    x1_word = 1 + x1_A1
                    alice_extra = 2*s + 1 + (s+1)*rest_size
                    base_contrib = pa[alice_extra] * a1c % MOD

                    if kw_A1 == 1:
                        for qkey, (q_coeff, _, _) in beta_Q[rest_size].items():
                            bp_t, kp_t, c_tail_q, _ = qkey
                            bw = bp_t + (k - x1_word)
                            kw = 1 + kp_t
                            contrib = base_contrib * q_coeff % MOD
                            add_to_orbit(ah, make_H_key(bw, kw, 0, 0, c_tail_q), contrib, x1_word, c_tail_q)

                    elif s - x1_A1 == 1:
                        for rkey, (coeff_Rw, _, xseqs_Rw) in alpha_H[rest_size].items():
                            bw_Rw, kw_Rw, _, _, _ = rkey
                            bw = bw_Rw + (rest_size + 1)
                            kw = 1 + kw_Rw
                            contrib = base_contrib * coeff_Rw % MOD
                            add_to_orbit(ah, make_H_key(bw, kw, 0, 0, 1), contrib, x1_word, 1)
                            # x_seq propagation: X((T)) = X((A1)) ++ X((B))
                            if xseqs_A1 and xseqs_Rw:
                                inv_c_a1 = pow(coeff_A1, MOD-2, MOD)
                                inv_c_b = pow(coeff_Rw, MOD-2, MOD)
                                for xs_a1, ca1 in xseqs_A1:
                                    for xs_b, cb in xseqs_Rw:
                                        full_xs = xs_a1 + xs_b
                                        xc = contrib * ca1 % MOD * inv_c_a1 % MOD
                                        xc = xc * cb % MOD * inv_c_b % MOD
                                        add_to_orbit(ah, make_H_key(bw, kw, 0, 0, 1), 0, x1_word, 1, full_xs)

                    else:
                        t_bob = bw_A1 - s + x1_A1
                        t_kk = kw_A1 - 1
                        t_sum = s - x1_A1
                        for qkey, (q_coeff, _, _) in beta_Q[rest_size].items():
                            bp_q, kp_q, _, _ = qkey
                            tail_bob = t_bob + bp_q + t_kk * rest_size
                            tail_kw = t_kk + kp_q
                            bw = tail_bob + t_sum + rest_size
                            kw = kw_A1 + kp_q
                            contrib = base_contrib * q_coeff % MOD
                            add_to_orbit(ah, make_H_key(bw, kw, 0, 0, 0), contrib, x1_word, 0)

        # === H c=0: primitive — FIXED filter: xs[0] == t1+1 (wrapping offset) ===
        if k - 1 >= 0:
            s_T = k - 1
            for hkey, (coeff_T, x1sub_T, xseqs_T) in alpha_H[s_T].items():
                bw_T, kw_T, c_T, all1_T, ct_T = hkey
                if c_T >= 1:
                    t1_vals = [(1, coeff_T, None)]
                else:
                    t1_vals = [(x1, c, ct) for (x1, ct), c in x1sub_T.items()] if x1sub_T else []

                for t1, tc, ct_T_val in t1_vals:
                    if tc == 0: continue
                    tail_size = k - 1 - t1
                    if tail_size < 0: continue

                    alice_A = 2*k - 1

                    xseq_total = sum(c for xs_t, c in (xseqs_T or [])) % MOD
                    use_xseq = False  # DISABLED: compute_XwT_real is not injective on X((T))

                    if use_xseq:
                        xseq_map = {}
                        for xs_tuple, c_xs in xseqs_T:
                            xs_list = list(xs_tuple)
                            # xs = X((T)), t1 = x₁(X(T)). xs[0] = t1 + 1
                            if xs_list[0] != t1 + 1: continue
                            Xw_A_real = compute_XwT_real(xs_list)
                            prev_c = xseq_map.get(Xw_A_real, 0)
                            xseq_map[Xw_A_real] = (prev_c + c_xs) % MOD

                        for Xw_A_seq, xt_coeff in xseq_map.items():
                            Xw_A_list = list(Xw_A_seq)
                            bw_A = sum(j * Xw_A_list[j] for j in range(len(Xw_A_list)))
                            kw_A = len(Xw_A_list)
                            ct_new = 0
                            if len(Xw_A_list) > 1:
                                ct = 0
                                for xx in Xw_A_list[1:]:
                                    if xx == 1: ct += 1
                                    else: break
                                ct_new = 1 if ct >= 1 else 0
                            # x1_A = x₁ of X(A) (unwrapped), NOT x₁ of X((A))
                            # A = (T), x₁(A) = t1+1 (for c_T=0) or 2 (for c_T≥1)
                            if c_T >= 1:
                                x1_A = 2
                            else:
                                x1_A = t1 + 1
                            contrib = pa[alice_A] * xt_coeff % MOD
                            add_to_orbit(ah, make_H_key(bw_A, kw_A, 0, 0, ct_new), contrib, x1_A, ct_new, Xw_A_seq)
                    else:
                        ct_new = 1 if s_T - t1 == 1 else 0
                        bp_expected = bw_T - s_T + t1
                        kp_expected = kw_T - 1
                        for qkey, (q_coeff, _, _) in beta_Q[tail_size].items():
                            bp_t, kp_t, cq, aq = qkey
                            if bp_t != bp_expected or kp_t != kp_expected: continue
                            if c_T >= 1:
                                c_tail_group = 1 if all1_T == 1 else 0
                                if cq != c_tail_group: continue
                            else:
                                c_tail_group = ct_T_val if ct_T_val is not None else 0
                                if cq != c_tail_group: continue
                            bw = bp_t + tail_size; kw = 1 + kp_t
                            contrib = pa[alice_A] * tc % MOD
                            add_to_orbit(ah, make_H_key(bw, kw, 0, 0, ct_new), contrib, 1 + t1, ct_new)

        # === H c=2p (even): X((T)) = [2]*p + [1+X((rest))[0]] + X((rest))[1:] ===
        for p in range(1, k//2 + 1):
            c = 2*p; rest_size = k - c
            if rest_size <= 0: continue
            for hkey, (coeff_r, _, xseqs_r) in alpha_H[rest_size].items():
                bw_r, kw_r, c_r, a_r, ct_r = hkey
                if c_r != 0 or a_r != 0: continue
                bw = p*(k-p) + bw_r; kw = p + kw_r
                alice_prefix = p*(2*p+1) + 2*p*rest_size
                contrib = pa[alice_prefix] * coeff_r % MOD
                key = make_H_key(bw, kw, 1, 0, None)
                if key not in ah: ah[key] = (0, None, [])
                tc, _, xs = ah[key]
                lead_twos = tuple([2]*p)
                if xseqs_r:
                    inv_cr = pow(coeff_r, MOD-2, MOD)
                    for xs_r, cr in xseqs_r:
                        if xs_r:
                            full_xs = lead_twos + (1 + xs_r[0],) + xs_r[1:]
                        else:
                            full_xs = lead_twos
                        xs.append((full_xs, contrib * cr % MOD * inv_cr % MOD))
                ah[key] = ((tc+contrib)%MOD, None, xs)

        # === H c=2p+1 (odd): X((T)) = [2]*(p+1) + X((rest)) ===
        for p in range(0, (k+1)//2):
            c = 2*p+1; rest_size = k - c
            if rest_size <= 0: continue
            for hkey, (coeff_r, _, xseqs_r) in alpha_H[rest_size].items():
                bw_r, kw_r, c_r, a_r, ct_r = hkey
                if c_r != 0 or a_r != 0: continue
                bw = (p+1)*(k-p-1) + bw_r; kw = p+1 + kw_r
                alice_prefix = (2*p+1)*(p+1) + (2*p+1)*rest_size
                contrib = pa[alice_prefix] * coeff_r % MOD
                key = make_H_key(bw, kw, 1, 0, None)
                if key not in ah: ah[key] = (0, None, [])
                tc, _, xs = ah[key]
                lead_twos = tuple([2]*(p+1))
                if xseqs_r:
                    inv_cr = pow(coeff_r, MOD-2, MOD)
                    for xs_r, cr in xseqs_r:
                        full_xs = lead_twos + xs_r
                        xs.append((full_xs, contrib * cr % MOD * inv_cr % MOD))
                ah[key] = ((tc+contrib)%MOD, None, xs)

        alpha_H[k] = ah

        # === Q (same as v13) ===
        # === Q c=k ===
        if k % 2 == 0: p = k//2; exp_bp = p*(p-1); exp_kp = p
        else: p = k//2; exp_bp = p*p; exp_kp = p+1
        alice_all_q = k + k*(k-1)//2
        key = make_Q_key(exp_bp, exp_kp, 1, 1)
        if key not in bq: bq[key] = (0, None, [])
        c, _, xs = bq[key]; bq[key] = ((c + pa[alice_all_q])%MOD, None, xs)

        # === Q c=0: non-primitive ===
        for s in range(1, k - 1):
            rest_size = k - s - 1
            if rest_size <= 0: continue
            for hkey, (coeff_A1, x1sub_A1, _) in alpha_H[s].items():
                bw_A1, kw_A1, c_A1, all1_A1, ct_A1 = hkey
                if c_A1 >= 1: x1A_vals = [(1, coeff_A1)]
                else: x1A_vals = [(x1, c) for (x1, _), c in x1sub_A1.items()] if x1sub_A1 else []
                for x1_A1, a1c in x1A_vals:
                    if a1c == 0: continue
                    x1_word = 1 + x1_A1
                    alice_extra = 2*s + 1 + (s+1)*rest_size
                    base_contrib = pa[alice_extra] * a1c % MOD
                    if kw_A1 == 1:
                        for qkey, (q_coeff, _, _) in beta_Q[rest_size].items():
                            bp_t, kp_t, _, _ = qkey
                            bp = bp_t + (k - x1_word); kp = 1 + kp_t
                            contrib = base_contrib * q_coeff % MOD
                            key = make_Q_key(bp, kp, 0, 0)
                            if key not in bq: bq[key] = (0, {}, [])
                            tc, xd, xs = bq[key]
                            prev = xd.get(x1_word, 0); xd[x1_word] = (prev + contrib) % MOD
                            bq[key] = ((tc+contrib)%MOD, xd, xs)
                    elif s - x1_A1 == 1:
                        for rkey, (coeff_Rw, _, _) in alpha_H[rest_size].items():
                            bw_Rw, kw_Rw, _, _, _ = rkey
                            bp = bw_Rw; kp = kw_Rw
                            contrib = base_contrib * coeff_Rw % MOD
                            key = make_Q_key(bp, kp, 0, 0)
                            if key not in bq: bq[key] = (0, {}, [])
                            tc, xd, xs = bq[key]
                            prev = xd.get(x1_word, 0); xd[x1_word] = (prev + contrib) % MOD
                            bq[key] = ((tc+contrib)%MOD, xd, xs)
                    else:
                        t_bob = bw_A1 - s + x1_A1; t_kk = kw_A1 - 1
                        for qkey, (q_coeff, _, _) in beta_Q[rest_size].items():
                            bp_q, kp_q, _, _ = qkey
                            tail_bob = t_bob + bp_q + t_kk * rest_size
                            tail_kw = t_kk + kp_q
                            bp = tail_bob; kp = tail_kw
                            contrib = base_contrib * q_coeff % MOD
                            key = make_Q_key(bp, kp, 0, 0)
                            if key not in bq: bq[key] = (0, {}, [])
                            tc, xd, xs = bq[key]
                            prev = xd.get(x1_word, 0); xd[x1_word] = (prev + contrib) % MOD
                            bq[key] = ((tc+contrib)%MOD, xd, xs)

        # === Q c=0: primitive ===
        if k - 1 >= 0:
            s_T = k - 1
            for hkey, (coeff_T, x1sub_T, xseqs_T) in alpha_H[s_T].items():
                bw_T, kw_T, c_T, all1_T, ct_T = hkey
                if c_T >= 1: t1_vals = [(1, coeff_T, None)]
                else: t1_vals = [(x1, c, ct) for (x1, ct), c in x1sub_T.items()] if x1sub_T else []
                for t1, tc, ct_T_val in t1_vals:
                    if tc == 0: continue
                    tail_size = k - 1 - t1
                    if tail_size < 0: continue
                    alice_A = 2*k - 1
                    if False and xseqs_T and sum(c for _,c in xseqs_T) % MOD == coeff_T:  # DISABLED
                        xseq_map = {}
                        for xs_tuple, c_xs in xseqs_T:
                            xs_list = list(xs_tuple)
                            if xs_list[0] != t1 + 1: continue
                            Xw_A_real = compute_XwT_real(xs_list)
                            prev_c = xseq_map.get(Xw_A_real, 0)
                            xseq_map[Xw_A_real] = (prev_c + c_xs) % MOD
                        for Xw_A_seq, xt_coeff in xseq_map.items():
                            Xw_A_list = list(Xw_A_seq)
                            Xw_A = pair_seq([1] + Xw_A_list)
                            bp_A = sum(j * Xw_A[j] for j in range(len(Xw_A)))
                            kp_A = len(Xw_A)
                            contrib = pa[alice_A] * xt_coeff % MOD
                            key = make_Q_key(bp_A, kp_A, 0, 0)
                            if key not in bq: bq[key] = (0, {}, [])
                            tc2, xd, xs_l = bq[key]
                            x1_A = Xw_A_list[0]
                            prev = xd.get(x1_A, 0); xd[x1_A] = (prev + contrib) % MOD
                            bq[key] = ((tc2 + contrib) % MOD, xd, xs_l)
                    else:
                        if c_T >= 1: c_tail_group = 1 if all1_T == 1 else 0; use_filter = True
                        else: c_tail_group = ct_T_val if ct_T_val is not None else 0; use_filter = True
                        bp_expected = bw_T - s_T + t1; kp_expected = kw_T - 1
                        for qkey, (q_coeff, _, _) in beta_Q[tail_size].items():
                            bp_t, kp_t, cq, aq = qkey
                            if bp_t != bp_expected or kp_t != kp_expected: continue
                            if use_filter and cq != c_tail_group: continue
                            bp = bp_t + tail_size; kp = 1 + kp_t
                            contrib = pa[alice_A] * tc % MOD
                            key = make_Q_key(bp, kp, 0, 0)
                            if key not in bq: bq[key] = (0, {}, [])
                            tc2, xd, xs_l = bq[key]
                            x1_A = 1 + t1
                            prev = xd.get(x1_A, 0); xd[x1_A] = (prev + contrib) % MOD
                            bq[key] = ((tc2 + contrib) % MOD, xd, xs_l)

        # === Q c=2p (even) ===
        for p in range(1, k//2 + 1):
            c = 2*p; rest_size = k - c
            if rest_size <= 0: continue
            for qkey, (q_coeff, _, _) in beta_Q[rest_size].items():
                bp_r, kp_r, c_r, a_r = qkey
                if c_r != 0 or a_r != 0: continue
                bp = bp_r + p*(k-p-1); kp = p + kp_r
                alice_prefix = p*(2*p+1) + 2*p*rest_size
                contrib = pa[alice_prefix] * q_coeff % MOD
                key = make_Q_key(bp, kp, 1, 0)
                if key not in bq: bq[key] = (0, None, [])
                tc, _, xs = bq[key]; bq[key] = ((tc+contrib)%MOD, None, xs)

        # === Q c=2p+1 (odd) ===
        for p in range(0, (k+1)//2):
            c = 2*p+1
            if c >= k: continue
            const_exp = (2*p+1)*(p+1) - 1 + (2*p+1)*(k-2*p-1)
            const_factor = pa[const_exp] % MOD
            max_v = k - 2*p - 2
            for v in range(2, max_v + 1):
                t = k - 2*p - 1 - v
                if t < 0: continue
                v_dep_exp = v * (k - 2*p + 1 - v)
                v_factor = pa[v_dep_exp] * total_H[v-1] % MOD
                full_factor = const_factor * v_factor % MOD
                for qkey, (q_coeff, _, _) in beta_Q[t].items():
                    bp_r, kp_r, _, _ = qkey
                    bp = p*p + bp_r + (p+1)*(k-2*p-1) - v
                    kp = p+1 + kp_r
                    contrib = full_factor * q_coeff % MOD
                    key = make_Q_key(bp, kp, 1, 0)
                    if key not in bq: bq[key] = (0, None, [])
                    tc, _, xs = bq[key]; bq[key] = ((tc+contrib)%MOD, None, xs)

        beta_Q[k] = bq

    return alpha_H, beta_Q, total_H, pa, pb

def compute_HkL(alpha_H, pb, N):
    H = [None] * (N + 1)
    for k in range(N + 1):
        Lmax = N - k; Hk = [0] * (Lmax + 1)
        for hkey, (coeff, _, _) in alpha_H[k].items():
            bw, kw, _, _, _ = hkey
            base = coeff * pb[bw] % MOD
            if Lmax >= 0:
                cur = base
                for L in range(Lmax + 1):
                    Hk[L] = (Hk[L] + cur) % MOD
                    cur = cur * pb[kw] % MOD
        H[k] = Hk
    return H

def compute_F(alpha_H, pa, pb, N):
    H = compute_HkL(alpha_H, pb, N)
    F = [0] * (N + 1); F[0] = 1
    for n in range(1, N + 1):
        total = 0
        for m in range(1, n + 1):
            k = m - 1; L = n - m
            exp = 2*m - 1 + m*(n - m)
            term = pa[exp] * H[k][L] % MOD * F[n - m] % MOD
            total = (total + term) % MOD
        F[n] = total
    return F

if __name__ == '__main__':
    Nmax = 8; a_val = 2; b_val = 3
    print("Computing split-orbit DP v14 (xs[0]!=t1+1 fix)...")
    alpha_H, beta_Q, total_H, pa, pb = compute_H_orbit_split(Nmax, a_val, b_val)

    print("\nOrbit counts:")
    for k in range(0, Nmax + 1):
        c0 = sum(1 for hkey in alpha_H[k] if hkey[2]==0)
        c1 = sum(1 for hkey in alpha_H[k] if hkey[2]==1)
        print("k=%2d: H=%d(c0:%d,c1:%d)" % (k, len(alpha_H[k]), c0, c1))

    print("\nH[k] verification (vs REAL wrapping BF):")
    H_bf, _, _ = compute_H_real_BF(Nmax, a_val, b_val)
    all_h_ok = True
    for k in range(1, Nmax + 1):
        Hdp = {}
        for hkey, (coeff, _, _) in alpha_H[k].items():
            bw, kw = hkey[0], hkey[1]
            Hdp[(bw,kw)] = Hdp.get((bw,kw),0) + coeff
        h_ok = True
        bf_keys = set(H_bf[k].keys())
        dp_keys = set(Hdp.keys())
        missing_bf = bf_keys - dp_keys
        extra_dp = dp_keys - bf_keys
        if missing_bf: print("k=%d: Missing from DP: %s" % (k, sorted(missing_bf)))
        if extra_dp: print("k=%d: Extra in DP: %s" % (k, sorted(extra_dp)))
        for (bw,kw), bfv in sorted(H_bf[k].items()):
            dpv = Hdp.get((bw,kw),0)%MOD
            if dpv != bfv%MOD:
                if h_ok: print("k=%d FAILS:" % k); h_ok=False; all_h_ok=False
                print("  bw=%d kw=%d: DP=%d BF=%d diff=%d" % (bw,kw,dpv,bfv%MOD,(dpv-bfv)%MOD))
        if h_ok: print("k=%d: ALL OK (%d orbits)" % (k, len(H_bf[k])))
        if not h_ok:
            print("  BF entries:")
            for (bw,kw), v in sorted(H_bf[k].items()):
                print("    bw=%d kw=%d: %d" % (bw, kw, v % MOD))
            print("  DP entries:")
            for hkey, (coeff, x1sub, xseqs) in sorted(alpha_H[k].items()):
                bw, kw, c_flag, all1, ct = hkey
                xseq_count = len(xseqs) if xseqs else 0
                print("    bw=%d kw=%d c=%d a=%d ct=%s: %d (xseq:%d)" % (bw, kw, c_flag, all1, ct, coeff % MOD, xseq_count))

    if all_h_ok:
        print("\nAll H[k] OK!")
        F = compute_F(alpha_H, pa, pb, Nmax)
        F_bf, _, _ = solve_bruteforce(Nmax, a_val, b_val)
        print("\nF comparison:")
        all_ok = True
        for n in range(1, Nmax+1):
            ok = "OK" if F[n]==F_bf[n] else "FAIL"
            if F[n]!=F_bf[n]: all_ok=False
            print("  F[%2d] %s" % (n, ok))
        if all_ok: print("\n*** ALL VERIFIED ***")
