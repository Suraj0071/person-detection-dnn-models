import time
import requests
import traceback
import cv2


def post_data(comp_name, store_name, enter_id, exit_id, first_time,last_time, duration, occupancy, elapsed_time, day) :

    try:
        api_post = 'https://apex21.doorcounts.com/ords/ws/v1/jamfast_data'

        headers = {
            "comp_name": comp_name,
            "store_name": store_name,
            "entering_id": str(enter_id),
            "exiting_id": str(exit_id),
            "first_time": first_time,
            "last_time": last_time,
            "durations": str(duration),
            "occupancy": str(occupancy),
            "zero_occupancy":str(elapsed_time),
            "day": day
        }

        response = requests.post(api_post, headers=headers)
        print(response, 'GOT THE RESPONSE')


    except Exception as ex:
        print("Exception in post_data: {}".format(ex))
        print(traceback.print_exc())

    return None

def post_image(frame,company_name, store_name,camera_id, zone, triggers,date_time):

    time.sleep(1)
    recipient = "http://apex21.doorcounts.com/ords/ws/photo.put"
    username = "httptest"
    password = "kjk67y"

    # Convert frame to jpg image format data
    encoded, buffer = cv2.imencode('.jpg', frame)

    # Convert data of jpg image to string
    payload = buffer.tostring()

    # Define header for POST request
    headers = {'Content-disposition': 'attachment; filename= {}.{}.{}.{}.{}.{}.jpg;'.format(company_name, store_name,
                                                                                            camera_id, zone, triggers,
                                                                                            date_time),'Content-type': 'image/jpeg'}

    # # HTTP POST request
    response = requests.post(recipient, data=payload, headers=headers, auth=(username, password))
    print(response)
    filename = '{}.{}.{}.{}.{}.{}.jpg;'.format(company_name, store_name,camera_id, zone, triggers,date_time)
    print(filename)

    return None
