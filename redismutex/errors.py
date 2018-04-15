class MutexLockError(Exception):
    """Exception when mutex lock fails
    """
    pass


class MutexUnlockError(Exception):
    """Exception when mutex unlock fails
    """
    pass


class BlockTimeExceedError(Exception):
    """Exception when acquiring mutex lock exceed the allwed block time
    """
    pass
