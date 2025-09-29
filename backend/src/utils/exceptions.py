class UncringerException(Exception):
    """Base exception for Uncringer application"""
    pass


class FeatureExtractionError(UncringerException):
    """Raised when audio feature extraction fails"""
    pass


class PredictionError(UncringerException):
    """Raised when ML prediction fails"""
    pass


class StorageError(UncringerException):
    """Raised when storage operations fail"""
    pass


class AuthenticationError(UncringerException):
    """Raised when authentication fails"""
    pass