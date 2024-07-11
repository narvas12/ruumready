from rest_framework.views import exception_handler
import json
import logging

def custom_exception_handler(exec, context):
    
    handlers = {
        "ValidationError": _handle_generic_error,
        "Http404": _handle_generic_error,
        "NotAuthenticated": _handle_authentication_error,
        "PermissionDenied": _handle_generic_error,
        "ValueError": _handle_generic_error,
        "NotFound": _handle_generic_error,
        "InvalidToken": _handle_invalid_token_error,
    }
    
    response = exception_handler(exec, context)
    
    if response is not None:
        if 'LoginUserView' in str(context['view']) and exec.status_code == 401:
            response.status_code = 401
            response.data = {"islogged_in": False}
            
            response.data['status_code'] = int(response.status_code)
    
    exception_class = exec.__class__.__name__
    
    logger = logging.getLogger('django')  # Or 'your_app' for custom logger
    logger.info(str(exec), str(context))
    
    if exception_class in handlers:
        return handlers[exception_class](exec, context, response)
    return response

def _handle_authentication_error(exec, context, response):
    response.data = {
                        "detail": "Please login to proceed",  
                        # "status_code": response.status_code
                     }
    return response

def _handle_invalid_token_error(exec, context, response):
    response.data = {
                        "detail": "Invalid Token", 
                        #  "status_code": response.status_code
                     }
    return response

def _handle_generic_error(exec, context, response):
    return response