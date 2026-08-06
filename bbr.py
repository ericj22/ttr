import random
import sys

import cv2
import mediapipe as mp
import pygame
import json
import sys

WIDTH, HEIGHT = 640, 480

def get_finger(frame, results, mp_hands, mp_draw):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger = hand_landmarks.landmark[8]
            cx, cy = int(index_finger.x * WIDTH), int(index_finger.y * HEIGHT)

            cv2.circle(frame, (cx, cy), 15, (50, 50, 200), cv2.FILLED)
            return (cx, cy)
    return None


def get_beat_map(song_info):
    BPM = song_info["bpm"]
    MS_PER_BEAT = 60000 / BPM
    ANIMATION_MS = BPM * 8
    
    OFFSET_MS = song_info["offset"]

    x_spots = [150, 250, 350]
    y_spots = [150, 250]
    prev_spot = (3, 3)

    beatmap = [] # (spawn_time_ms, x, y)
    cur_count = 0
    for eight_count in song_info["eight_counts"]:
        for beat in eight_count:
            spawn_time = int(((cur_count + beat) * MS_PER_BEAT) + OFFSET_MS - ANIMATION_MS)

            x_idx = random.randint(0, 2)
            y_idx = random.randint(0, 1)
            if prev_spot[0] == x_idx and prev_spot[1] == y_idx:
                y_idx -= 1
                x_idx -= 1
            tx = x_spots[x_idx]
            ty = y_spots[y_idx]
            prev_spot = (x_idx, y_idx)

            beatmap.append((spawn_time, tx, ty))
        cur_count += 8

    return beatmap
    
# Game Loop

def main(beat_file):
    with open(beat_file, "r") as file:
        song_info = json.load(file)

    score = 0
    box_size = 60
    GAME_START = 0
    GAME_PLAYING = 1
    game_state = GAME_START
    BPM = song_info["bpm"]
    
    ANIMATION_MS = BPM * 8

    beatmap = get_beat_map(song_info)
    active_targets = []

    # Setup MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # OpenCV setup
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    # Pygame init
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(song_info["audio"])

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BBR")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24, bold=True)

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

        finger_pos = get_finger(rgb_frame, results, mp_hands, mp_draw)

        # GAME LOGIC

        if game_state == GAME_START:
            start_rect = pygame.Rect(50, 50, 240, 90)
            if finger_pos and start_rect.collidepoint(finger_pos):
                game_state = GAME_PLAYING
                pygame.mixer.music.play()

        if game_state == GAME_PLAYING:
            current_music_time = pygame.mixer.music.get_pos()

            while beatmap and current_music_time >= beatmap[0][0]:
                target_time, tx, ty = beatmap.pop(0)
                active_targets.append({
                    "spawn_time": target_time,
                    "rect": pygame.Rect(tx, ty, box_size, box_size)
                })

            for i in range(len(active_targets) - 1, -1, -1):
                target = active_targets[i]
                time_alive = current_music_time - target["spawn_time"]
                progress = min(time_alive / ANIMATION_MS, 1.0)

                if progress >= 0.8 and finger_pos and target["rect"].collidepoint(finger_pos):
                    score += 100 * progress
                    active_targets.pop(i)
                    continue

                if time_alive > ANIMATION_MS + 100:
                    active_targets.pop(i)

        # Convert OpenCV array to Pygame Surface
        pg_bg = pygame.image.frombuffer(rgb_frame.tobytes(), (WIDTH, HEIGHT), 'RGB')
        screen.blit(pg_bg, (0, 0))

        if game_state == GAME_START:
            pygame.draw.rect(screen, (255, 0, 0), start_rect, 3)
            text_surf = font.render("Touch Here to Start!", True, (255, 0, 0))
            screen.blit(text_surf, (start_rect.x + 10, start_rect.y + 30))
        elif game_state == GAME_PLAYING:
            current_music_time = pygame.mixer.music.get_pos()

            for target in active_targets:
                time_alive = current_music_time - target["spawn_time"]
                progress = min(time_alive / ANIMATION_MS, 1.0)

                current_size = int(box_size * progress)
                anim_rect = pygame.Rect(0, 0, current_size, current_size)
                anim_rect.center = target["rect"].center

                pygame.draw.rect(screen, (100, 100, 100), target["rect"], 1)

                # Draw the expanding box. Turn it green when it enters the hit window.
                box_color = (0, 255, 0) if progress >= 0.8 else (255, 0, 0)
                pygame.draw.rect(screen, box_color, anim_rect, 3)
            
            score_surf = font.render(f"Score: {(int)(score)}", True, (0, 255, 0))
            screen.blit(score_surf, (20, 20))

        pygame.display.flip()
        clock.tick(60)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid arguments")
        exit()
    main(sys.argv[1])
