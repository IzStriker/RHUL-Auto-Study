from datetime import datetime, timedelta
from itertools import filterfalse
from pytz import UTC
import json

MIN_TIME_GAP = timedelta(hours=1)


def main():
    data = {}
    with open("sample.json", "r") as file:
        data = json.loads(file.read())
    print(free_space(data))


def free_space(data, startDate):
    free_spaces = []
    startDate = UTC.localize(startDate.replace(hour=0, minute=0, second=0))
    print(startDate)
    day_start = datetime.fromisoformat(
        data[0]["StartDateTime"]).replace(hour=0, minute=0, second=0)

    for i in range(len(data)):
        start = datetime.fromisoformat(data[i]["StartDateTime"])

        if i != 0:
            previous_end = datetime.fromisoformat(data[i - 1]["EndDateTime"])

        if i == 0:
            free_spaces.append({
                "StartDateTime": day_start,
                "EndDateTime": start
            })
        # If there is a gap between booking and is at least the min time gap
        elif start != previous_end and (start - previous_end) >= MIN_TIME_GAP:
            # If the previous and current booking aren't on the same day
            if previous_end.replace(hour=0, minute=0, second=0) != start.replace(hour=0, minute=0, second=0):
                # From end of previous end to end of that day
                free_spaces.append({
                    "StartDateTime": previous_end,
                    "EndDateTime": previous_end.replace(hour=23, minute=59, second=59)
                })
                # Start start of current day to start of current event
                free_spaces.append({
                    "StartDateTime": start.replace(hour=0, minute=0, second=0),
                    "EndDateTime": start
                })
            else:
                free_spaces.append({
                    "StartDateTime": previous_end,
                    "EndDateTime": start
                })

    # Remove entries for previous days.
    # Caused by booking spanning multiple days where first day is before start day.
    # This can lead to incorrect reporting about availability due to limited data.
    return filterfalse(lambda x: x["StartDateTime"] <= startDate, free_spaces)


if __name__ == "__main__":
    main()
