
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


def lazy_accumulate(f, acc, seq):
    for item in seq:
        acc = f(item, acc)
        yield acc


def drop_until(pred, seq):
    for item in seq:
        if pred(item):
            yield item

    yield from seq


def take_until(pred, seq):
    for item in seq:
        if pred(item):
            return
        yield item


def lazy_iterate(func, exit_condition, initial_value, *, include_last):
    x = initial_value

    while not exit_condition(x):
        yield x
        x = func(x)

    if include_last:
        yield x


def lazy_chain(seq):
    for item in seq:
        yield from item
