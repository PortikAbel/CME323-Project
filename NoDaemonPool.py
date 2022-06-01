import multiprocessing.pool as mpp

class NoDaemonPool(mpp.Pool):
    def Process(self, *args, **kwds):
        proc = super(NoDaemonPool, self).Process(*args, **kwds)

        class NoDaemonProcess(proc.__class__):
            """Monkey-patch process to ensure it is never daemonized"""
            @property
            def daemon(self):
                return False

            @daemon.setter
            def daemon(self, _val):
                pass

        proc.__class__ = NoDaemonProcess
        return proc
