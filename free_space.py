from datetime import date, datetime, timedelta
from itertools import filterfalse
from pytz import UTC
import json

MIN_TIME_GAP = timedelta(minutes=30)


def main():
    data = {}
    with open("sample.json", "r") as file:
        data = json.loads(file.read())
    print(free_space(data, datetime.now().date()))


def free_space(data, start_date: date):
    free_spaces = []

    # Covert  from date to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    start_datetime = UTC.localize(start_datetime)

    end_datetime = start_datetime + timedelta(days=1, microseconds=-1)

    # If no bookings the whole day is free
    if len(data) == 0:
        free_spaces.append({
            "StartDateTime": start_datetime.astimezone(),
            "EndDateTime": end_datetime.astimezone()
        })

        return free_spaces

    for i in range(len(data)):
        current_start = datetime.fromisoformat(data[i]["StartDateTime"])

        if i != 0:
            previous_end = datetime.fromisoformat(data[i - 1]["EndDateTime"])

        # If first and start of first booking as after start of the day
        if i == 0 and current_start > start_datetime:
            free_spaces.append({
                "StartDateTime":  start_datetime.astimezone(),
                "EndDateTime": current_start.astimezone()
            })
        elif i == 0:
            continue
        # If there is a gap between bookings and is at least the min time gap
        elif current_start != previous_end and (current_start - previous_end) >= MIN_TIME_GAP:
            free_spaces.append({
                "StartDateTime": previous_end.astimezone(),
                "EndDateTime": current_start.astimezone()
            })

    last_end = datetime.fromisoformat(data[-1]["EndDateTime"])
    # If end of last booking is before end of day and at least the min time gap
    if last_end < end_datetime and (end_datetime - last_end) >= MIN_TIME_GAP:
        free_spaces.append({
            "StartDateTime": last_end.astimezone(),
            "EndDateTime": end_datetime.astimezone()
        })

    # Remove entries for previous days.
    # Caused by booking spanning multiple days where first day is before start day.
    # This can lead to incorrect reporting about availability due to limited data.
    return filterfalse(lambda x: x["StartDateTime"] < start_datetime, free_spaces)


if __name__ == "__main__":
    main()
