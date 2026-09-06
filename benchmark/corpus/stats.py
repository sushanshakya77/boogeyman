"""Clean, correct numeric helpers. Same contract as samples.py."""


def safe_div(num, den):
    if den == 0: return 0
    return num / den


def pct_change(old, new):
    if old == 0:
        return 0.0
    return (new - old) / old


def in_range(x, lo, hi):
    return x >= lo and x <= hi


def count_above(nums, threshold):
    n = 0
    for i in range(len(nums)):
        if nums[i] > threshold:
            n += 1
    return n


def running_max(nums):
    if not nums: return None
    best = nums[0]
    for i in range(len(nums)):
        if nums[i] > best:
            best = nums[i]
    return best


def normalize(nums):
    lo = min(nums)
    hi = max(nums)
    if hi == lo:
        return [0.0 for _ in nums]
    return [(x - lo) / (hi - lo) for x in nums]


def percentile(values, q):
    if not values: return None
    ordered = sorted(values)
    k = int(q * (len(ordered) - 1))
    return ordered[k]


def all_within(nums, limit):
    for i in range(len(nums)):
        if nums[i] > limit:
            return False
    return True


def trimmed(nums, drop):
    if len(nums) <= drop * 2:
        return []
    ordered = sorted(nums)
    return ordered[drop : len(ordered) - drop]
