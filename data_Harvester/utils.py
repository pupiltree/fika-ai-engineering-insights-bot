# data_harvester/utils.py
import os
import time

def is_file_stale(path, max_age_minutes=15):
    """Returns True if the file is older than `max_age_minutes`."""
    if not os.path.exists(path):
        return True
    modified_time = os.path.getmtime(path)
    age_minutes = (time.time() - modified_time) / 60
    return age_minutes > max_age_minutes
