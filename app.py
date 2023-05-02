from datetime import datetime, timedelta
import edgeiq
import threading
import os
import re, traceback
import time
import logging
from utils.log import start_log
from utils.get_time import get_time, get_day
from utils.api import post_data, post_image

current_id_dict = {}
first_time_dict = {}
current_time_dict = {}
last_time_dict = {}
first_zone_dict = {}
current_zone_dict = {}
last_zone_dict = {}
disappeared_id = set()
entering_dict = {}
previous_current = []
object_set = set()
door_waiting_map = {}
existing_dict = {}

first_img_dict = {}
current_img_dict = {}
def main():

    global current_id_dict
    global first_time_dict
    global current_time_dict
    global last_time_dict
    global first_zone_dict
    global current_zone_dict
    global last_zone_dict
    global disappeared_id
    global entering_dict
    global previous_current
    global door_waiting_map
    global existing_dict
    test = []
    comp_name = 'Jamfast'
    store_name = 'Keizer Store'
    timer = False

    start_log(comp_name, store_name)
    logging.info("------------------AI APP Started---------------------")
    logging.info("Company Name: %s", comp_name)
    logging.info("Store Name: %s", store_name)


    # obj_detect = edgeiq.ObjectDetection("dougrien/jamba-01-person-detect-aug-mob-e100-b8-x300-20230312")
    obj_detect = edgeiq.ObjectDetection("dougrien/jamba-01-person-detect-mob-e100-b8-x300-20230129")
    obj_detect.load(engine=edgeiq.Engine.DNN)

    kalman_tracker = edgeiq.KalmanTracker(deregister_frames=50, max_distance=50)

    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Model:\n{}\n".format(obj_detect.model_id))
    print("Labels:\n{}\n".format(obj_detect.labels))

    fps = edgeiq.FPS()

    zones = edgeiq.ZoneList("zone_config.json")
    bottom = zones.get_zone('Bottom Area')
    door = zones.get_zone('door')
    employee = zones.get_zone('employee area')
    bottom_box = edgeiq.create_bounding_box_from_zone(bottom)
    door_box = edgeiq.create_bounding_box_from_zone(door)
    employee_box = edgeiq.create_bounding_box_from_zone(employee)


    try:
        # with edgeiq.FileVideoStream("jamba-keizer-20230127-1.mp4") as video_stream, \
        with edgeiq.IPVideoStream('http://doorcounts:9W1oc0V5ptTq@50.246.239.150:5001/axis-cgi/mjpg/video.cgi') as video_stream,\
                edgeiq.Streamer() as streamer:
            # Allow Webcam to warm up
            time.sleep(2.0)
            fps.start()

            while True:

                text = ' '
                image = video_stream.read()

                # Resize image to 640*480 resolution
                image = edgeiq.resize(image, width=640, height=480, keep_scale=False)

                # Calculating object detection results
                object_results = obj_detect.detect_objects(image, confidence_level=.65)

                # Results for those persons who are inside region of interest
                Waiting_area_results = zones.get_results_for_zone(object_results, "Waiting area")

                # Passing waiting area results to tracker
                objects = kalman_tracker.update(Waiting_area_results.predictions)

                try:
                    regex = r"\((\d+), ObjectDetectionPrediction"
                    matches = re.findall(regex, str(objects.items()))
                    current_list = [int(x) for x in matches]

                    # for zones
                    for (object_id, trackable_prediction) in objects.items():
                        Waiting_area_results.predictions.clear()

                        if timer is True:
                            end_time = time.time()
                            # print(start_time, end_time)
                            elapsed_time = end_time - start_time
                            elapsed_time = round(elapsed_time)
                            print('TIMER STOOOOP')
                            timer = False

                        # for door area
                        if trackable_prediction.box.compute_overlap(door_box) >= 0.4:
                            # Updating current time and zone for id
                            current_zone_dict[object_id] = 'door'
                            current_time_dict[object_id] = get_time()

                            # test_time=time.strftime('%H.%M.%S')
                            # print(test_time)
                            # print(type(test_time), 'type time')
                            current_id_dict[object_id] = object_id
                            # existing_dict[object_id] = time.strftime('%H.%M.%S')
                            # print(existing_dict,'existing_dict')

                            # Checking if new id appears
                            if object_id not in first_time_dict:
                                first_time_dict[object_id] = get_time()
                                first_zone_dict[object_id] = 'door'
                                # print(first_zone_dict,'entering')
                                entering_dict[object_id] = get_time()  # Entering dictionary
                                print(entering_dict, 'entering')
                                logging.debug("Current entering List {}".format(entering_dict))
                                # test_time = get_time()
                                # post_image(image, comp_name, store_name, 1, 'A', 'A.0', test_time)

                                # store the entering image
                                first_img_dict[object_id] = image

                                # print(first_time_dict, 'first_time')
                                # print(first_zone_dict, 'first_zone')
                        # for bottom area
                        elif trackable_prediction.box.compute_overlap(bottom_box) >= 0.2:
                            # Updating current time and zone for id
                            current_zone_dict[object_id] = 'Bottom_Area'
                            current_time_dict[object_id] = get_time()
                            current_id_dict[object_id] = object_id

                            # Checking if new id appears
                            if object_id not in first_time_dict:
                                first_time_dict[object_id] = get_time()
                                first_zone_dict[object_id] = 'Bottom_Area'
                                # print(first_time_dict, 'first_time')
                                # print(first_zone_dict, 'first_zone')

                        # for employee area
                        elif employee_box.compute_overlap(trackable_prediction.box) == 0.8:
                            # Updating current time and zone for id
                            current_zone_dict[object_id] = 'employee area'
                            current_time_dict[object_id] = get_time()
                            current_id_dict[object_id] = object_id

                            # Checking if new id appears
                            if object_id not in first_time_dict:
                                first_time_dict[object_id] = get_time()
                                first_zone_dict[object_id] = 'employee area'


                        # For first enterance of new id
                        elif object_id not in first_time_dict.keys():
                            first_time_dict[object_id] = get_time()
                            first_zone_dict[object_id] = 'Waiting_Area'
                            # print(first_time_dict, 'first_time')
                            # print(first_zone_dict, 'first_zone')

                        else:
                            # Updating current time and zone for id
                            current_zone_dict[object_id] = 'Waiting_Area'
                            current_time_dict[object_id] = get_time()
                            current_id_dict[object_id] = object_id

                            current_img_dict[object_id] = image
                            # print(current_list,'current_list')
                            # print(previous_current, 'previous')
                            # print(current_zone_dict,'curr_zone')
                        # Assigning new label to trackable prediction
                        new_label = 'Person {} '.format(object_id)
                        trackable_prediction.label = new_label
                        # Append new prediction into zone_results

                        # check whether person enter is employee or not
                        if employee_box.compute_overlap(trackable_prediction.box) == 0.5 and object_id in entering_dict:
                            if first_zone_dict[object_id] == 'door':
                                del entering_dict[object_id]
                                del first_img_dict[object_id]
                                print(f'REMOVE EMPLOYEE - {object_id} FROM ENTERING LIST')

                        try:
                            Waiting_area_results.predictions.append(trackable_prediction.prediction)
                        except Exception as ex:
                            Waiting_area_results.predictions.append(trackable_prediction)
                        # Markup image with zone results which is inside region of interst
                        image = edgeiq.markup_image(image, Waiting_area_results.predictions,
                                                    colors=((200, 0, 0), (0, 0, 0), (100, 0, 0)))

                    if len(objects.items()) == 0:
                        for key in list(current_time_dict.keys()):
                            if key not in current_id_dict.keys():
                                last_time_dict[key] = current_time_dict[key]
                                if current_zone_dict[key] == 'door':
                                    if first_zone_dict[key] != 'employee area':
                                        existing_dict[key] = current_time_dict[key]
                                        print(existing_dict, 'exiting')
                                        logging.debug("Current Exiting List {}".format(existing_dict))
                                    # print(last_time_dict, 'last time')

                        for key in current_zone_dict.keys():
                            if key not in current_id_dict.keys():
                                last_zone_dict[key] = current_zone_dict[key]
                                # print(last_zone_dict, 'last zone')
                        current_id_dict.clear()

                        # Calculating time

                        # for (i, j) in zip(list(entering_dict), list(existing_dict)):
                        #
                        #     print(i, j, 'chexck')
                        # print(len(entering_dict), 'LENGHT OF ENTRY LIST OUTSIDE')

                        for i in list(entering_dict):
                            for j in list(existing_dict):
                                # print(i, j, 'chexck')
                                if i in entering_dict and j in existing_dict:
                                    index_i = list(entering_dict).index(i)
                                    index_j = list(existing_dict).index(j)
                                    # print(index_j, 'OOO', index_i)
                                    # print(len(entering_dict), 'LENGHT OF ENTRY LIST')

                                    if index_i == index_j:
                                        # same id duration value
                                        if j in entering_dict:
                                            first_time = datetime.strptime(entering_dict[j], "%Y%m%d%H%M%S")
                                            last_time = datetime.strptime(existing_dict[j], "%Y%m%d%H%M%S")
                                            overall_time = last_time - first_time
                                            # print(first_time, 'first_time')
                                            # print(last_time, 'first_time')
                                            overall_value = round(overall_time.total_seconds())
                                            print(overall_value, 'SAME ID TIME', overall_time)
                                            print("Elapsed time: {:} seconds".format(elapsed_time))
                                            day = get_day()

                                            # using thread send data to API
                                            thread_to_send_data = threading.Thread(target=post_data, args=(
                                            comp_name, store_name, j, j, first_time_dict[j], last_time_dict[j], overall_value,
                                            len(entering_dict),elapsed_time, day))
                                            thread_to_send_data.start()

                                            logging.debug("Sending data of comp_name-{} store_name-{} enter id-{} exit id-{} enter time-{} exit time-{}".
                                                          format(comp_name, store_name, j, j, first_time_dict[j], last_time_dict[j]))

                                            # get entering frame of that id
                                            enter_frame = first_img_dict[j]

                                            # thread to send entering image
                                            thread_to_send_enter_photo = threading.Thread(target=post_image, args=(enter_frame, comp_name, store_name, 1, 'C', 'X.0', first_time_dict[j]))
                                            thread_to_send_enter_photo.start()

                                            # thread to send exiting image
                                            exit_frame = current_img_dict[j]
                                            thread_to_send_exit_photo = threading.Thread(target=post_image, args=(
                                            exit_frame, comp_name, store_name, 1, 'A', 'A.0', last_time_dict[j]))
                                            thread_to_send_exit_photo.start()

                                            # send elapsed_time one time only if entering person is multiple
                                            elapsed_time = 0

                                            del current_time_dict[j]
                                            del entering_dict[j]
                                            del existing_dict[j]
                                            del first_img_dict[j]
                                            del current_img_dict[j]

                                        elif j >= i:

                                            first_time = datetime.strptime(entering_dict[i], "%Y%m%d%H%M%S")
                                            last_time = datetime.strptime(existing_dict[j], "%Y%m%d%H%M%S")
                                            overall_time = last_time - first_time
                                            # print(type(first_time), 'first_time')
                                            # print(last_time, 'first_time')
                                            overall_value = round(overall_time.total_seconds())

                                            print(overall_value, 'time', overall_time)
                                            print("Elapsed time: {:} seconds".format(elapsed_time))
                                            day = get_day()

                                            # using thread send data to API
                                            thread_to_send_data = threading.Thread(target=post_data, args=(comp_name, store_name, i,
                                            j, first_time_dict[i], last_time_dict[j], overall_value, len(entering_dict), elapsed_time, day))
                                            thread_to_send_data.start()

                                            logging.debug(
                                                "Sending data of comp_name-{} store_name-{} enter id-{} exit id-{} enter time{} exit time{}".
                                                format(comp_name, store_name, i, j, first_time_dict[i],
                                                       last_time_dict[j]))

                                            # get eneterin frame of that id
                                            enter_frame = first_img_dict[i]

                                            # thread to send entering image
                                            thread_to_send_photo = threading.Thread(target=post_image, args=(
                                            enter_frame, comp_name, store_name, 1, 'C', 'X.0', first_time_dict[i]))
                                            thread_to_send_photo.start()

                                            # thread to send exiting image
                                            exit_frame = current_img_dict[j]
                                            thread_to_send_exit_photo = threading.Thread(target=post_image, args=(
                                                exit_frame, comp_name, store_name, 1, 'A', 'A.0', last_time_dict[j]))
                                            thread_to_send_exit_photo.start()

                                            # send elapsed_time one time only if entering person is multiple
                                            elapsed_time = 0

                                            del entering_dict[i]
                                            del existing_dict[j]

                                            del current_time_dict[i]
                                            del current_time_dict[j]

                                            del first_img_dict[i]
                                            del current_img_dict[j]
                                            print(entering_dict, 'entering_dict after del')
                                            print(existing_dict, 'existing_dict after dellllll')

                                        elif i > j:
                                            del current_time_dict[j]
                                            del entering_dict[i]
                                            del existing_dict[j]
                                            del first_img_dict[i]
                                            del current_img_dict[j]

                        if len(entering_dict) == 0 and len(existing_dict) != 0:
                            existing_dict.clear()
                            current_time_dict.clear()
                            print('CLEAR EXIT LIST ')
                        if len(entering_dict) == 0 and len(existing_dict) == 0 and timer is False:
                            start_time = time.time()
                            timer = True
                            print('TIMER START')

                except:
                    print(traceback.format_exc())

                # Markup zone of interest
                image = zones.markup_image_with_zones(image, fill_zones=False, color=(255, 0, 0))

                streamer.send_data(image, text)

                fps.update()

                if streamer.check_exit():
                    break

    finally:
        fps.stop()

        logging.info("------------------AI APP STOP--------------------")
        logging.info("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        logging.info("approx. FPS: {:.2f}".format(fps.compute_fps()))
        logging.info("Program Ending")

        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))
        print("Program Ending")


if __name__ == "__main__":
    main()
