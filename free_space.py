from datetime import datetime, timedelta
from itertools import filterfalse
from pytz import UTC, timezone, utc
import json

MIN_TIME_GAP = timedelta(minutes=30)


def main():
    data = {}
    with open("sample.json", "r") as file:
        data = json.loads(file.read())
    print(free_space(data))


def free_space(data, startDate):
    free_spaces = []
    startDate = UTC.localize(startDate.replace(hour=0, minute=0, second=0))
    day_start = datetime.fromisoformat(
        data[0]["StartDateTime"]).replace(hour=0, minute=0, second=0)

    for i in range(len(data)):
        start = datetime.fromisoformat(data[i]["StartDateTime"])

        if i != 0:
            previous_end = datetime.fromisoformat(data[i - 1]["EndDateTime"])

        if i == 0:
            free_spaces.append({
                "StartDateTime":  day_start.astimezone(),
                "EndDateTime": start.astimezone()
            })
        # If there is a gap between bookings and is at least the min time gap
        elif start != previous_end and (start - previous_end) >= MIN_TIME_GAP:
            free_spaces.append({
                "StartDateTime": previous_end.astimezone(),
                "EndDateTime": start.astimezone()
            })

    # Remove entries for previous days.
    # Caused by booking spanning multiple days where first day is before start day.
    # This can lead to incorrect reporting about availability due to limited data.
    return filterfalse(lambda x: x["StartDateTime"] <= startDate, free_spaces)


if __name__ == "__main__":
    main()
