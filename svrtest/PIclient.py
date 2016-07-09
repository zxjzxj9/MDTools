import xmlrpclib
import numpy as np

class ServerProxy(object):
    def __init__(self, url):
        self._xmlrpc_server_proxy = xmlrpclib.ServerProxy(url)
    def __getattr__(self, name):
        call_proxy = getattr(self._xmlrpc_server_proxy, name)
        def _call(*args, **kwargs):
            return call_proxy(args, kwargs)
        return _call


if __name__ == "__main__":

    lattice = [[10.00,0.00,0.00],[0.00,10.00,0.00],[0.00,0.00,10.00]]

    atmlist = [1,2,2]

    coord = [ \
              [4.888906, 4.190531, 5.341819], \
              [4.518590, 4.930775, 6.081417], \
              [5.998905, 4.191843, 5.340974], \
            ]

    na = 3
    server = ServerProxy("http://localhost:8000")
    exe = "/home/zxj/program/siesta-4.0b-485/Obj/siesta"
    srcdir = "/home/zxj/program/siesta-4.0b-485/PIMD/svrtest"
    tmpfolder = '/home/zxj/program/siesta-4.0b-485/PIMD/client/tmp'
    
    for i in range(100):
        output = server.calcEF(coord,lattice,atmlist,exe = exe,srcdir = srcdir, tmpfolder = tmpfolder)
        energy,force,stress = output
        coord = (np.array(coord) + 0.01 * np.array(force)).tolist()
        #print np.array(force)
        print max(np.abs(np.array(force)).flatten())

    print output
