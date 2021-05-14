import cv2
from hand_tracker import hand_tracker


cap = cv2.VideoCapture(0)
h_tracker = hand_tracker(debug_draw=True)
while True:
    ret, frame = cap.read()

    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame, hand_data = h_tracker.process_frame(rgb_image)
    print(hand_data)

    cv2.imshow("image", frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
