import sys;sys.path.insert(0,'.');from solution import solve
MOD=998244353;a=2;b=3
def gen(m):
    r=[];dfs=lambda o,c,s:(r.append(s) if len(s)==2*m else((o<m and dfs(o+1,c,s+'(')),(c<o and dfs(o,c+1,s+')'))))
    dfs(0,0,'');return r
def xs(s):
    m=len(s)//2;l=0;ys=[]
    while l<m:
        best=0
        for x in range(1,m-l+1):
            if s[:2*l+x].count('(')==l+x:best=x
        ys.append(best);l+=best
    return ys
al=lambda s:sum(1 for i,ci in enumerate(s) if ci=='(' for j in range(i+1,len(s)) if s[j]==')')
bo=lambda s:sum((j-1)*x for j,x in enumerate(xs(s),1))
def bf(n):return sum(pow(a,al(s),MOD)*pow(b,bo(s),MOD)%MOD for s in gen(n))%MOD
dp=solve(8,a,b)
for n in range(1,9):
    br=bf(n);d=int(dp[n-1]);ok="OK" if br==d else f"FAIL (br={br} dp={d} diff={(br-d)%MOD})"
    print(f"n={n}: {ok}")