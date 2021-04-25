
def clamp(lower_bound, upper_bound, x):
    assert lower_bound <= upper_bound, (lower_bound, upper_bound)
    return max(min(upper_bound, x), lower_bound)
