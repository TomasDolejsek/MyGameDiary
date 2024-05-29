"""
Utility functions to work with session
"""


def store_in_session(request, param_key, param_value):
    """
    Store key-value pair in session
    """
    if request and param_key:
        request.session[param_key] = param_value
        return True
    return False


def get_from_session(request, param_key, pop=False):
    """
    Retrieve a value of given key from session, pop if requested
    """
    object_value = None
    if request and param_key:
        try:
            if pop:
                object_value = request.session.pop(param_key)
            else:
                object_value = request.session.get(param_key)
        except KeyError:
            print(f"Parameter {param_key} not found in session")
    return object_value
