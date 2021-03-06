# RHUL Auto Study

The website for the RHUL study rooms provides an awkward and difficult to use interface. Users are forced to click back and forth between multiple pages to find the desired availability. The filtering tools provided are too restrictive. The system would be easier to use if the times from all the study rooms were displayed on a single page for a given day. That's what this tool aims to do.

When run, the program generates a chart in a html file, showing the free spaces in each study room. If a study room is fully booked or unavailable, it doesn't appear in the chart at all. You can hover over free periods to display detailed information (e.g. How long the room is free for). Once you've made your decision, navigate to the corresponding room on the original website and book it.

## Install Requirements

To run the program you need any version of Python 3.

```bash
pip install -r requirements.txt
```

You only need to do that the first time you run the program.

## Using the tool

```bash
python app.py -u <username>@live.rhul.ac.uk -p <password> [ -s <date> ]
```

The results are placed in the `./output` directory named with the date for which they show the availability.

The `-s` flag allows you to provide the date you want to check the availability for. If you choose this option, you need the give the date in ISO format. `YYYY-MM-DD` e.g. `2020-07-07`.
It's a good idea to surround all the values specified for flag in quotes in case they contain special characters.

The generated document contains the free periods each study room is empty.

<img src="./images/table.png">

If you hover over a slot it tells you the exact times it's free.

<img src="./images/tooltip.png">

At the top of the page it tells you how up to date the document is.

<img src="./images/timestamp.png">

## Security

This program doesn't store or log any sensitive data in any way. The username and password you provide are used to login into the study room system and get your access token. Then, your access token (which is only valid for 60 mins) is used to make independent requests to the systems API. Once the program exits, all your sensitive information is cleared. It is open source as well.

## Compatibility

Tested and working on:

- Windows 10
- Arch Linux

Mileage may very on different operating systems.
