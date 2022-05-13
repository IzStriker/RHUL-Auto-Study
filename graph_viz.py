from datetime import datetime
import gviz_api

page_template = """
<html>
  <script src="https://www.gstatic.com/charts/loader.js"></script>
  <script>
    google.charts.load('current', {packages:['timeline']});

    google.charts.setOnLoadCallback(drawTable);
    function drawTable() {
  
      var json_table = new google.visualization.Timeline(document.getElementById('table_div_json'));
      var json_data = new google.visualization.DataTable(%(json)s, 0.6);
      json_table.draw(json_data, {height: 700});
    }
  </script>
  <body>
    <H1>Table created using ToJSon</H1>
    <div id="table_div_json"></div>
  </body>
</html>
"""


def generate(data):
    # Creating the data
    description = {"room": ("string", "Room Name"),
                   "start": ("datetime", "Period Start"),
                   "end": ("datetime", "Period End")}

    # Loading it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    # Create a JSON string.
    json = data_table.ToJSon(columns_order=("room", "start", "end"),
                             order_by="room")

    # Put JSON string into the template.
    with open('index.html', 'w') as f:
        f.write(page_template % vars())
