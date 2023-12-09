import random
import time

import pygame

pygame.init()

window_width = 800
window_height = 600

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Snake Game")

snake_width = 10
snake_height = 10
head_position = [300, 250]
move_direction = "right"
snake_length = 1
snake_segments = [head_position.copy()]

apple_position = [
    random.randrange(1, (window_width // 10)) * 10,
    random.randrange(1, (window_height // 10)) * 10,
]

clock = pygame.time.Clock()


def draw_snake(snake_segments):
    for segment in snake_segments:
        pygame.draw.rect(
            screen,
            (0, 0, 255),
            pygame.Rect(segment[0], segment[1], snake_width, snake_height),
        )


def draw_apple(apple_position):
    pygame.draw.rect(
        screen,
        (255, 0, 0),
        pygame.Rect(apple_position[0], apple_position[1], snake_width, snake_height),
    )


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_direction = "left"
            elif event.key == pygame.K_RIGHT:
                move_direction = "right"
            elif event.key == pygame.K_UP:
                move_direction = "up"
            elif event.key == pygame.K_DOWN:
                move_direction = "down"

    if move_direction == "right":
        head_position[0] += 10
    elif move_direction == "left":
        head_position[0] -= 10
    elif move_direction == "up":
        head_position[1] -= 10
    elif move_direction == "down":
        head_position[1] += 10

    # Check if the snake hits the wall
    if (
        head_position[0] < 0
        or head_position[0] >= window_width
        or head_position[1] < 0
        or head_position[1] >= window_height
    ):
        pygame.quit()
        quit()

    snake_segments.insert(0, list(head_position))

    if head_position == apple_position:
        apple_position = [
            random.randrange(1, (window_width // 10)) * 10,
            random.randrange(1, (window_height // 10)) * 10,
        ]
        snake_length += 1
    else:
        snake_segments.pop()

    screen.fill((0, 0, 0))
    draw_apple(apple_position)
    draw_snake(snake_segments)

    pygame.display.update()

    clock.tick(15)  # Adjust the speed of the snake
