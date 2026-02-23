"""
Custom exceptions for the RUCKUS One (R1) SDK.
"""


class RuckusOneError(Exception):
    """Base exception for all RUCKUS One SDK errors."""
    pass


class AuthenticationError(RuckusOneError):
    """Exception raised for authentication errors."""
    pass


class APIError(RuckusOneError):
    """Exception raised for API errors."""
    
    def __init__(self, status_code=None, detail=None, message=None):
        """
        Initialize the APIError exception.
        
        Args:
            status_code: HTTP status code
            detail: Detailed error information
            message: Error message
        """
        self.status_code = status_code
        self.detail = detail
        self.message = message or str(detail) or f"API Error (Status: {status_code})"
        super().__init__(self.message)


class ResourceNotFoundError(APIError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, detail=None, message=None):
        """
        Initialize the ResourceNotFoundError exception.
        
        Args:
            detail: Detailed error information
            message: Error message
        """
        super().__init__(status_code=404, detail=detail, message=message or "Resource not found")


class ValidationError(APIError):
    """Exception raised when request validation fails."""
    
    def __init__(self, detail=None, message=None):
        """
        Initialize the ValidationError exception.
        
        Args:
            detail: Detailed error information
            message: Error message
        """
        super().__init__(status_code=400, detail=detail, message=message or "Validation error")


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, detail=None, message=None):
        """
        Initialize the RateLimitError exception.
        
        Args:
            detail: Detailed error information
            message: Error message
        """
        super().__init__(status_code=429, detail=detail, message=message or "Rate limit exceeded")


class ServerError(APIError):
    """Exception raised for server-side errors."""
    
    def __init__(self, status_code=None, detail=None, message=None):
        """
        Initialize the ServerError exception.
        
        Args:
            status_code: HTTP status code
            detail: Detailed error information
            message: Error message
        """
        status_code = status_code or 500
        super().__init__(
            status_code=status_code,
            detail=detail,
            message=message or f"Server error occurred (Status: {status_code})"
        )