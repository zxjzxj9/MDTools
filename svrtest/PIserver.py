import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
import tempfile
import os
import shutil
import glob
import string
import subprocess
import threading
from lxml import etree

# Threadpool needed
from multiprocessing import Pool


# This function calc the energy and force using SIESTA package
# Suitable for other packages with slight modification

# https://stackoverflow.com/questions/1589150/python-xmlrpc-with-concurrent-requests
# Good solution!
class RPCThreading(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# https://stackoverflow.com/questions/119802/using-kwargs-with-simplexmlrpcserver-in-python
class Server(object):
    def __init__(self, hostport):
#        threading.Thread.__init__(self)
        self.server = RPCThreading(hostport)

    def register_function(self, function, name=None):
        def _function(args, kwargs):
            return function(*args, **kwargs)
        _function.__name__ = function.__name__
        self.server.register_function(_function, name)
        self.server.register_introspection_functions()
        self.server.register_multicall_functions()

    def serve_forever(self):
        self.server.serve_forever()




def calcEF(coords,lattice,atmlist, srcdir = None, ncpu = 12, projname = 'test', template = 'INPUT_DEBUG.template', exe = None, tmpfolder = None):
   
    # it does not support kwargs !!!
    # srcdir = kwargs['srcdir'] if 'srcdir' in kwargs else None
    # ncpu = kwargs['ncpu'] if 'ncpu' in kwargs else 12
    # projname = kwargs['projname'] if 'projname' in kwargs else 'test'
    # template = kwargs['template'] if 'template' in kwargs else 'INPUT_DEBUG.template'
    # exe = kwargs['exe'] if 'exe' in kwargs else None
    # tmpfolder = kwargs['tmpfolder'] if 'tmpfolder' in kwargs else None

    # we suppose all the key data are in the INPUT_DEBUG.template file
    if not srcdir: # if source dir is None, use pwd as source dir
        srcdir = os.getcwd()
    cwd = os.getcwd()

    # for single calculation
    if not tmpfolder:
        tmpfolder = tempfile.mkdtemp(suffix='siesta')

    psffiles = glob.glob(os.path.join(srcdir,"*.psf"))
    # The following works are done in the temporary folder
    os.chdir(tmpfolder)
    # copy all psf files
    for psffile in psffiles:
        shutil.copy(psffile,tmpfolder)

    # generate the INPUT_DEBUG file
    fin = open(os.path.join(srcdir,template),"r")
    tp = string.Template(fin.read())
    fin.close()

    # use lattice vector and cartesian coordinates
    sd = {}
    sd['lattice'] = "%12.6f%12.6f%12.6f\n"*3 %( \
                                               lattice[0][0],lattice[1][0],lattice[2][0],\
                                               lattice[0][1],lattice[1][1],lattice[2][1],\
                                               lattice[0][2],lattice[1][2],lattice[2][2],\
                                              )

    sd['coord'] = ''
    for coord,atm in zip(coords,atmlist):
        sd['coord'] += "%12.6f%12.6f%12.6f%5d\n" %(coord[0],coord[1],coord[2],atm)

    sd['na'] = '%d' %len(atmlist)
    sd['name'] = projname

    data = tp.substitute(sd)

    f = open('INPUT_DEBUG','w')
    f.write(data)
    f.close()

    if not exe:
        exe = os.path.join(srcdir,'siesta')

    print "Executing SIESTA"
    subprocess.call("source /home2/shang/.bashrc &> /dev/null; mpirun -np %d %s > siesta.out 2>&1 " %(ncpu,exe), shell=True)
    print "END execution"

    # after run, get data
    xmldoc = etree.parse('./%s.xml' %projname)

    energydata = xmldoc.xpath("//*[local-name()='property'][@dictRef='siesta:E_KS']")[-1].xpath("./*/text()")[0] # in eV
    # print energydata
    forcedata = xmldoc.xpath("//*[local-name()='property'][@dictRef='siesta:forces']")[-1].xpath("./*/text()")[0].split() # in eV/A
    # print forcedata
    stressdata = xmldoc.xpath("//*[local-name()='property'][@dictRef='siesta:stress']")[-1].xpath("./*/text()")[0].split() # in eV/A**3
    # print stressdata

    energy = float(energydata)
    force = []

    # print energy
    for i in range(len(atmlist)):
        # print i
        force.append(map(lambda x: float(x),forcedata[3*i:3*i+3]))

    # print force
    stress = []
    for i in range(3):
        stress.append(map(lambda x: float(x), stressdata[3*i:3*i+3]))

    # print stress
    os.chdir(cwd)
    # should clean the folder, if not used
    return (energy,force,stress)

if __name__ == "__main__":

    server = Server(("localhost", 8000))
    server.register_function(calcEF)
    print "Listening on port 8000..."
    server.serve_forever()

    #pool = Pool(processes=6)
    #for i in range(6):
    #    res = pool.apply_async(server.serve_forever,())
    #pool.close()
    #pool.join()
    #pool.map(server.run,())
    #r = pool.wait()
    #server.start()
    #server.serve_forever()
