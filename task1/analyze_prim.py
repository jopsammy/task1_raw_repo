# Analyze: how bob((A)) relates to bob(A), k(A)
def gen_all(n):
    res=[]
    def dfs(o,c,s):
        if len(s)==2*n: res.append(s);return
        if o<n: dfs(o+1,c,s+'(')
        if c<o: dfs(o,c+1,s+')')
    dfs(0,0,'');return res

def x_seq(s):
    n=len(s)//2;l=0;xs=[]
    while l<n:
        best=0
        for x in range(1,n-l+1):
            if s[:2*l+x].count('(')==l+x: best=x
        xs.append(best);l+=best
    return xs

def bob(s): xs=x_seq(s);return sum((j-1)*x for j,x in enumerate(xs,1))

def alice(s):
    ans=0
    for i,ci in enumerate(s):
        if ci=='(':
            for j in range(i+1,len(s)):
                if s[j]==')': ans+=1
    return ans

for n in range(1,6):
    prims=[]
    for s in gen_all(n):
        # check primitive
        bal=0;ok=True
        for i,c in enumerate(s):
            bal+=1 if c=='(' else -1
            if bal==0 and i<len(s)-1: ok=False;break
        if ok: prims.append(s)

    print(f"\nn={n}: {len(prims)} primitives")
    for p in prims:
        xs=x_seq(p);k=len(xs);a=alice(p);b=bob(p)
        print(f"  {p:20s}  alice={a:3d}  bob={b:2d}  k={k}  x={xs}")