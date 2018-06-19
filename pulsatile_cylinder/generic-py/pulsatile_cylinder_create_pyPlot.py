import matplotlib.pyplot as plt
#import pulsatile_cylinder_generic2 as gen
import re
import os

tlist = [0.025, 0.075,0.125,0.175]
#fullrundir = gen.fullrundir
fullrundir = '/Users/fanweikong/SimVascular-Tests/pulsatile_cylinder/polydata-tetgen-py/6-18-2018-20741'


for i in range(0,4):
    t = tlist[i]
    title = 'polydata_tetgen '+ 't/T='+str(t/0.2)
    rR = []
    analytic = []
    fea = []
    fp = open(fullrundir+'/profiles_for_'+str(t),'rU')
    next(fp)
    for line in fp:
        try:
            tmp = re.split('\t| |\n',line)
            print tmp
            if len(tmp)>=4:
                fea.append(float(tmp[3])/-10.)
            else:
                fea.append(0)
            print tmp[1]
            rR.append(float(tmp[1])/10.)
            analytic.append(float(tmp[2])/-10.)
        except:
            pass
        
    print rR
    print fea
    print len(rR)
    print len(fea)
    plt.figure(i+1)
    plt.scatter(rR,fea,color='r')
    plt.plot(rR,analytic,color='g')
    plt.title(title)
    axes = plt.gca()
    axes.set_xlim([min(rR),max(rR)])
    axes.set_xlim([-5.,50.])
    fp.close()
    
plt.show()