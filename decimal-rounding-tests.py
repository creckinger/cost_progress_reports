import decimal

def round_half_up(n, decimals=2):
    # Set the precision high enough to handle the multiplication accurately
    decimal.getcontext().prec = 10
    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    
    # Perform the multiplication using Decimal
    n = decimal.Decimal(str(n))
    factor = decimal.Decimal(10) ** decimals
    shifted = n * factor
    
    # Round the shifted value
    rounded_value = shifted.to_integral_value()
    return float(rounded_value / factor)



x = 22.50*3.01
print(round_half_up(x, decimals=2))