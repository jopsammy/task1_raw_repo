"""
Test the claimed formula: F = 1 + P/(1-xy)
and explore the true relationship between F and P.
"""
import sys
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def compute_F_and_P(N, a_val, b_val):
    """Compute F(x,y) and P(x,y) as dictionaries."""
    max_exp = N * N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * a_val % MOD
        pb[i] = pb[i-1] * b_val % MOD
    
    F_coeffs = {}
    P_coeffs = {}
    
    for n in range(1, N + 1):
        words = generate_dyck(n)
        for s in words:
            alice_v = alice_of(s)
            X, bob_v = x_seq_and_bob(s)
            k_val = len(X)
            coeff = pa[alice_v] * pb[bob_v] % MOD
            key = (n, k_val)
            F_coeffs[key] = (F_coeffs.get(key, 0) + coeff) % MOD
    
    for n in range(1, N + 1):
        A_words = generate_dyck(n - 1)
        for a_word in A_words:
            alice_a = alice_of(a_word)
            ws = '(' + a_word + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            coeff = pa[alice_a + 2*(n-1) + 1] * pb[bobw] % MOD
            key = (n, kw)
            P_coeffs[key] = (P_coeffs.get(key, 0) + coeff) % MOD
    
    return F_coeffs, P_coeffs

def test_formula_F_equals_1_plus_P_over_1_minus_xy(N, a_val, b_val):
    """Test F = 1 + P/(1-xy) by expanding coefficients."""
    F, P = compute_F_and_P(N, a_val, b_val)
    
    print(f"\n=== Testing F = 1 + P/(1-xy) for a={a_val}, b={b_val} ===")
    
    P_over = {}
    for (pn, pk), pval in P.items():
        for t in range(0, N - pn + 1):
            key = (pn + t, pk + t)
            P_over[key] = (P_over.get(key, 0) + pval) % MOD
    
    ok = True
    for n in range(1, N + 1):
        for k in range(0, n + 1):
            actual = F.get((n, k), 0) if (n, k) != (0, 0) else 1
            pred = P_over.get((n, k), 0)
            if n == 0 and k == 0:
                pred = 1
            
            if actual != pred:
                print(f"  MISMATCH n={n}, k={k}: F={actual}, P/(1-xy)={pred}")
                ok = False
    
    if ok:
        print(f"  All OK! ✓")
    else:
        print(f"  Formula FAILS")
    
    return ok

def find_true_relationship(N, a_val, b_val):
    """Try to find the actual relationship between F and P."""
    F, P = compute_F_and_P(N, a_val, b_val)
    
    print(f"\n=== Finding relationship F(P) for a={a_val}, b={b_val} ===")
    
    print(f"\n  n=1:")
    print(f"    F[1,1] = {F.get((1,1),0)}")
    print(f"    P[1,1] = {P.get((1,1),0)}")
    
    for n in range(2, min(N + 1, 6)):
        print(f"\n  n={n}:")
        f_row = {k: F.get((n,k), 0) for k in range(n+1)}
        p_row = {k: P.get((n,k), 0) for k in range(n+1)}
        
        for k in sorted(set(list(f_row.keys()) + list(p_row.keys()))):
            if k == 0:
                continue
            f_val = f_row.get(k, 0)
            p_val = p_row.get(k, 0)
            if f_val or p_val:
                print(f"    k={k}: F={f_val:12d}, P={p_val:12d}")

def test_concatenation_series(N, a_val, b_val):
    """
    Test the full concatenation series:
    F = 1 + P₁ + P₂ + P₃ + ...
    where P_m is the contribution of m concatenated primitives (with cross terms).
    """
    F, P = compute_F_and_P(N, a_val, b_val)
    
    print(f"\n=== Testing concatenation series F = 1 + Σ P_m ===")
    
    max_exp = N * N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i-1] * a_val % MOD
        pb[i] = pb[i-1] * b_val % MOD
    
    P_list = [{} for _ in range(N + 1)]
    P_list[1] = dict(P)
    
    concat_F = {(0, 0): 1}
    for (pn, pk), pv in P.items():
        concat_F[(pn, pk)] = (concat_F.get((pn, pk), 0) + pv) % MOD
    
    for depth in range(2, N + 1):
        P_prev = P_list[depth - 1]
        P_new = {}
        for (prev_n, prev_k), prev_v in P_prev.items():
            for (p_n, p_k), p_v in P.items():
                total_n = prev_n + p_n
                if total_n > N:
                    continue
                total_k = prev_k + p_k
                
                cross_a = prev_n * p_n
                cross_b = prev_k * p_n
                term = prev_v * p_v % MOD * pa[cross_a] % MOD * pb[cross_b] % MOD
                key = (total_n, total_k)
                P_new[key] = (P_new.get(key, 0) + term) % MOD
        
        P_list[depth] = P_new
        for (tn, tk), tv in P_new.items():
            concat_F[(tn, tk)] = (concat_F.get((tn, tk), 0) + tv) % MOD
    
    ok = True
    for n in range(1, N + 1):
        for k in range(0, n + 1):
            actual = F.get((n, k), 0)
            pred = concat_F.get((n, k), 0)
            if actual != pred:
                print(f"  MISMATCH n={n}, k={k}: F={actual}, concat={pred}")
                ok = False
    
    if ok:
        print(f"  Concatenation series matches! ✓")
    
    return ok, P_list

if __name__ == '__main__':
    print("=" * 60)
    test_formula_F_equals_1_plus_P_over_1_minus_xy(4, 2, 3)
    test_formula_F_equals_1_plus_P_over_1_minus_xy(4, 1, 1)
    
    find_true_relationship(5, 2, 3)
    find_true_relationship(5, 1, 1)
    
    test_concatenation_series(4, 2, 3)
    test_concatenation_series(4, 1, 1)
