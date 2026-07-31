import random
import time

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

score = 0
box_size = 40
current_target = None


# Game states
GAME_START = 0
GAME_PLAYING = 1


game_state = GAME_START


def get_new_target(width, height):
    x = random.randint(50, width - box_size - 50)
    y = random.randint(50, height - box_size - 50)
    return(x, y)


def track_hands(frame, results, start, end):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger = hand_landmarks.landmark[8]
            cx, cy = int(index_finger.x * w), int(index_finger.y * h)

            cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)

            if start[0] < cx < end[0] and start[1] < cy < end[1]:
                return True
    return False


while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if game_state == GAME_START:
        cv2.rectangle(frame, (50, 50), (290, 140), (0, 0, 255), 3)
        cv2.putText(frame, "Touch Here to Start!", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 225), 2)
        if track_hands(frame, results, (50, 50), (290, 140)):
            game_state = GAME_PLAYING
    elif game_state == GAME_PLAYING:
        if current_target is None:
            current_target = get_new_target(w, h)

        tx, ty = current_target
        cv2.rectangle(frame, (tx, ty), (tx + box_size, ty + box_size), (0, 0, 255), 3)
        cv2.putText(frame, "TOUCH HERE", (tx, ty - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if track_hands(frame, results, current_target, (tx + box_size, ty + box_size)):
            current_target = get_new_target(w, h)

    cv2.imshow("Hand DDR", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


# Plan to: figure out a way to hand music
# Add a timer, and then check for timer beats/ticks for when to add squares
# Make a method for adding squares, check at every loop if we've reached a certain point in the song
# 


