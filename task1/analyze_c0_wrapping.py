# -*- coding: utf-8 -*-
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

def bob_of_seq(sq):
    return sum(j * sq[j] for j in range(len(sq)))

print("=" * 70)
print("SECTION 1: Verify c=0 wrapping formula")
print("=" * 70)

for k in range(2, 9):
    words = generate_dyck(k)
    ok, fail = 0, 0
    for A in words:
        X, _ = x_seq_and_bob(A)
        Xw_act = pair_seq([1] + X)
        bw_act = sum((j-1)*Xw_act[j-1] for j in range(1, len(Xw_act)+1))
        kw_act = len(Xw_act)
        
        x1 = X[0]
        tail_X = X[1:]
        if tail_X:
            tail_ps = pair_seq(tail_X)
            exp_bw = bob_of_seq(tail_ps) + (k - x1)
            exp_kw = 1 + len(tail_ps)
        else:
            exp_bw = 0
            exp_kw = 1
        
        if (bw_act, kw_act) != (exp_bw, exp_kw):
            fail += 1
            if fail <= 2:
                print("FAIL k=%d X=%s tail_ps=%s act=(%d,%d) exp=(%d,%d)" %
                      (k, X, tail_ps, bw_act, kw_act, exp_bw, exp_kw))
        else:
            ok += 1
    status = "ALL OK" if fail == 0 else "%d FAILS" % fail
    print("k=%d: %s" % (k, status))

print("\n" + "=" * 70)
print("SECTION 2: Q[k] = pair_seq on x_seq (without prepended [1])")
print("Recursive verification")
print("=" * 70)

def compute_Q_params_from_xseq(X):
    ps = pair_seq(X)
    bp = bob_of_seq(ps)
    kp = len(ps)
    return bp, kp

for k in range(1, 9):
    words = generate_dyck(k)
    ok, fail = 0, 0
    
    for A in words:
        X, _ = x_seq_and_bob(A)
        bp_act, kp_act = compute_Q_params_from_xseq(X)
        
        c = 0
        for val in X:
            if val == 1: c += 1
            else: break
        
        if c == k:
            if k % 2 == 0:
                p = k // 2
                exp_bp = p * (p - 1)
                exp_kp = p
            else:
                p = k // 2
                exp_bp = p * p
                exp_kp = p + 1
        elif c == 0:
            x1 = X[0]
            tail_X = X[1:]
            tail_bp, tail_kp = compute_Q_params_from_xseq(tail_X)
            exp_bp = tail_bp + (k - x1)
            exp_kp = 1 + tail_kp
        else:
            if c % 2 == 0:
                p = c // 2
                rest_X = X[c:]
                rest_bp, rest_kp = compute_Q_params_from_xseq(rest_X)
                exp_bp = rest_bp + p * (k - p - 1)
                exp_kp = p + rest_kp
            else:
                p = (c - 1) // 2
                rest_X = X[c:]
                rest_bp, rest_kp = compute_Q_params_from_xseq(rest_X)
                exp_bp = p * p + rest_bp + (p + 1) * (k - 2 * p - 1)
                exp_kp = p + 1 + rest_kp
        
        if (bp_act, kp_act) != (exp_bp, exp_kp):
            fail += 1
            if fail <= 3:
                print("FAIL k=%d c=%d X=%s act=(%d,%d) exp=(%d,%d)" %
                      (k, c, X, bp_act, kp_act, exp_bp, exp_kp))
        else:
            ok += 1
    
    status = "ALL OK" if fail == 0 else "%d FAILS" % fail
    print("k=%d: %s" % (k, status))

print("\n" + "=" * 70)
print("SECTION 3: Combined wrapping formula (unified)")
print("For ANY c, wrapping (bw,kw) expressed via Q[rest] + c-based formula")
print("=" * 70)

for k in range(1, 9):
    words = generate_dyck(k)
    ok, fail = 0, 0
    
    for A in words:
        X, _ = x_seq_and_bob(A)
        Xw_act = pair_seq([1] + X)
        bw_act = bob_of_seq(Xw_act)
        kw_act = len(Xw_act)
        
        c = 0
        for val in X:
            if val == 1: c += 1
            else: break
        
        if c == k:
            t = k + 1
            if t % 2 == 0:
                u = t // 2
                exp_bw = u * (u - 1)
                exp_kw = u
            else:
                u = t // 2
                exp_bw = u * u
                exp_kw = u + 1
        elif c == 0:
            tail_X = X[1:]
            tail_ps = pair_seq(tail_X)
            exp_bw = bob_of_seq(tail_ps) + (k - X[0])
            exp_kw = 1 + len(tail_ps)
        else:
            rest_X = X[c:]
            rest_ps = pair_seq([1] + rest_X)
            rest_bw = bob_of_seq(rest_ps)
            rest_kw = len(rest_ps)
            if c % 2 == 0:
                p = c // 2
                exp_bw = p * (k - p) + rest_bw
                exp_kw = p + rest_kw
            else:
                p = (c - 1) // 2
                exp_bw = (p + 1) * (k - p - 1) + rest_bw
                exp_kw = p + 1 + rest_kw
        
        if (bw_act, kw_act) != (exp_bw, exp_kw):
            fail += 1
            if fail <= 2:
                print("FAIL k=%d c=%d X=%s act=(%d,%d) exp=(%d,%d)" %
                      (k, c, X, bw_act, kw_act, exp_bw, exp_kw))
        else:
            ok += 1
    
    status = "ALL OK" if fail == 0 else "%d FAILS" % fail
    print("k=%d: %s" % (k, status))

print("\n" + "=" * 70)
print("SECTION 4: Orbit counts for H[k] vs Q[k]")
print("=" * 70)

for k in range(1, 10):
    words = generate_dyck(k)
    H_orbits = set()
    Q_orbits = set()
    
    for A in words:
        X, _ = x_seq_and_bob(A)
        Xw = pair_seq([1] + X)
        bw = bob_of_seq(Xw)
        kw = len(Xw)
        H_orbits.add((bw, kw))
        
        ps = pair_seq(X)
        bp = bob_of_seq(ps)
        kp = len(ps)
        Q_orbits.add((bp, kp))
    
    print("k=%d: Catalan=%d  H_orbits=%d  Q_orbits=%d" %
          (k, len(words), len(H_orbits), len(Q_orbits)))

print("\n" + "=" * 70)
print("SECTION 5: Verify that Q-orbits are (bob, k) of pair_seq(X)")
print("NOT wrapping. Q[k][bp][kp] = sum of a^alice for words")
print("where pair_seq(X) gives (bp, kp)")
print("=" * 70)

for k in range(1, 9):
    words = generate_dyck(k)
    by_orbit = {}
    for A in words:
        X, _ = x_seq_and_bob(A)
        ps = pair_seq(X)
        bp = bob_of_seq(ps)
        kp = len(ps)
        al = alice_of(A)
        key = (bp, kp)
        val = by_orbit.get(key, [0, []])
        val[0] += 1
        val[1].append(X)
        by_orbit[key] = val
    
    print("k=%d: %d Q-orbits" % (k, len(by_orbit)))
    for (bp, kp), (cnt, examples) in sorted(by_orbit.items())[:5]:
        print("  (bp=%d, kp=%d): %d words, e.g. X=%s" % (bp, kp, cnt, examples[:2]))
