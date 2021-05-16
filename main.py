import math
import cv2
import numpy as np
from pynput.mouse import Button
from hand_tracker import hand_tracker
from mouse_handler import mouse_listener, mouse_controller
from volume_controler import win_audio_controller


def main():
    cam_width, cam_height = 648, 480

    cap = cv2.VideoCapture(0)
    cap.set(3, cam_width), cap.set(4, cam_height)
    h_tracker = hand_tracker(debug_draw=True)
    listener = mouse_listener()
    volume_controller = win_audio_controller(listener.process_name)
    height_offset = 70
    width_offset = 0
    mouse_sensitivity = 3.5
    pressed_state = False

    while True:
        ret, frame = cap.read()

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        center_x, center_y = width//2-width_offset, height//2-height_offset

        hands = h_tracker.find_hands(rgb_image)
        if listener.pressed and listener.button == Button.left:
            volume_controller.process_name = listener.process_name
        if hands:
            # Initial mode is none, if all target fingers far from base of hand, it stays that way
            # Volume control (thumb and index far from base of hand) - fingertips further for more volume, closer for less
            # don't forget to click on the process you want to control
            # Mouse control (thumb close to base of palm, index and middle up) - if the line between fingertips and base of palm
            # above thresh - register click for LMB for index finger bent, RMB for middle finger and index apart,
            # double click by middle and index far apart, scroll by raising ring finger and moving up or down
            hand_data = h_tracker.get_landmark_data(rgb_image, hands)
            frame = h_tracker.draw_debug_landmarks(frame, hands)
            hand_1 = hand_data.get(0, None)

            if hand_1:
                thumb_tip = hand_1.get(4, None)
                index_finger_tip = hand_1.get(8, None)
                index_finger_cmc = hand_1.get(5, None)
                middle_finger_tip = hand_1.get(12, None)
                middle_finger_cmc = hand_1.get(9, None)
                wrist = hand_1.get(0, None)

                if index_finger_tip and middle_finger_tip and wrist:
                    thumb_tip_cx, thumb_tip_cy = thumb_tip[3], thumb_tip[4]
                    index_finger_tip_cx, index_finger_tip_cy = index_finger_tip[3], index_finger_tip[4]
                    index_finger_cmc_cx, index_finger_cmc_cy = index_finger_cmc[3], index_finger_cmc[4]
                    middle_finger_tip_cx, middle_finger_tip_cy = middle_finger_tip[3], middle_finger_tip[4]
                    middle_finger_cmc_cx, middle_finger_cmc_cy = middle_finger_cmc[3], middle_finger_cmc[4]

                    mode_line_index = math.hypot(index_finger_tip_cx-index_finger_cmc_cx, index_finger_tip_cy-index_finger_cmc_cy)
                    mode_line_middle = math.hypot(middle_finger_tip_cx-middle_finger_cmc_cx, middle_finger_tip_cy-middle_finger_cmc_cy)
                    mode_line_thumb = math.hypot(middle_finger_cmc_cx-thumb_tip_cx, middle_finger_cmc_cy-thumb_tip_cy)

                    # print(f"modelines - index: {mode_line_index}, middle: {mode_line_middle}, thumb: {mode_line_thumb}")

                    if mode_line_thumb >= 100 and mode_line_index > 70:

                        volume_line_center_x, volume_line_center_y = (thumb_tip_cx+index_finger_tip_cx)//2, (thumb_tip_cy+index_finger_tip_cy)//2
                        volume_line_len = math.hypot(index_finger_tip_cx-thumb_tip_cx, index_finger_tip_cy-thumb_tip_cy)

                        cv2.line(frame,
                                (thumb_tip_cx, thumb_tip_cy),
                                (index_finger_tip_cx, index_finger_tip_cy),
                                (155, 0, 155), 3)
                        cv2.circle(frame,
                                (volume_line_center_x, volume_line_center_y),
                                    10,
                                    (155, 0, 155))
                        volume = np.interp(volume_line_len, [100, 200], [0.0, 1.0])
                        volume_controller.set_volume(volume)
                    if mode_line_thumb < 100 and mode_line_index >= 60 and mode_line_middle >= 60:

                        mouse = mouse_controller()

                        mouse_distance = math.hypot(index_finger_tip_cx-center_x, index_finger_tip_cy-center_y)
                        # print(f"mouse from center: {mouse_distance}")

                        double_click_distance = math.hypot(index_finger_tip_cx-middle_finger_tip_cx, index_finger_tip_cy-middle_finger_tip_cy
                        )
                        if double_click_distance > 100:
                            mouse.click_button(1, True)
                            print("double click left")

                        if 90 >= mode_line_index >= 80:
                            mouse.click_button(1, False)
                            print("click left")
                        if 90 >= mode_line_middle >= 80:
                            mouse.click_button(2, False)
                            print("click right")

                        if 80 >= mode_line_index >= 60 and pressed_state == False:
                            pressed_state = True
                            mouse.press_button(1)
                            print("LMB pressed")
                        if 80 < mode_line_index and pressed_state == True:
                            pressed_state = False
                            mouse.release_button(1)
                            print("LMB released")

                        x_movement, y_movement = (index_finger_tip_cx-center_x)/mouse_sensitivity, (index_finger_tip_cy-center_y)/mouse_sensitivity
                        mouse.move_cursor(x_movement, y_movement)

                        cv2.line(frame,
                                 (index_finger_tip_cx, index_finger_tip_cy),
                                 (center_x, center_y),
                                 (155, 0, 0), 3)
                        cv2.line(frame,
                                 (middle_finger_tip_cx, middle_finger_tip_cy),
                                 (center_x, center_y),
                                 (155, 0, 0), 3)

                        cv2.line(frame,
                                 (index_finger_tip_cx, index_finger_tip_cy),
                                 (index_finger_cmc_cx, index_finger_cmc_cy),
                                 (155, 0, 155), 2)
                        cv2.line(frame,
                                 (middle_finger_tip_cx, middle_finger_tip_cy),
                                 (middle_finger_cmc_cx, middle_finger_cmc_cy),
                                 (155, 0, 155), 2)

        cv2.imshow("image", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    listener.listener.stop()
    cap.release()


main()
