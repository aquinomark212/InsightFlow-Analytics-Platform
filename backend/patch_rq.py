# patch_rq.py
import multiprocessing
import sys

# Only apply this patch on Windows
if sys.platform == 'win32':
    original_get_context = multiprocessing.get_context
    
    def patched_get_context(method=None):
        if method == 'fork':
            # Windows doesn't support 'fork', use 'spawn' instead
            method = 'spawn'
        return original_get_context(method)
    
    multiprocessing.get_context = patched_get_context