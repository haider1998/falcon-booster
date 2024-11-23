# custom_exceptions.py
import logging

class CustomException(Exception):
    """Base class for custom exceptions"""
    pass

class GitHubURLException(CustomException):
    """Exception raised for errors in the GitHub URL format"""
    def __init__(self, message="Invalid GitHub URL format"):
        self.message = message
        super().__init__(self.message)

class GitCommandException(CustomException):
    """Exception raised for errors in Git commands"""
    def __init__(self, message="Git command error"):
        self.message = message
        super().__init__(self.message)

class UnexpectedException(CustomException):
    """Exception raised for unexpected errors"""
    def __init__(self, message="An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)

def handle_exception(e):
    if isinstance(e, GitHubURLException):
        logging.error(f"GitHub URL Exception: {e.message}")
    elif isinstance(e, GitCommandException):
        logging.error(f"Git Command Exception: {e.message}")
    elif isinstance(e, UnexpectedException):
        logging.error(f"Unexpected Exception: {e.message}")
    else:
        logging.error(f"Unhandled Exception: {str(e)}")