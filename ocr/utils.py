def collect_texts(obj, out):
    if obj is None:
        return
    if isinstance(obj, str):
        s = obj.strip()
        if s:
            out.append(s)
        return
    if isinstance(obj, dict):
        for v in obj.values():
            collect_texts(v, out)
        return
    if isinstance(obj, (list, tuple)):
        for v in obj:
            collect_texts(v, out)
        return

def unique_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def to_debug_string(obj, max_chars=200000):
    s = repr(obj)
    if len(s) > max_chars:
        s = s[:max_chars] + "\n...[TRUNCATED]..."
    return s
