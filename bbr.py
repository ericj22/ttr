import random
import sys

import cv2
import mediapipe as mp
import pygame

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 640, 480
pygame.mixer.init()
pygame.mixer.music.load("soda-pop.mp3")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BBR")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)


# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils


# OpenCV setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


# Game setup
score = 0
box_size = 60
current_target = None
GAME_START = 0
GAME_PLAYING = 1
game_state = GAME_START


def get_new_target(width, height):
    x = random.randint(50, width - box_size - 50)
    y = random.randint(50, height - box_size - 50)
    return (x, y)


def track_hands(frame, results, target_rect):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger = hand_landmarks.landmark[8]
            cx, cy = int(index_finger.x * WIDTH), int(index_finger.y * HEIGHT)

            cv2.circle(frame, (cx, cy), 15, (50, 50, 200), cv2.FILLED)

            if target_rect.collidepoint(cx, cy):
                return True
    return False

# Game Loop

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    success, frame = cap.read()
    if not success: continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    hit = False
    if game_state == GAME_START:
        start_rect = pygame.Rect(50, 50, 240, 90)
        hit = track_hands(rgb_frame, results, start_rect)
        if hit:
            pygame.mixer.music.play(1)
            game_state = GAME_PLAYING
    if game_state == GAME_PLAYING:
        if current_target is None:
            current_target = get_new_target(WIDTH, HEIGHT)

        target_rect = pygame.Rect(current_target[0], current_target[1], box_size, box_size)
        hit = track_hands(rgb_frame, results, target_rect)
        if hit:
            score += 1
            current_target = get_new_target(WIDTH, HEIGHT)

    # Convert OpenCV array to Pygame Surface
    pg_bg = pygame.image.frombuffer(rgb_frame.tobytes(), (WIDTH, HEIGHT), 'RGB')
    screen.blit(pg_bg, (0, 0))

    if game_state == GAME_START:
        pygame.draw.rect(screen, (255, 0, 0), start_rect, 3)
        text_surf = font.render("Touch Here to Start!", True, (255, 0, 0))
        screen.blit(text_surf, (start_rect.x + 10, start_rect.y + 30))
    elif game_state == GAME_PLAYING:
        pygame.draw.rect(screen, (255, 0, 0), target_rect, 3)
        text_surf = font.render("TOUCH", True, (255, 0, 0))
        screen.blit(text_surf, (target_rect.x, target_rect.y - 30))

        score_surf = font.render(f"Score: {score}", True, (0, 255, 0))
        screen.blit(score_surf, (20, 20))

    pygame.display.flip()
    clock.tick(60)