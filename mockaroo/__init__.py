"""A Python Package for the Mockaroo API."""
from .api.client import Client
from .api.exceptions import MockarooError, InvalidApiKeyError, UsageLimitExceededError

__all__ = ["Client", "MockarooError", "InvalidApiKeyError", "UsageLimitExceededError"]
__version__ = "2.0.0"
