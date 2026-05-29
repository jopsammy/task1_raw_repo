import sys;sys.path.insert(0,'.')
from solution import solve

# Brute force for small n
MOD=998244353

def gen(n):
    res=[]
    def dfs(o,c,s):
        if len(s)==2*n:res.append(s);return
        if o<n:dfs(o+1,c,s+'(')
        if c<o:dfs(o,c+1,s+')')
    dfs(0,0,'');return res

def alice(s):
    ans=0
    for i,ci in enumerate(s):
        if ci=='(':
            for j in range(i+1,len(s)):
                if s[j]==')':ans+=1
    return ans

def bob_count(s):
    n=len(s)//2;l=0;total=0
    while l<n:
        best=0
        for x in range(1,n-l+1):
            if s[:2*l+x].count('(')==l+x:best=x
        l+=best;total+=n-l
    return total

def brute_f(n,a,b):
    w=gen(n);t=0
    for s in w:t=(t+pow(a,alice(s),MOD)*pow(b,bob_count(s),MOD))%MOD
    return t

for n in range(1,9):
    a=2;b=3
    bf=brute_f(n,a,b)
    dp=solve(n,a,b)[n-1]
    print(f"n={n}: brute={bf} dp={int(dp)} {'OK' if bf==int(dp) else 'FAIL'}")