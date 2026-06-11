import jdatetime
from datetime import datetime

def jalali_to_gregorian(date_str: str, time_str: str) -> datetime:
    # format: 1405-03-22 + 15:00
    j_date = jdatetime.datetime.strptime(
        f"{date_str} {time_str}",
        "%Y-%m-%d %H:%M"
    )

    return j_date.togregorian()
