import time
import subprocess as sp
import os
import shutil
import sys
import string
from time import localtime, strftime

# xfoil_lib.py
# - Executes Xfoil
#   - xfoil_alt: Function to alter airfoil geometry and run it
#   - xfoil_run_flap: Function to iterate flap alpha
#   - xfoil_run:  Function to execute xfoil
#   - xfoil_final:  Final xfoil airfoil altering
#   - getdata_xfoil: Return lift and drag data from xfoil run

print("Current Path", os.getcwd())
xfoilpath = './Aerodynamics/xfoil'
print("Xfoil Path", xfoilpath)


def xfoil_alt(name, camber, max_camb_pos, thickness, max_thick_pos, Re, alpha ):
    # Alter, run, and save
    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')


    try:
        os.remove(name+'_data.dat')
    except :
        pass
    #    print ("no such file")
    # run xfoil
    ps = sp.Popen( xfoilpath ,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    Cmd('PLOP')
    Cmd('G')
    Cmd(' ')


    Cmd('load ./airfoils/'+name+'.dat')
    Cmd('load ./airfoils/E420.dat')

    # alter geometry
    Cmd('GDES')
    Cmd('TSET')
    Cmd(str(thickness))
    Cmd(str(camber))
    Cmd('HIGH')
    Cmd(str(max_thick_pos))
    Cmd(str(max_camb_pos))   
    Cmd('x')
    Cmd(' ')
    Cmd(' ')

 
    # increase panling 
    # Cmd('PANE')
    Cmd('PPAR')
    Cmd('N')
    Cmd('150')
    Cmd(' ')
    Cmd(' ')



    # calculate data
    Cmd('OPER')
    Cmd('ITER 100')
    Cmd('visc '+str(Re))
    Cmd('PACC')
    Cmd(name+'_data.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('a '+str(alpha))
    Cmd('PACC')
    Cmd('PDEL 0')
    Cmd(' ')

    Cmd(' ')
    Cmd('SAVE')
    Cmd('./airfoils/'+name+'.dat')
    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()

def xfoil_run_flap(name, Re, alpha_start, alpha_end ):
    # Makes a flap, run
    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')


    try:
        os.remove('elev_data_flap.dat')
    except :
        pass

    try:
        os.remove('elev_data.dat')
    except :
        pass
    #    print ("no such file")
    # run xfoil
    ps = sp.Popen(xfoilpath,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    # Cmd('PLOP')
    # Cmd('G')
    # Cmd(' ')

    Cmd(name)

    Cmd('GDES')
    Cmd('FLAP')
    Cmd('0.5')
    Cmd('0')
    Cmd('-20')   
    Cmd('x')
    Cmd(' ')
    Cmd(' ')
    # increase panling 
    Cmd('PPAR')
    Cmd('N')
    Cmd('250')
    Cmd(' ')
    Cmd(' ')
    Cmd(' ')

    # calculate data
    Cmd('OPER')
    Cmd('ITER 200')
    Cmd('visc '+str(Re))
    Cmd('PACC')
    Cmd('elev_data_flap.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq '+str(alpha_start)+' ' + str(alpha_end) + ' 1')


    # time.sleep(5)
    Cmd('PACC')
    Cmd('PDEL 0')

    Cmd(' ')
    Cmd(' ')  

    Cmd(name)
    # increase panling 
    Cmd('GDES')
    Cmd(' ')


    # calculate data
    Cmd('OPER')
    Cmd('PACC')
    Cmd('elev_data.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq '+str(alpha_start)+' ' + str(alpha_end) + ' 1')
    Cmd('PACC')
    Cmd('PDEL 0')

    Cmd(' ')
           

    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()


def xfoil_run(name, Re, alpha_start, alpha_end ):
    # Run xfoil without alterring airfoil
    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')


    try:
        os.remove(name+'_data.dat')
    except :
        pass
    #    print ("no such file")
    # run xfoil
    ps = sp.Popen(xfoilpath,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    # Cmd('PLOP')
    # Cmd('G')
    # Cmd(' ')

    Cmd('load '+name+'.dat')

    
    # increase panling 
    Cmd('PANE')
    Cmd('PPAR')
    Cmd('N')
    Cmd('250')
    Cmd(' ')
    Cmd(' ')

    # calculate data
    Cmd('OPER')
    Cmd('ITER 200')
    Cmd('visc '+str(Re))
    Cmd('PACC')
    Cmd(name+'_data.dat')  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq '+str(alpha_start)+' ' + str(alpha_end) + ' 1')
    Cmd('PACC')
    Cmd('PDEL')

    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()

def xfoil_final(name, camber, max_camb_pos, thickness, max_thick_pos):
    # Alter, run, save picture of xfoil
    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')


    try:
        os.remove(name+'_data.dat')

    except :
        pass
    #    print ("no such file")
    # run xfoil
    ps = sp.Popen( xfoilpath ,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    Cmd('PLOP')
    Cmd('G')
    Cmd(' ')


    # Cmd('load ./airfoils/'+name+'.dat')
    Cmd('load E420.dat')

    # alter geometry
    Cmd('GDES')
    Cmd('TSET')
    Cmd(str(thickness))
    Cmd(str(camber))
    Cmd('HIGH')
    Cmd(str(max_thick_pos))
    Cmd(str(max_camb_pos))   
    Cmd('x')
    Cmd(' ')
    Cmd(' ')

    Cmd('SAVE')
    Cmd('./airfoils/'+name+'.dat')
    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()




def getData_xfoil(filename):
    # Getting data
    f = open(filename, 'r')
    flines = f.readlines()

    alphas = []
    Cls = []
    Cds = []
    Cms =  []
   

    for i in range(12,len(flines)): 
        words = string.split(flines[i]) 
        alphas.append(float(words[ 0]))
        Cls.append(float(words[ 1]))
        Cds.append(float(words[ 2]))
        Cms.append(float(words[ 4]))

    LtoDs = [a/b for a,b in zip(Cls,Cds)]

    return (alphas, Cls, Cds, Cms, LtoDs)

# def getLDmax(name):
#     filename = name+"_data.dat"
#     f = open(filename, 'r')
#     flines = f.readlines()
#     LDmax = 0
#     for i in range(12,len(flines)):
#         #print flines[i]
#         words = string.split(flines[i]) 
#         LD = float(words[1])/float(words[2])
#         if(LD>LDmax):
#             LDmax = LD
#     return LDmax