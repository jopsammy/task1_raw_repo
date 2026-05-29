# Compare DP vs brute for n=1..8
MOD = 998244353

def gen_all(n):
    res=[]
    def dfs(o,c,s):
        if len(s)==2*n: res.append(s);return
        if o<n: dfs(o+1,c,s+'(')
        if c<o: dfs(o,c+1,s+')')
    dfs(0,0,'');return res

def x_seq(s): n=len(s)//2;l=0;xs=[];return xs  # ... we don't need it for brute sum

def alice(s):
    ans=0
    for i,ci in enumerate(s):
        if ci=='(': ans+=sum(1 for j in range(i+1,len(s)) if s[j]==')')
    return ans

def bob_count(s):
    n=len(s)//2;l=0;total=0
    while l<n:
        best=0
        for x in range(1,n-l+1):
            if s[:2*l+x].count('(')==l+x: best=x
        l+=best; total+=n-l
    return total

def brute(a,b,n):
    words=gen_all(n)
    total=0
    for s in words:
        total=(total+pow(a,alice(s),MOD)*pow(b,bob_count(s),MOD))%MOD
    return total

# DP implementation (refined)
def dp(N,a,b):
    a%=MOD; b%=MOD
    max_exp=N*N+2*N+5
    pa=[1]*(max_exp+1); pb=[1]*(max_exp+1)
    for i in range(1,max_exp+1):
        pa[i]=pa[i-1]*a%MOD; pb[i]=pb[i-1]*b%MOD

    G=[[0]*(N-n+1) for n in range(N+1)]
    for L in range(N+1): G[0][L]=1
    for L in range(N): G[1][L]=a*pb[L]%MOD

    for n in range(2,N+1):
        Gn=G[n]; mL=N-n
        for L in range(mL+1):
            val=pa[2*n-1]*G[n-1][L]%MOD
            val=(val+pa[n]*pb[L+n-1]%MOD*G[n-1][L])%MOD
            for m in range(2,n):
                r=n-m
                if L+r<=N-m:
                    val=(val+pa[m*r]*G[m][L+r]%MOD*G[r][L])%MOD
            Gn[L]=val
    return [G[i][0] for i in range(1,N+1)]

a=2;b=3
for n in range(1,9):
    bf=brute(a,b,n)
    dpv=dp(n,a,b)
    print(f"n={n}: brute={bf} dp={dpv[n-1]} {'OK' if bf==dpv[n-1] else 'FAIL'}")