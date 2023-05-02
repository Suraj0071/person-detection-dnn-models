import time
from datetime import datetime, timedelta
import traceback
def get_time():
    try:
        current_time = time.strftime("%Y%m%d%H%M%S")

        # # test to send previous date and rime
        # now = datetime.now()
        # previous_datetime = now + timedelta(days=1)
        # current_time = previous_datetime.strftime("%Y%m%d%H%M%S")
        # print(current_time_dict,"GET EDIT TIME")
        # print(type(previous_datetime))
        # print(current_time)

    except:
        print(traceback.print_exc())
    return current_time


def get_day():
    try:
        now = datetime.now()
        day = now.strftime("%A")

        # previous_datetime = now + timedelta(days=1)
        # print(previous_datetime.strftime("%A"))
        # day = previous_datetime.strftime("%A")
    except:
        print(traceback.print_exc())
    return day
