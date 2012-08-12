try:
    import fcntl
except ImportError:
    fcntl = None


if fcntl is None:
    # fcntl isn't available on Windows.  By default, handles aren't
    # inherited on Windows, so we can do nothing here.
    setCloseOnExec = unsetCloseOnExec = lambda fd: None
else:
    def setCloseOnExec(fd):
        """
        Make a file descriptor close-on-exec.
        """
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        flags = flags | fcntl.FD_CLOEXEC
        fcntl.fcntl(fd, fcntl.F_SETFD, flags)


    def unsetCloseOnExec(fd):
        """
        Make a file descriptor close-on-exec.
        """
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        flags = flags & ~fcntl.FD_CLOEXEC                                                                            
        fcntl.fcntl(fd, fcntl.F_SETFD, flags)
