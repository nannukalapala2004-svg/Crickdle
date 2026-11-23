import json,glob,collections,sys
src=sys.argv[1]
apps=collections.Counter(); teams=collections.defaultdict(set); seasons=collections.defaultdict(set); ids={}
names=collections.defaultdict(set)
for f in glob.glob(src+'/*.json'):
    d=json.load(open(f)); i=d['info']
    reg=i['registry']['people']
    for t,pl in i['players'].items():
        for p in pl:
            pid=reg[p]; apps[pid]+=1; teams[pid].add(t); seasons[pid].add(str(i['season'])); names[pid].add(p)
print('players',len(apps))
for th in (1,5,10,20,30,50,100):
    print(th, sum(1 for v in apps.values() if v>=th))
multi=[(k,v) for k,v in names.items() if len(v)>1]; print('multi-name ids',len(multi), multi[:5])
allteams=collections.Counter(t for s in teams.values() for t in s); print(allteams)
print(sorted(set(s for v in seasons.values() for s in v)))
