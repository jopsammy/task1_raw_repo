"""
Derive c-based wrapping transformation for REAL x_seq_and_bob (not pair_seq).

Key question: Given a Dyck word A = "()" * c + R where R has x₁(R) ≥ 2 (c = 0 for R),
how does wrapping (A) relate to wrapping of sub-words?

This analysis uses ENUMERATION (not pair_seq formulas) as ground truth.
"""
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353


def compute_L_seq(s):
    n = len(s) // 2
    L = [0] * n
    rc = 0
    for i, ch in enumerate(s):
        if ch == ')':
            L[rc] = (i + 1) - (rc + 1)
            rc += 1
    return L


def get_c(s):
    """Number of leading () blocks."""
    L = compute_L_seq(s)
    c = 0
    for i, val in enumerate(L):
        if val == i + 1:
            c += 1
        else:
            break
    return c


def split_word(s, c):
    """Split s = "()"*c + rest."""
    if c == 0:
        return s
    return s[2*c:]


def analyze_c_transformation(max_k=9):
    """
    For each k, for each c>0 word, check:
    - c = how many leading "()" blocks
    - rest = word after removing c leading "()" blocks
    - Verify: is rest a valid Dyck word?
    - How do (bobw, kw, alice) of (A) relate to c and wrapping of rest?
    """
    print("=== c-based decomposition analysis (REAL wrapping) ===\n")

    for k in range(1, max_k + 1):
        words = generate_dyck(k)
        print(f"\n--- k={k} (Catalan={len(words)}) ---")
        
        for s in words:
            c = get_c(s)
            rest_word = split_word(s, c)
            
            rest_k = len(rest_word) // 2
            
            if c == 0:
                continue
            
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            al = alice_of(s)
            
            if rest_k > 0:
                w_rest = '(' + rest_word + ')'
                Xrw, bobrw = x_seq_and_bob(w_rest)
                krw = len(Xrw)
                al_rest = alice_of(rest_word)
            else:
                Xrw, bobrw, krw = [], 0, 0
                al_rest = 0
            
            print(f"  s={s:20s} c={c} rest={rest_word:12s} rest_k={rest_k}")
            print(f"    Xw={Xw}  bw={bobw:2d} kw={kw}  al={al}")
            if rest_k > 0:
                print(f"    X((rest))={Xrw}  bwr={bobrw:2d} kwr={krw}  al_rest={al_rest}")
            
            if rest_k > 0 and c >= 1:
                bobw_pred = bobw - bobrw
                kw_pred = kw - krw
                al_pred = al - al_rest - c*(c-1)//2 - c*rest_k
                print(f"    Δbw={bobw_pred:2d} Δkw={kw_pred} Δal={al_pred}  (actual vs formula)")
            print()


def derive_pattern(max_k=8):
    """
    Systematic attempt: for each (c, bw_rest, kw_rest, al_rest, rest_k, k),
    derive the transformation rule.
    """
    print("\n\n=== Systematic pattern derivation ===\n")
    
    data_by_c = {}
    
    for k in range(1, max_k + 1):
        words = generate_dyck(k)
        for s in words:
            c = get_c(s)
            if c == 0:
                continue
            
            rest_word = split_word(s, c)
            rest_k = len(rest_word) // 2
            
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            al = alice_of(s)
            
            if rest_k == 0:
                w_rest = '(' + ')'  # size 1
                Xrw, bobrw = x_seq_and_bob(w_rest)
                krw = 1
                al_rest = 1
            else:
                w_rest = '(' + rest_word + ')'
                Xrw, bobrw = x_seq_and_bob(w_rest)
                krw = len(Xrw)
                al_rest = alice_of(rest_word)
            
            key = (c, rest_k, k, krw, bobrw, al_rest)
            row = {
                'word': s,
                'k': k,
                'c': c,
                'rest_k': rest_k,
                'bw': bobw,
                'kw': kw,
                'al': al,
                'bw_rest': bobrw,
                'kw_rest': krw,
                'al_rest': al_rest,
                'Xw': Xw,
                'Xrw': Xrw,
                'Δbw': bobw - bobrw,
                'Δkw': kw - krw,
                'Δal': al - al_rest - c*(c-1)//2 - c*rest_k
            }
            
            if c not in data_by_c:
                data_by_c[c] = []
            data_by_c[c].append(row)
    
    for c in sorted(data_by_c.keys()):
        print(f"\n--- c={c} ---")
        rows = data_by_c[c]
        print(f"  Count: {len(rows)}")
        print(f"  Sample rows (first 5):")
        for r in rows[:5]:
            print(f"    k={r['k']} rest_k={r['rest_k']} kw_rest={r['kw_rest']} "
                  f"Δbw={r['Δbw']} Δkw={r['Δkw']} Δal={r['Δal']} "
                  f"bw={r['bw']} bwr={r['bw_rest']} "
                  f"Xw={r['Xw']}")


def verify_c_recurrence(max_k=8):
    """
    Try to verify: can we reconstruct wrapping of c>0 word from
    its c and the wrapping of its rest?
    
    Hypotheses to test:
    H1: bw = f(c, k, bw_rest)
    H2: kw = g(c, kw_rest)
    H3: al = al_rest + c*(c-1)/2 + c*rest_k + h(c, k, bw_rest, kw_rest)
    """
    print("\n\n=== Hypothesis testing ===\n")
    
    all_ok = True
    for k in range(1, max_k + 1):
        words = generate_dyck(k)
        for s in words:
            c = get_c(s)
            if c == 0:
                continue
            
            rest_word = split_word(s, c)
            rest_k = len(rest_word) // 2
            
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            al = alice_of(s)
            
            if rest_k == 0:
                w_rest = '(' + ')' 
                Xrw, bobrw = x_seq_and_bob(w_rest)
                krw = 1
                al_rest = 1
            else:
                w_rest = '(' + rest_word + ')'
                Xrw, bobrw = x_seq_and_bob(w_rest)
                krw = len(Xrw)
                al_rest = alice_of(rest_word)
            
            al_expected = al_rest + c*(c-1)//2 + c*rest_k
            
            n = k + 1
            
            bobw_predicted_from_rest = bobrw
            
            t = c + 1
            if t % 2 == 0:
                u = t // 2
                exp_kw = u + (krw - 1)
                exp_bw_delta = u * (u - 1) + u * (krw - 1)
            else:
                u = t // 2
                exp_kw = u + 1 + (krw - 1)
                exp_bw_delta = u * u + (u + 1) * (krw - 1)
            
            exp_bw = exp_bw_delta + bobrw
            
            if al != al_expected:
                print(f"  ALICE FAIL: k={k} c={c} s={s} al={al} exp={al_expected}")
                all_ok = False
            
            if exp_bw != bobw or exp_kw != kw:
                flag = ""
                if exp_bw != bobw and exp_kw != kw:
                    flag = "BOTH"
                elif exp_bw != bobw:
                    flag = "BW"
                else:
                    flag = "KW"
                print(f"  {flag} FAIL: k={k} c={c} s={s:20s} Xw={Xw} bw={bobw} kw={kw} | exp_bw={exp_bw} exp_kw={exp_kw}")
                all_ok = False
    
    if all_ok:
        print("  ALL OK!")
    else:
        print("\n  SOME FAILS - need different formula")


if __name__ == '__main__':
    analyze_c_transformation(8)
    derive_pattern(8)
    verify_c_recurrence(8)
