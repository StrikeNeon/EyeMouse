import math
import cv2
import numpy as np
from pynput.mouse import Button
from hand_tracker import hand_tracker
from mouse_handler import mouse_listener
from volume_controler import win_audio_controller


def main():
    cam_width, cam_height = 648, 480

    cap = cv2.VideoCapture(0)
    cap.set(3, cam_width), cap.set(4, cam_height)
    h_tracker = hand_tracker(debug_draw=True)
    listener = mouse_listener()
    volume_controller = win_audio_controller(listener.process_name)
    while True:
        ret, frame = cap.read()

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands = h_tracker.find_hands(rgb_image)
        if listener.pressed and listener.button == Button.left:
            volume_controller.process_name = listener.process_name
        if hands:
            # Initial mode is none, if all target fingers far from base of hand, it stays that way
            # Volume control (thumb and index far from base of hand) - fingertips further for more volume, closer for less
            # don't forget to click on the process you want to control
            # Mouse control (thumb close to base of palm, index and middle up) - if the line between fingertips and base of palm
            # above thresh - register click for LMB for index finger bent, RMB for middle finger
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

                    print(f"modelines - index: {mode_line_index}, middle: {mode_line_middle}, thumb: {mode_line_thumb}")

                    if mode_line_thumb > 100 and mode_line_index > 100:

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
                    if mode_line_thumb < 100 and mode_line_index > 100 and mode_line_middle > 100:
                        cv2.line(frame,
                                 (index_finger_tip_cx, index_finger_tip_cy),
                                 (index_finger_cmc_cx, index_finger_cmc_cy),
                                 (155, 0, 155), 3)
                        cv2.line(frame,
                                 (middle_finger_tip_cx, middle_finger_tip_cy),
                                 (middle_finger_cmc_cx, middle_finger_cmc_cy),
                                 (155, 0, 155), 3)

        cv2.imshow("image", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    listener.listener.stop()
    cap.release()


main()
