class ValidationError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

def format_error(message, error_code):
    return {
        "status": "error",
        "message": message,
        "error_code": error_code
    }