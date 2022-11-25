import sys

argu = sys.argv[1]
for x in range(0,int(argu)):    
    file = open("{0}.txt".format(x+1),'w')
    file.write("2\n")
    file.write("{0}\n".format(x+1))
    file.write("{0}\n".format(x+1))
    file.write("q")
    file.close()
