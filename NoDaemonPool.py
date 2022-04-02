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

# class NoDaemonProcess(mp.Process):
#     def _get_daemon(self):
#         return False
#     def _set_daemon(self, value):
#         pass
#     daemon = property(_get_daemon, _set_daemon)

# class NoDaemonPool(mpp.Pool):
#     Process = NoDaemonProcess
