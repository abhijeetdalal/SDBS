import csv

file="insurance"
counts = []

for d in csv.DictReader(open(file+'.csv'), delimiter='\t'):
    counts.append((d[file]))
 

print 'Words = ', counts


for i in range(0,len(counts)):
    print counts[i]
