"""
定义装饰器工具
"""

import time 
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        cost = time.perf_counter() - start_time
        print(f"该函数{func.__name__}消耗时间是:{cost:.2f}s")

        return result
    
    return wrapper
