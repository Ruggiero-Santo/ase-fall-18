
def sum (m, n):
    addend = (-1 if n < 0 else 1)
    for _ in range(abs(n)):
        m += addend
    return m

def divide (m, n):
    result = 0
    if n == 0: return "NaN"
    factor = (-1 if (n < 0) != (m < 0) else 1)

    n, m = abs(n), abs(m)

    while m-n <= 0:
        result += 1
        m -= n

    return factor * (result +1)
