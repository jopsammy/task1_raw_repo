import sys
MOD = 998244353

def gen_all_dyck(n):
    res = []
    def dfs(o, c, s):
        if len(s) == 2 * n:
            res.append(s)
            return
        if o < n: dfs(o+1,c,s+'(')
        if c < o: dfs(o,c+1,s+')')
    dfs(0,0,'')
    return res

def x_seq(s):
    n=len(s)//2;l=0;xs=[]
    while l<n:
        best=0
        for x in range(1,n-l+1):
            if s[:2*l+x].count('(')==l+x: best=x
        xs.append(best);l+=best
    return xs

def alice(s):
    ans=0
    for i,ci in enumerate(s):
        if ci=='(':
            for j in range(i+1,len(s)):
                if s[j]==')': ans+=1
    return ans

def bob(s): xs=x_seq(s); return sum((j-1)*x for j,x in enumerate(xs,1))

def brute_g(n,a,b,L):
    words=gen_all_dyck(n); t=0
    for s in words:
        k=len(x_seq(s))
        t=(t+pow(a,alice(s),MOD)*pow(b,bob(s)+k*L,MOD))%MOD
    return t

# DP calculation matching solution.py
def dp_g(N, a_val, b_val):
    max_exp = N * N + 2 * N + 5
    pow_a = [1] * (max_exp + 1)
    pow_b = [1] * (max_exp + 1)
    for i in range(1, max_exp + 1):
        pow_a[i] = pow_a[i - 1] * a_val % MOD
        pow_b[i] = pow_b[i - 1] * b_val % MOD

    G = []
    for i in range(N + 1):
        size = N - i + 1
        G.append([0] * size)

    for L in range(N + 1):
        G[0][L] = 1

    for L in range(N):
        G[1][L] = a_val * pow_b[L] % MOD

    for n in range(2, N + 1):
        Gn = G[n]
        Gn1 = G[n - 1]
        max_L = N - n

        for L in range(max_L + 1):
            total = pow_a[2 * n - 1] * Gn1[L] % MOD
            total = (total + pow_a[n] * pow_b[L + n - 1] % MOD * Gn1[L]) % MOD

            for a in range(1, n - 1):
                b_size = n - a - 1
                factor = pow_a[(a + 1) * b_size + 2 * (a + 1) - 1]
                term = factor * G[a][L + b_size] % MOD * G[b_size][L] % MOD
                total = (total + term) % MOD

            Gn[L] = total

    return G

a_val=2; b_val=3; N=4
G = dp_g(N, a_val, b_val)

for L in range(N+1):
    for n in range(min(N+1, N-L+1)):
        bg = brute_g(n, a_val, b_val, L)
        dg = G[n][L]
        ok = "OK" if bg==dg else "FAIL"
        print(f"n={n} L={L}: brute={bg:10d} dp={dg:10d} {ok}")
    print()

print("F_n (brute) for n=1..4:")
for n in range(1,5):
    print(f"  F_{n}={brute_g(n,a_val,b_val,0)}")