"""
Shared exception classes
"""

class CRIPException(Exception):
    """Base exception for CRIP platform"""
    pass

class AuthenticationException(CRIPException):
    """Authentication related errors"""
    pass

class AuthorizationException(CRIPException):
    """Authorization related errors"""
    pass

class ValidationException(CRIPException):
    """Input validation errors"""
    pass

class ServiceException(CRIPException):
    """Service operation errors"""
    pass

class NotFoundException(ServiceException):
    """Resource not found"""
    pass

class ConflictException(ServiceException):
    """Resource conflict (e.g., duplicate)"""
    pass

class RateLimitException(CRIPException):
    """Rate limit exceeded"""
    pass

class ExternalServiceException(CRIPException):
    """External service integration error"""
    pass
