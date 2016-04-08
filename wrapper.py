#! /usr/bin/env python

# Simple wrapper of calcRDF written by Python
# Written by zxj, 2016/4/7

# class to parse *.arc trajectory
import numpy as np
import matplotlib.pyplot as plt
import ctypes
from math import sin,cos,pi,sqrt

class TrajReader:
    def __init__(self,fn):
        self.fn = fn
        self.fh = open(fn,"r") # get file handle
        # get the atom number:
        self.na = 0 
        for line in self.fh:
            if line.startswith("end"): break
            self.na += 1
        self.na -= 5
        self.fh.seek(0,0)
        # skip the initial two lines
        self.fh.readline()
        self.fh.readline()
        #print "Atom number:",self.na

    def __iter__(self):
        return self

    def __next__(self):
        strinfo = StrObj(self.na)
        strinfo.note = self.fh.readline()
        self.fh.readline()
        strinfo.cell = self.fh.readline()
        #strinfo.data = strinfo.note
        for i in range(self.na):
            strinfo.data.append(self.fh.readline())

        self.fh.readline()
        end = self.fh.readline()

        if not end:
            self.fh.close()
            raise StopIteration

        strinfo.parse()
        return strinfo

# class to obtain the structure object
class StrObj:
    def __init__(self,na):
        self.na = na
        self.data = []  

# data are finally strored in three variables
# self.elem
# self.coord
# self.lattice

    def parse(self):
        if not self.data:
            raise Exception("null data info!!!")
        self.elem = []
        self.coord = []
        for line in self.data:
            # print line
            tmp = line.split()
            self.elem.append(tmp[0])
            self.coord.append(list(map(lambda x:float(x),tmp[1:4])))
        #print(self.cell.split()[1:7])
        self.lattice = self.lattvec(list(map(lambda x:float(x),self.cell.split()[1:7])))

    def lattvec(self,abc):
        a = abc[0]
        b = abc[1]
        c = abc[2]
        alf = abc[3]
        bet = abc[4]
        gam = abc[5]
        latt = [[0 for col in range(3)] for row in range(3)]
        latt[0][0] = a
        latt[0][1] = b*cos(gam*pi/180.0)
        latt[1][1] = b*sin(gam*pi/180.0)
        latt[0][2] = c*cos(bet*pi/180.0)
        latt[1][2] = (b*c*cos(alf*pi/180.0) - \
        latt[0][1]*latt[0][2])/latt[1][1]
        latt[2][2] = sqrt(c**2-latt[0][2]**2- latt[1][2]**2)
        return latt

# Main program

if __name__ == "__main__":

    shlib = ctypes.cdll.LoadLibrary("./calcRDF.so")
    func = shlib.basicRDF

    ntot = 9
    na = 9
    nb = 9
    aser = range(9)
    bser = range(9)

    cntot = ctypes.c_int(ntot)
    cna = ctypes.c_int(na)
    cnb = ctypes.c_int(nb)
    caser = (ctypes.c_int*na)(*aser)
    cbser = (ctypes.c_int*nb)(*bser)

    nbins = 400
    
    cnbins = ctypes.c_int(nbins)
    cbinsize = ctypes.c_double(0.05)
    RDF = np.zeros(nbins)
    cRDF = (ctypes.c_double*nbins)(0)

    cnt = 0
    for data in TrajReader("data1.arc"):
        cnt += 1
        ccoord = (ctypes.c_double*(3*ntot))(*(np.array(data.coord).flatten(order='C').tolist()))
        clatt = (ctypes.c_double*(9))(*(np.array(data.lattice).flatten(order='C').tolist()))
        func(cna,caser,cnb,cbser,cntot,ccoord,clatt,cnbins,cbinsize,cRDF)
        RDF += np.array(cRDF)

    RDF = RDF/cnt

    Xdata = np.arange(len(RDF))*0.05
    plt.plot(Xdata,RDF)
    plt.show()
   
    acc = 0.0
    for _x,_y in zip(Xdata,RDF):
        if _x < 3.54:
            acc += _y

    acc = acc*0.05
    print("Average coordination number: %12.6f" %acc)

