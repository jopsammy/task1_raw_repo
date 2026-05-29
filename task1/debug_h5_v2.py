# -*- coding: utf-8 -*-
"""Deep debug H[5]: trace each word through DP branches to find root cause."""
from orbit_dp_v11 import *

MOD = 998244353
a_val = 2; b_val = 3

max_exp = 50
pa = [1]*(max_exp+1); pb = [1]*(max_exp+1)
for i in range(1,max_exp+1): pa[i]=pa[i-1]*a_val%MOD; pb[i]=pb[i-1]*b_val%MOD

k = 5
words = generate_dyck(k)
print("=== H[5] full word analysis (size 5 Dyck words) ===")
print("Total words:", len(words))

# Classify each word
print("\n--- Word classification ---")
for A in sorted(words):
    X, bob = x_seq_and_bob(A)
    Xw = pair_seq([1]+X)
    bw = sum((j)*Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    al = alice_of(A)
    
    # Compute c
    c = 0
    for xx in X:
        if xx == 1: c += 1
        else: break
    
    alice_parts = []
    if c >= 1:
        B = A[2*c:]  # remove c leading "()"
        alice_B = alice_of(B) if B else 0
        kB = len(B)//2
        expected_al = alice_B + c*(c+1)//2 + c*(k-c)
        alice_parts.append("al=al(B)+c(c+1)/2+c(k-c)=%d+%d+%d=%d" % (alice_B, c*(c+1)//2, c*(k-c), expected_al))
    else:
        alice_parts.append("c=0")
    
    print("  A=%-20s X=%s c=%d Xw=%s bw=%d kw=%d al=%d exp_al=%s" % (
        A, X, c, 
        ','.join(str(x) for x in Xw), bw, kw, al, 
        '; '.join(alice_parts)))

print("\n--- H[5] BF by (bw,kw) ---")
Hbf = {}
for A in words:
    X, _ = x_seq_and_bob(A)
    Xw = pair_seq([1]+X)
    bw = sum(j*Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    al = alice_of(A)
    key = (bw, kw)
    if key not in Hbf: Hbf[key] = (0, [])
    Hbf[key] = (Hbf[key][0] + pa[al], Hbf[key][1] + [A])

for (bw,kw), (val, wlist) in sorted(Hbf.items()):
    print("  bw=%d kw=%d: BF=%d words: %s" % (bw, kw, val % MOD, wlist))

# Now trace the DP
print("\n\n=== DP Trace ===")
alpha_H, beta_Q, total_H, _, _ = compute_H_orbit_split(5, a_val, b_val)

print("\nH[5] DP entries:")
for hkey, (coeff, x1sub, xseqs) in sorted(alpha_H[5].items()):
    bw, kw, c_flag, all1, ct = hkey
    print("  bw=%d kw=%d c_flag=%d all1=%d ct=%s: coeff=%d" % (bw, kw, c_flag, all1, ct, coeff % MOD))
    if c_flag == 0 and x1sub:
        for (x1,ct2), c in sorted(x1sub.items()):
            print("    x1=%d ct=%d → %d" % (x1, ct2, c % MOD))
    if xseqs:
        for xs, c in xseqs[:5]:
            print("    xseq=%s → %d" % (xs, c % MOD))
        if len(xseqs) > 5:
            print("    ... (%d more)" % (len(xseqs)-5))

# Compare
print("\n=== Comparison ===")
for (bw,kw), (bfv, _) in sorted(Hbf.items()):
    dpv = sum(coeff for hkey, (coeff,_,_) in alpha_H[5].items() if hkey[0]==bw and hkey[1]==kw) % MOD
    ok = "OK" if dpv == bfv % MOD else "FAIL (diff=%d)" % ((dpv - bfv) % MOD)
    print("  bw=%d kw=%d: BF=%d DP=%d %s" % (bw, kw, bfv % MOD, dpv, ok))

# Now trace individual failing words
print("\n\n=== TRACE FAILING WORDS ===")
# (bw=3,kw=2) fails
target_words_32 = [A for A in words if sum(j*x for j,x in enumerate(pair_seq([1]+x_seq_and_bob(A)[0])))==3 and len(pair_seq([1]+x_seq_and_bob(A)[0]))==2]
print("\n(bw=3,kw=2) words:", target_words_32)

for A in target_words_32:
    X, _ = x_seq_and_bob(A)
    c = 0
    for xx in X:
        if xx == 1: c += 1
        else: break
    print("\n  A=%s X=%s c=%d" % (A, X, c))
    
    # Which DP branch should handle this?
    if c == k:  # all 1s
        print("  → c=k=5, all1 branch")
    elif c >= 2:  # c=2p or c=2p+1
        print("  → c=%d branch" % c)
    elif c == 1:
        print("  → c=1 (c_flag=1 but not all1), need to trace...")
        # For c=1: (A) started with 1 leading "()"
        # X = [1, ...rest...]
        # Xw = pair_seq([1,1,...rest...]) = pair_seq([2, ...rest...])
        # Actually c=1 means X begins with 1 and X[1] >= 2
        rest_size = k - 1
        B = A[2:]  # remove leading "()"
        XB, _ = x_seq_and_bob(B)
        print("    rest_size=%d B=%s X(B)=%s" % (rest_size, B, XB))
    elif c == 0:
        print("  → c=0 (x1>=2), need to trace...")
        # For c=0: X[0] >= 2
        # Could be primitive or non-primitive
        # Check if A is primitive
        h_test = 0
        is_prim = True
        for i, ch in enumerate(A):
            h_test += 1 if ch == '(' else -1
            if i > 0 and i < len(A)-1 and h_test == 0:
                is_prim = False
                break
        print("    is_primitive=%s" % is_prim)

print("\n\n=== Trace (bw=3,kw=2) through DP ===")
# For (bw=3,kw=2), the BF has only certain words
# Let's check which c_flag entries contribute to this
ah5 = alpha_H[5]
for hkey, (coeff, x1sub, xseqs) in ah5.items():
    bw, kw, c_flag, all1, ct = hkey
    if bw != 3 or kw != 2: continue
    print("Entry: bw=%d kw=%d c_flag=%d all1=%d ct=%s coeff=%d" % (bw, kw, c_flag, all1, ct, coeff%MOD))
    if x1sub:
        for (x1,ct2), c in sorted(x1sub.items()):
            print("  x1=%d ct=%d → %d" % (x1, ct2, c%MOD))
    if xseqs:
        for xs, c in xseqs[:10]:
            print("  xseq=%s → %d" % (xs, c%MOD))

# Trace (bw=4,kw=3)
print("\n=== Trace (bw=4,kw=3) through DP ===")
for hkey, (coeff, x1sub, xseqs) in ah5.items():
    bw, kw, c_flag, all1, ct = hkey
    if bw != 4 or kw != 3: continue
    print("Entry: bw=%d kw=%d c_flag=%d all1=%d ct=%s coeff=%d" % (bw, kw, c_flag, all1, ct, coeff%MOD))
    if x1sub:
        for (x1,ct2), c in sorted(x1sub.items()):
            print("  x1=%d ct=%d → %d" % (x1, ct2, c%MOD))
    if xseqs:
        for xs, c in xseqs[:10]:
            print("  xseq=%s → %d" % (xs, c%MOD))
