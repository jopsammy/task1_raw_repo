# -*- coding: utf-8 -*-
"""Deep trace of H[5] failing words through each DP branch."""
from orbit_dp_v11 import *

MOD = 998244353
a_val = 2; b_val = 3
max_exp = 50
pa = [1]*(max_exp+1)
for i in range(1,max_exp+1): pa[i]=pa[i-1]*a_val%MOD

k = 5
words = generate_dyck(k)

# Classify ALL 42 words by which DP branch should handle them
print("=== Branch classification for H[5] ===")
branch_counts = {"c=k": 0, "c=2p": 0, "c=2p+1": 0, "c=0-other": 0}

for A in sorted(words):
    X, _ = x_seq_and_bob(A)
    Xw = pair_seq([1]+X)
    bw = sum(j*Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    al = alice_of(A)
    
    c = 0
    for xx in X:
        if xx == 1: c += 1
        else: break
    
    # Which branch?
    branch = "???"
    if c == k:
        branch = "c=k (all1)"
    elif c >= 2:
        if c % 2 == 0: branch = "c=2p (p=%d,c=%d)" % (c//2, c)
        else: branch = "c=2p+1 (p=%d,c=%d)" % ((c-1)//2, c)
    elif c == 1:
        branch = "c=2p+1 (p=0,c=1)"
    else:  # c == 0
        branch = "c=0"
    
    print("  %-20s X=%-15s Xw=%-10s bw=%d kw=%d al=%2d c=%d → %s" % (A, str(X), str(Xw), bw, kw, al, c, branch))

# Now trace the DP internal for primitive c=0
print("\n\n=== Trace primitive c=0 for H[5] ===")
print("s_T=4, alice multiply = pa[9]=%d" % pa[9])

# H[4] entries
alpha_H, _, _, _, _ = compute_H_orbit_split(5, a_val, 3)

print("\nH[4] entries:")
for hkey, (coeff, x1sub, xseqs) in sorted(alpha_H[4].items()):
    bw, kw, c_flag, all1, ct = hkey
    print("  bw=%d kw=%d c_flag=%d all1=%d ct=%s: coeff=%d" % (bw, kw, c_flag, all1, ct, coeff % MOD))
    if c_flag == 0 and x1sub:
        for (x1,ct2), c in sorted(x1sub.items()):
            print("    x1=%d ct=%d → %d" % (x1, ct2, c % MOD))
    if xseqs:
        for xs, c in xseqs[:8]:
            print("    xseq=%s → %d" % (xs, c % MOD))

# Now trace each T ∈ D_4 through the wrapping process
print("\n\n=== Manual wrapper trace: T → (T) for each T ∈ D_4 ===")
for k4 in range(4, 5):
    words4 = generate_dyck(4)
    for T in words4:
        X_T, _ = x_seq_and_bob(T)
        c_T = 0
        for xx in X_T:
            if xx == 1: c_T += 1
            else: break
        
        T_wrapped = '(' + T + ')'
        Xw_real, _ = x_seq_and_bob(T_wrapped)
        bw_real = sum(j*Xw_real[j] for j in range(len(Xw_real)))
        kw_real = len(Xw_real)
        al_T = alice_of(T)
        al_w = 2*5 - 1  # 2k-1 where k=5 (wrapped size)
        
        Xw_pair = pair_seq([1]+X_T)
        bw_pair = sum(j*Xw_pair[j] for j in range(len(Xw_pair)))
        kw_pair = len(Xw_pair)
        
        print("  T=%-20s X(T)=%-10s c=%d pair→%-10s bw=%d kw=%d  real→%-10s bw=%d kw=%d al(T)=%d" % (
            T, str(X_T), c_T, str(Xw_pair), bw_pair, kw_pair, str(Xw_real), bw_real, kw_real, al_T))

# Now trace the EXACT mechanism: Which H[4] entry should produce each T?
print("\n\n=== Match T to H[4] entries ===")
# For each T, find its (bw,kw) in H[4]
for T in words4:
    X_T, _ = x_seq_and_bob(T)
    Xw_T = pair_seq([1]+X_T)
    bw_T = sum(j*Xw_T[j] for j in range(len(Xw_T)))
    kw_T = len(Xw_T)
    c_T = 0
    for xx in X_T:
        if xx == 1: c_T += 1
        else: break
    al_T = alice_of(T)
    
    # Find matching H[4] entry
    matched = []
    for hkey, (coeff, x1sub, xseqs) in alpha_H[4].items():
        bw_h, kw_h, c_flag, all1, ct = hkey
        if bw_h != bw_T or kw_h != kw_T: continue
        matched.append((hkey, coeff, x1sub, xseqs))
    
    A = '(' + T + ')'
    print("  T=%s al=%d X(T)=%s c=%d → X((T)) bw=%d kw=%d" % (T, al_T, X_T, c_T, bw_T, kw_T))
    for hkey, coeff, x1sub, xseqs in matched:
        print("    H[4] entry: c_flag=%d all1=%d ct=%s coeff=%d" % (hkey[2], hkey[3], hkey[4], coeff % MOD))
        if x1sub:
            for (x1,ct2), c in sorted(x1sub.items()):
                print("      x1=%d ct=%d → %d" % (x1, ct2, c % MOD))
        if xseqs:
            for xs, c in xseqs[:5]:
                print("      xseq=%s → %d" % (xs, c % MOD))

# Specific trace: the primitive c=0 process for X(T)=[1,2,1] → (T) should give Xw=[2,3]
print("\n\n=== Specific trace: primitive c=0 for T with X(T)=[1,2,1] ===")
for T in words4:
    X_T, _ = x_seq_and_bob(T)
    if X_T != [1, 2, 1]: continue
    print("T=%s X(T)=%s" % (T, X_T))
    # This T has c=1 (x1=1). In H[4], this T's wrapped version X((T)) has some (bw,kw)
    # The primitive c=0 at k=5 wraps (T) to get H[5] entry
    
    # H[5] should have (T) → X(((T)))
    A = '(' + T + ')'
    X_A, _ = x_seq_and_bob(A)
    Xw_A = pair_seq([1]+X_A)
    bw_A = sum(j*Xw_A[j] for j in range(len(Xw_A)))
    kw_A = len(Xw_A)
    al_A = alice_of(A)
    print("  (T)=%s X(A)=%s Xw(A)=%s bw=%d kw=%d al=%d" % (A, X_A, Xw_A, bw_A, kw_A, al_A))

# Specific trace: the primitive c=0 for X(T)=[2,1,2] → (T) should give Xw=[2,3] or [3,3]?
print("\n=== Specific: primitive c=0 for T with X(T)=[2,1,2] ===")
for T in words4:
    X_T, _ = x_seq_and_bob(T)
    if X_T != [2, 1, 2]: continue
    print("T=%s X(T)=%s" % (T, X_T))
    A = '(' + T + ')'
    X_A, _ = x_seq_and_bob(A)
    Xw_A = pair_seq([1]+X_A)
    bw_A = sum(j*Xw_A[j] for j in range(len(Xw_A)))
    kw_A = len(Xw_A)
    al_A = alice_of(A)
    print("  (T)=%s X(A)=%s Xw(A)=%s bw=%d kw=%d al=%d" % (A, X_A, Xw_A, bw_A, kw_A, al_A))
