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
            print(hand_data)
        cv2.imshow("image", frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    listener.listener.stop()
    cap.release()

main()
