from datetime import datetime
import gviz_api
import os

TIMETABLE_TEMPLATE_PATH = "./templates/timetable.html"
OUTPUT_DIRECTORY = "./output"


def generate(data, date):
    page_template = ""
    params = {}
    date_string = date.strftime("%d-%m-%y")

    # Creating the data
    description = {
        "room": ("string", "Room Name"),
        "start": ("datetime", "Period Start"),
        "end": ("datetime", "Period End")
    }

    # Loading it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    # Create a JSON string.
    params["json"] = data_table.ToJSon(
        columns_order=("room", "start", "end"),
        order_by="room"
    )
    params["generated-date"] = datetime.now()
    params["for-date"] = date_string

    # Load Template file
    with open(TIMETABLE_TEMPLATE_PATH, 'r') as f:
        page_template = f.read()

    try:
        os.mkdir(OUTPUT_DIRECTORY)
    except OSError:
        pass

    # Put JSON string into the template.
    with open(os.path.join(OUTPUT_DIRECTORY, f"{date_string}.html"), 'w') as f:
        f.write(page_template % params)
