import sys
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def solve_brute_with_k(N, a_val, b_val):
    """Compute F(x,y) coefficients: sum a^{alice} b^{bob} x^n y^k"""
    F_poly = {}
    for n in range(0, N + 1):
        if n == 0:
            F_poly[(0, 0)] = 1
            continue
        words = generate_dyck(n)
        for s in words:
            alice_v = alice_of(s)
            X, bob_v = x_seq_and_bob(s)
            k_val = len(X)
            coeff = pow(a_val, alice_v, MOD) * pow(b_val, bob_v, MOD) % MOD
            key = (n, k_val)
            F_poly[key] = (F_poly.get(key, 0) + coeff) % MOD
    return F_poly

def extract_coeffs(N, a_val, b_val):
    F_poly = solve_brute_with_k(N, a_val, b_val)
    print(f"\n=== F(x,y) coefficients for a={a_val}, b={b_val} (up to n={N}) ===")
    for n in range(0, min(N + 1, 7)):
        row = []
        for k in range(0, n + 1):
            val = F_poly.get((n, k), 0)
            if val:
                row.append(f"k={k}:{val}")
        print(f"  n={n}: {', '.join(row) if row else '1'}")

    F_n = []
    for n in range(N + 1):
        total = sum(F_poly.get((n, k), 0) for k in range(n + 1)) % MOD
        F_n.append(total)
    print(f"\nF[n] (sum_k) = {F_n}")
    return F_poly, F_n

def verify_ab_decomposition(N, a_val, b_val):
    """
    Verify the (A)B decomposition formula:
    s = (A)B, |s|=n, |A|=a, |B|=n-1-a
    
    alice(s) = alice(A) + alice(B) + n + a*(n-a)
    bob(s) = bob((A)) + bob(B) + k((A))*(n-1-a)
    k(s) = k((A)) + k(B)
    """
    print(f"\n=== (A)B decomposition verification for a={a_val}, b={b_val} ===")
    for n in range(1, N + 1):
        words = generate_dyck(n)
        errors = []
        for s in words:
            a_size = None
            for split in range(1, 2 * n):
                if s[:split + 1].count('(') == s[:split + 1].count(')'):
                    A = s[1:split]
                    B = s[split + 1:]
                    a_size = len(A) // 2
                    b_size = len(B) // 2
                    break
            
            if a_size is None:
                errors.append(f"  s={s}: can't find first return to zero!")
                continue

            alice_s = alice_of(s)
            Xs, bob_s = x_seq_and_bob(s)
            ks = len(Xs)

            alice_A = alice_of(A)
            Xw_A, bobw_A = x_seq_and_bob('(' + A + ')')
            kw_A = len(Xw_A)

            alice_B = alice_of(B)
            X_B, bob_B = x_seq_and_bob(B)
            k_B = len(X_B)

            comp_alice = alice_A + alice_B + n + a_size * (n - a_size)
            comp_bob = bobw_A + bob_B + kw_A * b_size
            comp_k = kw_A + k_B

            if alice_s != comp_alice or bob_s != comp_bob or ks != comp_k:
                errors.append(f"  s={s} A={A}(|A|={a_size}) B={B}(|B|={b_size})")
                errors.append(f"    alice: true={alice_s} comp={comp_alice} ({alice_A}+{alice_B}+{n}+{a_size}*{n-a_size}={comp_alice})")
                errors.append(f"    bob:   true={bob_s} comp={comp_bob} ({bobw_A}+{bob_B}+{kw_A}*{b_size})")
                errors.append(f"    k:     true={ks} comp={comp_k} ({kw_A}+{k_B})")

        if errors:
            print(f"  n={n}: {len(errors)//2} errors!")
            for e in errors[:4]:
                print(e)
        else:
            print(f"  n={n}: ALL OK ✓")

def generate_func_equation(N, a_val, b_val):
    """
    F(x,y) = 1 + Σ_A [contribution of (A)] * F(a^{|A|+1} * b^{k((A))} * x, y)
    where contribution of (A) = a^{alice(A)+2|A|+1} * b^{bob((A))} * x^{|A|+1} * y^{k((A))}
    """
    print(f"\n=== GF equation verification for a={a_val}, b={b_val} ===")
    
    F_poly = solve_brute_with_k(N, a_val, b_val)
    
    max_exp = N * N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i - 1] * a_val % MOD
        pb[i] = pb[i - 1] * b_val % MOD

    all_ok = True
    for target_n in range(1, N + 1):
        for target_k in range(0, target_n + 1):
            expected = F_poly.get((target_n, target_k), 0)
            if expected == 0 and target_n > 0 and target_k == 0:
                continue
            
            computed = 0
            for a_size in range(0, target_n):
                b_size = target_n - a_size - 1
                if b_size < 0:
                    continue
                
                words_a = generate_dyck(a_size)
                for a_word in words_a:
                    alice_a = alice_of(a_word)
                    ws = '(' + a_word + ')'
                    Xw, bobw = x_seq_and_bob(ws)
                    kw = len(Xw)
                    
                    for b_k in range(0, b_size + 1):
                        fb_coeff = F_poly.get((b_size, b_k), 0)
                        if fb_coeff == 0:
                            continue
                        
                        comp_k = kw + b_k
                        if comp_k != target_k:
                            continue
                        
                        a_term = pa[alice_a + 2 * a_size + 1]
                        b_term_bob = pb[bobw]
                        
                        cross_a = (a_size + 1) * b_size
                        cross_b = kw * b_size
                        shift = pa[cross_a] * pb[cross_b] % MOD
                        
                        term = a_term * b_term_bob % MOD * fb_coeff % MOD * shift % MOD
                        computed = (computed + term) % MOD

            if computed != expected:
                if expected != 0 or computed != 0:
                    print(f"  MISMATCH n={target_n}, k={target_k}: expected={expected}, computed={computed}")
                    all_ok = False
    
    if all_ok:
        print(f"  All coefficients match for n=1..{N}! ✓")

def check_lagrange_form(N, a_val, b_val):
    """
    Check if there's a simple Lagrange inversion form.
    
    Look for: F = 1 + a*x*y * φ(F, y) or similar.
    
    For Lagrange inversion: if F = 1 + x*φ(F), then [x^n]F = (1/n)[t^{n-1}]φ(t)^n.
    
    Key insight: check if for each fixed k, the coefficients follow a power series composition pattern.
    """
    print(f"\n=== Lagrange form analysis for a={a_val}, b={b_val} ===")
    
    F_poly, F_n = extract_coeffs(N, a_val, b_val)
    
    max_exp = N * N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i - 1] * a_val % MOD
        pb[i] = pb[i - 1] * b_val % MOD

    class F_poly_eval:
        def __init__(self, poly):
            self.poly = poly
        def __call__(self, x_shift, y_shift):
            return self.poly.get((x_shift, y_shift), 0)

    wrapper_contrib = {}
    for k in range(0, N):
        words = generate_dyck(k)
        for a_word in words:
            alice_a = alice_of(a_word)
            ws = '(' + a_word + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            key = (k + 1, kw)
            coeff = pa[alice_a + 2 * k + 1] * pb[bobw] % MOD
            wrapper_contrib[key] = (wrapper_contrib.get(key, 0) + coeff) % MOD
    
    print(f"\nWrapper contribution P(x,y):")
    for (pn, pk), val in sorted(wrapper_contrib.items()):
        print(f"  [x^{pn} y^{pk}] P = {val}")

    print(f"\n--- F(x,y) table ---")
    for n in range(0, min(N + 1, 7)):
        line = []
        for k in range(0, n + 1):
            val = F_poly.get((n, k), 0)
            line.append(f"{val:8d}")
        print(f"n={n}: " + " ".join(line))

    print(f"\n--- P(x,y) table (primitive words) ---")
    max_prim_n = min(N, 7)
    for n in range(0, max_prim_n + 1):
        line = []
        for k in range(0, n + 1):
            val = wrapper_contrib.get((n, k), 0)
            line.append(f"{val:8d}")
        print(f"n={n}: " + " ".join(line))

    print(f"\n--- GF equation: F = 1 + Σ P_nk * F(x*a^{n}*b^{k}, y)  ---")
    print(f"Checking simplified form: F = 1 + a*x*y * something...")
    
    for target_n in range(1, min(N + 1, 6)):
        f_val = F_poly.get((target_n, target_n), 0) or F_poly.get((target_n, target_n - 1), 0)
        

def explore_primitive_gf(N, a_val, b_val):
    """Explore if P can be expressed as a function of F."""
    print(f"\n=== Primitive GF analysis for a={a_val}, b={b_val} ===")
    
    F_poly, F_n = extract_coeffs(N, a_val, b_val)
    
    max_exp = N * N + 5
    pa = [1] * (max_exp + 1)
    pb = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pa[i] = pa[i - 1] * a_val % MOD
        pb[i] = pb[i - 1] * b_val % MOD

    wrapper_contrib = {}
    for k in range(0, N):
        words = generate_dyck(k)
        for a_word in words:
            alice_a = alice_of(a_word)
            ws = '(' + a_word + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            key = (k + 1, kw)
            coeff = pa[alice_a + 2 * k + 1] * pb[bobw] % MOD
            wrapper_contrib[key] = (wrapper_contrib.get(key, 0) + coeff) % MOD

    print(f"P[x^n] = Σ_k P[n,k]:")
    for n in range(1, min(N + 1, 7)):
        total = sum(v for (pn, pk), v in wrapper_contrib.items() if pn == n) % MOD
        print(f"  P[{n}] = {total}")

    print(f"\nF[x^n] = Σ_k F[n,k]:")
    for n in range(1, min(N + 1, 7)):
        total = sum(v for (fn, fk), v in F_poly.items() if fn == n) % MOD
        print(f"  F[{n}] = {total}")

    print(f"\nRelationship P[n] vs F[n-1]:")
    for n in range(2, min(N + 1, 7)):
        p_n = sum(v for (pn, pk), v in wrapper_contrib.items() if pn == n) % MOD
        f_n1 = sum(v for (fn, fk), v in F_poly.items() if fn == n - 1) % MOD
        print(f"  P[{n}]/a^(2n-1) = {p_n * pow(pa[2*n-1], MOD - 2, MOD) % MOD}, F[{n-1}] = {f_n1}")


if __name__ == '__main__':
    print("=" * 70)
    print("ROUTE D: Lagrange Inversion Mathematical Exploration")
    print("=" * 70)
    
    verify_ab_decomposition(6, 2, 3)
    
    generate_func_equation(4, 2, 3)
    
    check_lagrange_form(5, 2, 3)
    check_lagrange_form(5, 1, 1)
    
    explore_primitive_gf(6, 2, 3)
    explore_primitive_gf(6, 1, 1)
