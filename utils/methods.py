def cast_to_int_with_errors(value):
    try:
        
        int_value = int(value)
        return True

    except ValueError:
        return False