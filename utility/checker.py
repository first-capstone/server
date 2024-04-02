import re

def is_valid_uuid_format(data: str) -> bool:
    UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$")
    
    return bool(re.match(UUID_PATTERN, data))