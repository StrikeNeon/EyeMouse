import math
import cv2
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
            hand_data = h_tracker.get_landmark_data(rgb_image, hands)
            frame = h_tracker.draw_debug_landmarks(frame, hands)
            hand_1 = hand_data.get(0, None)
            if hand_1:
                thumb_tip = hand_1.get(4, None)
                index_finger_tip = hand_1.get(8, None)
                if thumb_tip and index_finger_tip:
                    thumb_tip_cx, thumb_tip_cy = thumb_tip[2], thumb_tip[3]
                    index_finger_tip_cx, index_finger_tip_cy = index_finger_tip[2], index_finger_tip[3]

                    line_center_x, line_center_y = (thumb_tip_cx+index_finger_tip_cx)//2, (thumb_tip_cy+index_finger_tip_cy)//2
                    line_len = math.hypot(index_finger_tip_cx-thumb_tip_cx, index_finger_tip_cy-thumb_tip_cy)

                    cv2.line(frame,
                             (thumb_tip_cx, thumb_tip_cy),
                             (index_finger_tip_cx, index_finger_tip_cy),
                             (155, 0, 155), 3)
                    cv2.circle(frame,
                               (line_center_x, line_center_y),
                               10,
                               (155, 0, 155))
                    if 200 >= line_len >= 100:
                        volume_controller.set_volume(int(line_len-100) / 100)
        cv2.imshow("image", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    listener.listener.stop()
    cap.release()


main()
