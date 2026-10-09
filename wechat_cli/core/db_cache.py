"""解密数据库缓存 — mtime 检测变化，跨会话复用。"""

import hashlib
import json
import os
import tempfile
import time
from contextlib import contextmanager

from .crypto import full_decrypt, decrypt_wal
from .key_utils import get_key_info


@contextmanager
def _file_lock(lock_path, timeout=30.0, stale_after=120.0):
    """A tiny cross-process lock based on atomic O_EXCL file creation.

    Lock files live only in the CLI temp cache. Stale locks left by killed
    processes are reclaimed after ``stale_after`` seconds.
    """
    deadline = time.monotonic() + timeout
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    fd = None
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            payload = f"pid={os.getpid()} time={time.time()}\n".encode("ascii", "replace")
            os.write(fd, payload)
            os.close(fd)
            fd = None
            break
        except FileExistsError:
            try:
                age = time.time() - os.path.getmtime(lock_path)
                if age > stale_after:
                    os.unlink(lock_path)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"等待缓存锁超时: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass


class DBCache:
    CACHE_DIR = os.path.join(tempfile.gettempdir(), "wechat_cli_cache")
    MTIME_FILE = os.path.join(CACHE_DIR, "_mtimes.json")
    META_LOCK = os.path.join(CACHE_DIR, "_mtimes.lock")

    def __init__(self, all_keys, db_dir):
        self._all_keys = all_keys
        self._db_dir = db_dir
        self._cache = {}  # rel_key -> (db_mtime, wal_mtime, tmp_path)
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        self._load_persistent_cache()

    def _cache_path(self, rel_key):
        h = hashlib.md5(rel_key.encode()).hexdigest()[:12]
        return os.path.join(self.CACHE_DIR, f"{h}.db")

    def _cache_lock_path(self, rel_key):
        h = hashlib.md5(rel_key.encode()).hexdigest()[:12]
        return os.path.join(self.CACHE_DIR, f"{h}.lock")

    def _read_persistent_cache(self):
        if not os.path.exists(self.MTIME_FILE):
            return {}
        try:
            with open(self.MTIME_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError, TypeError):
            return {}

    def _entry_is_current(self, rel_key, info):
        try:
            tmp_path = info["path"]
            if not os.path.exists(tmp_path):
                return None
            rel_path = rel_key.replace("\\", os.sep).replace("/", os.sep)
            db_path = os.path.join(self._db_dir, rel_path)
            wal_path = db_path + "-wal"
            db_mtime = os.path.getmtime(db_path)
            wal_mtime = os.path.getmtime(wal_path) if os.path.exists(wal_path) else 0
            if db_mtime == info["db_mt"] and wal_mtime == info["wal_mt"]:
                return db_mtime, wal_mtime, tmp_path
        except (KeyError, OSError, TypeError, ValueError):
            pass
        return None

    def _load_persistent_cache(self):
        for rel_key, info in self._read_persistent_cache().items():
            current = self._entry_is_current(rel_key, info)
            if current:
                self._cache[rel_key] = current

    def _reload_entry_from_disk(self, rel_key):
        info = self._read_persistent_cache().get(rel_key)
        if not info:
            return None
        current = self._entry_is_current(rel_key, info)
        if current:
            self._cache[rel_key] = current
            return current
        return None

    def _save_persistent_cache(self):
        # Different DBs may refresh concurrently. Merge with the latest file
        # while holding one metadata lock so one process cannot erase another's
        # freshly written cache entry.
        try:
            with _file_lock(self.META_LOCK):
                data = self._read_persistent_cache()
                for rel_key, (db_mt, wal_mt, path) in self._cache.items():
                    data[rel_key] = {"db_mt": db_mt, "wal_mt": wal_mt, "path": path}

                tmp_meta = f"{self.MTIME_FILE}.{os.getpid()}.tmp"
                try:
                    with open(tmp_meta, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(tmp_meta, self.MTIME_FILE)
                finally:
                    try:
                        os.unlink(tmp_meta)
                    except FileNotFoundError:
                        pass
        except (OSError, TimeoutError):
            # Cache metadata is an optimization; a failure must not break reads.
            pass

    def get(self, rel_key):
        key_info = get_key_info(self._all_keys, rel_key)
        if not key_info:
            return None
        rel_path = rel_key.replace("\\", os.sep).replace("/", os.sep)
        db_path = os.path.join(self._db_dir, rel_path)
        wal_path = db_path + "-wal"
        if not os.path.exists(db_path):
            return None

        try:
            db_mtime = os.path.getmtime(db_path)
            wal_mtime = os.path.getmtime(wal_path) if os.path.exists(wal_path) else 0
        except OSError:
            return None

        cached = self._cache.get(rel_key)
        if cached:
            c_db_mt, c_wal_mt, c_path = cached
            if c_db_mt == db_mtime and c_wal_mt == wal_mtime and os.path.exists(c_path):
                return c_path

        # Only one process may refresh a specific decrypted DB at a time.
        # After acquiring the lock, re-check metadata because another process
        # may have completed the refresh while we were waiting.
        lock_path = self._cache_lock_path(rel_key)
        try:
            with _file_lock(lock_path):
                refreshed = self._reload_entry_from_disk(rel_key)
                if refreshed:
                    return refreshed[2]

                # Re-read mtimes after waiting for the lock; WeChat may have
                # advanced its WAL while another process was refreshing.
                try:
                    db_mtime = os.path.getmtime(db_path)
                    wal_mtime = os.path.getmtime(wal_path) if os.path.exists(wal_path) else 0
                except OSError:
                    return None

                final_path = self._cache_path(rel_key)
                work_path = f"{final_path}.{os.getpid()}.{time.time_ns()}.tmp"
                enc_key = bytes.fromhex(key_info["enc_key"])
                try:
                    full_decrypt(db_path, work_path, enc_key)
                    if os.path.exists(wal_path):
                        decrypt_wal(wal_path, work_path, enc_key)
                    os.replace(work_path, final_path)
                finally:
                    try:
                        os.unlink(work_path)
                    except FileNotFoundError:
                        pass

                self._cache[rel_key] = (db_mtime, wal_mtime, final_path)
                # Persist immediately while the refresh is known-good. This
                # avoids losing metadata when the CLI process is later killed.
                self._save_persistent_cache()
                return final_path
        except TimeoutError:
            # If a peer is wedged, prefer a valid stale/current cache entry over
            # hanging the whole CLI forever. Re-check disk metadata once.
            refreshed = self._reload_entry_from_disk(rel_key)
            return refreshed[2] if refreshed else None

    def cleanup(self):
        self._save_persistent_cache()
