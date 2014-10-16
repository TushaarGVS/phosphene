f = open('out','r')
prev_x = float(f.next()[:-1])
maxVal = 0
count = 0
avg = 0
aaa = 0
for line in f:
    try:
        diff = float(line[:-1]) - prev_x
    except:
        print line
        continue
    prev_x = float(line[:-1])
    avg+=diff
    count+=1
    maxVal = max(maxVal,diff)
    if diff>0.04:
        aaa+=1
        print diff
print "max=",maxVal
print "avg=",avg/float(count)
print aaa
print count
