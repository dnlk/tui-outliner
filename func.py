
def iterate(func, exit_condition, initial_value, *, include_first, include_last):
    results = []
    x = initial_value

    if include_first:
        results.append(x)

    while not exit_condition(x):
        next_x = func(x)
        assert next_x != x, 'iterated values must be changing'
        x = next_x
        results.append(x)

    if not include_last:
        results.pop()

    return results
