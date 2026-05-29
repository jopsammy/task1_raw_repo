with open('verifyback/18/18.out', 'rb') as f: a=f.read().decode('utf-8-sig').split()
with open('my18_out.txt', 'rb') as f: b=f.read().decode('utf-8-sig').split()
d=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
print(f'n=500: {len(a)} nums, diffs={len(d)}/{len(a)}')
for i in d[:10]:
    print(f'  F_{i+1}: exp=...{a[i][-20:]} got=...{b[i][-20:]}')