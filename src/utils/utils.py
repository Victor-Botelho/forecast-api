import psutil


def convert_bytes(num):
    """This function will convert bytes to MB.... GB... etc"""
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:.2f}{x}"
        num /= 1024.0


def ram_stats():
    """Returns a tuple (used, total, percentage used)"""
    mem = psutil.virtual_memory()
    return convert_bytes(mem.used), convert_bytes(mem.total) , mem.percent
