import matplotlib.pyplot as plt
import pulsatile_cylinder_generic2 as gen
import re
import os

fullrundir = gen.fullrundir
#fullrundir = '/Users/fanweikong/SimVascular-Tests/pulsatile_cylinder/polydata-tetgen-py/6-24-2018-231720'
def PlotResult(fullrundir):
    tlist = [0.025, 0.075,0.125,0.175]

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
                if len(tmp)>=4:
                    fea.append(float(tmp[3])/-10.)
                else:
                    fea.append(0)
                rR.append(float(tmp[1])/10.)
                analytic.append(float(tmp[2])/-10.)
            except:
                pass
            
        plt.figure(i+1)
        plt.scatter(rR,fea,color='r')
        plt.plot(rR,analytic,color='g')
        plt.title(title)
        axes = plt.gca()
        axes.set_xlim([min(rR),max(rR)])
        axes.set_ylim([-5.,50.])
        fp.close()
        
    plt.show()


PlotResult(fullrundir)
