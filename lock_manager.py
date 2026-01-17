class LockManager:
    def __init__(self):
        """
        TODO:
        - manage locks for state
        - може да включва RWLock или CAS
        """
        pass

    def acquire_write(self):
        """
        TODO:
        - блокира write на state
        """
        pass

    def release_write(self):
        """
        TODO:
        - освобождава write lock
        """
        pass

    def acquire_read(self):
        """
        TODO:
        - lock-free или краткосрочно read lock
        """
        pass

    def release_read(self):
        """
        TODO:
        - release read lock
        """
        pass
