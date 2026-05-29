MOD=998244353
a=2;b=3;inv_b=pow(b,MOD-2,MOD)
pa=[1];pb=[1];pib=[1]
for i in range(1,200):pa.append(pa[-1]*a%MOD);pb.append(pb[-1]*b%MOD);pib.append(pib[-1]*inv_b%MOD)

c=4;n=5;r=n-1-c
dk=c//2;p=c//2
db_head=c*(c-1)//2-p*(p-1)
print(f"c={c} n={n} r={r} dk={dk} db_head={db_head}")

# A=()^4: alice=10, bob=6, k=4
# G4[0] naive contribution for A: a^10*b^6
cont_A=pa[10]*pb[6]%MOD
# P5 naive contribution: a^9*cont_A
P5_A_naive=pa[9]*cont_A%MOD
print(f"G4 naive for A: {cont_A}")
print(f"P5 naive for A: {P5_A_naive}")

# Actual (A)=(()()()()): alice=19, bob=2, k=2
actual=pa[19]*pb[2]%MOD
print(f"P5 actual: {actual}")

# total P5 naive
G4_0=2624512
P5_all_naive=pa[9]*G4_0%MOD
print(f"Total P5 naive: {P5_all_naive}")

# Correction formula
alice_pow=2*n-1+c+c*(c-1)//2+c*r
bob_pow=c*(c-1)//2+c*r
base=pa[alice_pow]*pb[bob_pow]%MOD
print(f"alice_pow={alice_pow} bob_pow={bob_pow} base={base}")

corr_mult=(pib[dk*0+dk*r+db_head]-1)%MOD
print(f"dk*L+dk*r+db_head = {dk*0+dk*r+db_head}")
print(f"b^{-(dk*r+db_head)} = {pib[dk*r+db_head]}")
print(f"corr_mult={corr_mult}")

delta=base*corr_mult%MOD
print(f"delta={delta}")
print(f"P5 corrected = {(P5_all_naive+delta)%MOD}")

# Expected brute
print(f"Expected P5[0] = 607649792")

# What should the correction be?
# actual P5 = P5_all_naive - naive_cont_A + actual_cont_A
# = P5_all_naive + (actual - naive_cont_A * pa[9])
correct_delta = (actual - P5_A_naive) % MOD
print(f"Correct delta should be: {correct_delta}")
print(f"P5 using correct delta: {(P5_all_naive+correct_delta)%MOD}")