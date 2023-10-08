"""Error handling classes."""


class MockarooError(Exception):
    """Base exception class for Mockaroo API errors."""

    pass


class ApiKeyNotFound(MockarooError):
    """Raised when the API key is not found."""

    def __init__(self):
        super().__init__("API key is required. export API_KEY=mockaroo_api_key")


class InvalidApiKeyError(MockarooError):
    """Raised when the API key is invalid."""

    pass


class UsageLimitExceededError(MockarooError):
    """Raised when the API usage limit is exceeded."""

    pass
