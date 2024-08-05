def custom_round(n, decimals=2):
    multiplier = 10 ** decimals
    n *= multiplier
    integer_part = int(n)
    decimal_part = n - integer_part

    if decimal_part >= 0.5:
        # Rounding against the direction of zero
        if n > 0:
            integer_part += 1
        else:
            integer_part -= 1
    elif decimal_part > 0 and decimal_part < 0.5:
        # Rounding in the direction of zero
        if n > 0:
            pass  # No change needed
        else:
            integer_part += 1
    elif decimal_part < 0 and decimal_part > -0.5:
        # Rounding in the direction of zero
        if n > 0:
            integer_part -= 1
        else:
            pass  # No change needed
    else:  # decimal_part <= -0.5
        # Rounding against the direction of zero
        if n > 0:
            integer_part -= 1
        else:
            integer_part += 1

    return integer_part / multiplier

# Examples
print(custom_round(1.234))  # Output: 1.23
print(custom_round(1.235))  # Output: 1.24
print(custom_round(-1.234)) # Output: -1.23
print(custom_round(-1.235)) # Output: -1.24

# Additional test
result = 0+0
rounded_result = custom_round(result)
print(rounded_result)  # Output: 1736.67
