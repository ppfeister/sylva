import platformdirs

__cache_dir = platformdirs.user_cache_dir
__cache_db = f"{__cache_dir}/cache.sqlite"

class Cache:
    def __init__(self):
        self.cache_db_path = __cache_db