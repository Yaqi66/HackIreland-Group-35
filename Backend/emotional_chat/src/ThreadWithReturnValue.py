"""
A Thread subclass that can return a value from its target function
"""
import threading

class ThreadWithReturnValue(threading.Thread):
    """Thread that can return a value from its target function"""
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        """Initialize the thread with the same parameters as threading.Thread"""
        if kwargs is None:
            kwargs = {}
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self._return = None

    def run(self):
        """Run the thread's target function and store its return value"""
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        """Wait for the thread to complete and return its value"""
        super().join(timeout)
        return self._return