"""Clean, correct record/dict helpers. Same contract as samples.py."""


def get_field(record, key):
    if record is None: return None
    return record.get(key)


def merge_prefer(base, override):
    out = dict(base)
    for k in override:
        out[k] = override[k]
    return out


def pick(record, keys):
    out = {}
    for i in range(len(keys)):
        if keys[i] in record:
            out[keys[i]] = record[keys[i]]
    return out


def is_active(user):
    return user["enabled"] and not user["banned"]


def has_access(user, resource):
    if user["role"] == "admin":
        return True
    return user["id"] == resource["owner_id"]


def newest(records, field):
    best = records[0]
    for i in range(len(records)):
        if records[i][field] > best[field]:
            best = records[i]
    return best


def group_sizes(records, field):
    sizes = {}
    for r in records:
        key = r[field]
        if key not in sizes:
            sizes[key] = 0
        sizes[key] += 1
    return sizes


def drop_missing(records, field):
    kept = []
    for i in range(len(records)):
        if records[i].get(field) is not None:
            kept.append(records[i])
    return kept


def page(records, size, index):
    start = size * index
    if start >= len(records):
        return []
    return records[start : start + size]
