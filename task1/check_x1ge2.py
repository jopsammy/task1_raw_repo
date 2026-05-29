import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, x_seq_and_bob

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N = 8
wrong_identity = 0
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        if X[0] >= 2 and (bobw != bob or kw != len(X)):
            wrong_identity += 1
            if wrong_identity <= 5:
                print(f"COUNTEREXAMPLE: {s}, X={X}, x1={X[0]}, bob={bob}, k={len(X)}, bobw={bobw}, kw={kw}, Xw={Xw}")

print(f"\nTotal x1>=2 trees where wrapping is NOT identity: {wrong_identity}")

identity_ok = 0
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        if X[0] >= 2 and bobw == bob and kw == len(X):
            identity_ok += 1

print(f"Total x1>=2 trees where wrapping IS identity: {identity_ok}")
