import requests
import datetime
import json

# Logger settings
INFO_PREFIX = "info"
ERROR_PREFIX = "error"
WARNING_PREFIX = "warning"
LOG_FILE = ".log"
USE_WEBHOOK = True
WEBHOOK = "CHANGE ME"
WEBHOOK_NAME = "Das Auto Loginator"


def formatLog(loggerTag: str, logMessage) -> str:
    return f"[{loggerTag}][{datetime.datetime.now()}]: {logMessage}"


def log(prefix: str, logMessage: str) -> None:
    with open(LOG_FILE, "a") as f:
        msg = formatLog(prefix, logMessage)
        f.write(msg + "\n")
        print(msg)


def logDiscord(prefix: str, logMessage: str) -> bool:
    msg = f"```py\n{formatLog(prefix, logMessage)}\n```"
    MAX = 2000
    if len(msg) > MAX:
        msg = msg[0 : (MAX - 1)]

    values = {
        "username": WEBHOOK_NAME,
        "content": f"{msg}",
    }

    try:
        requests.post(
            WEBHOOK,
            data=json.dumps(values),
            headers={"Content-Type": "application/json"},
        )
    except:
        return False
    return True


def logInfo(logMessage: str) -> None:
    log(INFO_PREFIX, logMessage)


def logError(logMessage: str) -> None:
    log(ERROR_PREFIX, logMessage)
    if USE_WEBHOOK:
        if not logDiscord(ERROR_PREFIX, logMessage):
            logWarning("Failed to log to discord")


def logWarning(logMessage: str) -> None:
    log(WARNING_PREFIX, logMessage)
