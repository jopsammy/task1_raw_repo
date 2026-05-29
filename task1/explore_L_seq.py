"""
Explore L(i) sequence representation as a potential DP basis.
L(i) = P(i) - i where P(i) = position of i-th right parenthesis (1-indexed).
alice = Σ L(i)
bob derived from L via: l₀=0, lⱼ₊₁=L(lⱼ+1), xⱼ₊₁=lⱼ₊₁-lⱼ
"""
import sys
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def compute_L_seq(s):
    """Compute L(i) = P(i) - i for Dyck word s."""
    n = len(s) // 2
    L = []
    right_count = 0
    left_count = 0
    for i, ch in enumerate(s):
        if ch == '(':
            left_count += 1
        else:
            right_count += 1
            pos = i + 1
            L_val = pos - right_count
            L.append(L_val)
    return L

def L_to_alice(L):
    return sum(L)

def L_to_bob_k(L):
    """Compute bob and k from L sequence."""
    n = len(L)
    l_vals = [0]
    idx = 0
    while idx < n:
        next_l = L[idx]
        l_vals.append(next_l)
        idx = next_l
    l_vals = l_vals[:-1]
    
    k = len(l_vals) - 1
    bob = 0
    for j in range(k):
        bob += j * (l_vals[j+1] - l_vals[j])
    return bob, k, l_vals

def enumerate_L_sequences(n):
    """Check how many distinct L sequences exist for Dyck words of size n."""
    words = generate_dyck(n)
    L_set = set()
    L_to_words = {}
    for s in words:
        L = tuple(compute_L_seq(s))
        L_set.add(L)
        L_to_words.setdefault(L, []).append(s)
    
    print(f"n={n}: Catalan={len(words)}, distinct L-seqs={len(L_set)}, ratio={len(words)/len(L_set):.1f}")
    
    return L_set, L_to_words

def characterize_L_sequence(L):
    """Check constraints on valid L sequences."""
    n = len(L)
    constraints = []
    
    for i in range(n):
        lo = i + 1
        hi = 2*n - i - 1
        ok = (lo <= L[i] <= hi)
        constraints.append((f"L[{i}] in [{lo},{hi}]", ok))
    
    for i in range(n - 1):
        ok = (L[i] <= L[i+1])
        constraints.append((f"L[{i}] <= L[{i+1}]", ok))
    
    L[n-1] = n (always)
    ok = (L[n-1] == n)
    constraints.append(("L[n-1]=n", ok))
    
    return constraints

def find_L_properties(n):
    """Analyze L-sequence properties for small n."""
    L_set, L_to_words = enumerate_L_sequences(n)
    
    print(f"\n--- L-sequence properties for n={n} ---")
    
    for L in sorted(L_set):
        alice = L_to_alice(L)
        bob, k, l_vals = L_to_bob_k(L)
        words = L_to_words[L]
        L_str = str(list(L))
        print(f"  L={L_str:40s} alice={alice:2d} bob={bob:2d} k={k} l={l_vals} words[{len(words)}]={words[:3]}")

if __name__ == '__main__':
    print("=== L-sequence Analysis ===\n")
    
    for n in range(2, 7):
        print(f"\n{'='*50}")
        find_L_properties(n)
    
    print(f"\n\n=== L(i) constraints ===")
    for n in [3, 4, 5]:
        words = generate_dyck(n)
        all_ok = True
        for s in words:
            L = compute_L_seq(s)
            constraints = characterize_L_sequence(L)
            for desc, ok in constraints:
                if not ok:
                    print(f"  FAIL: {desc} for s={s}, L={L}")
                    all_ok = False
        if all_ok:
            print(f"  n={n}: all constraints satisfied for all words")
