"""A Python Package for the Mockaroo API"""
from .client import Client
from .exceptions import MockarooError, InvalidApiKeyError, UsageLimitExceededError

__all__ = ["Client", "MockarooError", "InvalidApiKeyError", "UsageLimitExceededError"]
__version__ = "1.0.0"
