"""Error handling classes."""


class MockarooError(Exception):
    """Base exception class for Mockaroo API errors."""

    pass


class InvalidApiKeyError(MockarooError):
    """Raised when the API key is invalid."""

    pass


class UsageLimitExceededError(MockarooError):
    """Raised when the API usage limit is exceeded."""

    pass
