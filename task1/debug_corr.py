MOD=998244353;a=2;b=3;ib=pow(3,MOD-2,MOD)
pa=[1];pb=[1];pib=[1]
for i in range(1,500):pa.append(pa[-1]*a%MOD);pb.append(pb[-1]*b%MOD);pib.append(pib[-1]*ib%MOD)

def x_seq(s):
    n=len(s)//2;l=0;xs=[]
    while l<n:
        best=0
        for x in range(1,n-l+1):
            if s[:2*l+x].count('(')==l+x:best=x
        xs.append(best);l+=best
    return xs
alice=lambda s:sum(1 for i,ci in enumerate(s) if ci=='(' for j in range(i+1,len(s)) if s[j]==')')
bob=lambda s:sum((j-1)*x for j,x in enumerate(x_seq(s),1))
k=lambda s:len(x_seq(s))

# Correct primitive contributions by brute
def prim_brute(n):
    res=[]
    def dfs(o,c,s):
        if len(s)==2*n:
            bal=0;ok=True
            for i,ch in enumerate(s):
                bal+=1 if ch=='(' else -1
                if bal==0 and i<len(s)-1:ok=False;break
            if ok:res.append(s)
            return
        if o<n:dfs(o+1,c,s+'(')
        if c<o:dfs(o,c+1,s+')')
    dfs(0,0,'');return res

for n in range(1,6):
    prims=prim_brute(n)
    pn=sum(pa[alice(s)]*pb[bob(s)]%MOD for s in prims)%MOD
    print(f"P{n}[0] brute = {pn}")