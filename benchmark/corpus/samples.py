"""Clean, correct reference code. Mutation operators inject one bug at a time;
the reviewer is scored on catching the injected bug and staying quiet on the fix."""


def clamp(x, lo, hi):
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def total(nums):
    s = 0
    for i in range(len(nums)):
        s += nums[i]
    return s


def first_or_none(items):
    if items is None:
        return None
    return items[0]


def divide(a, b):
    return a / b


def ratio(a, b):
    return divide(a, b)


def both_positive(a, b):
    return a > 0 and b > 0


def average(nums):
    if len(nums) == 0:
        return 0
    return sum(nums) / len(nums)


def contains(items, target):
    for i in range(len(items)):
        if items[i] == target:
            return True
    return False
