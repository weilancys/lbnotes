from datetime import datetime

FLASH_MESSAGE_TYPES = { "info": "info", "error": "error" }  

MYSQL_DATETIME_FORMAT_STR = "%Y-%m-%d %H:%M:%S"

def parse_db_time(time_str):
    """ parse datetime object from string based on format """
    if time_str is None:
        return None
    global MYSQL_DATETIME_FORMAT_STR
    return datetime.strptime(time_str, MYSQL_DATETIME_FORMAT_STR)


def convert_to_time_str(dt):
    """ convert datetime object to string based on format """
    global MYSQL_DATETIME_FORMAT_STR
    return dt.strftime(MYSQL_DATETIME_FORMAT_STR)

