import sys
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np


pygame.init()
font = pygame.font.Font('arial.ttf', 25)

BLOCK_SIZE = 20

# Enum for directions
class Direction(Enum):
  RIGHT = 1
  LEFT = 2
  UP = 3
  DOWN = 4

# Light class (named tuple) for point
Point = namedtuple('Point', 'x, y')

# Snake game class
class SnakeGameAI:
  # Init object
  def __init__(self, width=640, height=480):
    # Set width and height of the game
    self.width = width
    self.height = height

    # Init display
    self.display = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption('Snake')
    self.clock = pygame.time.Clock()
    self.reset()

    

  def reset(self):
    # Reset body state
    self.direction = Direction.RIGHT
    self.head = Point(self.width/2, self.height/2)
    self.snake = [
      self.head,
      Point(self.head.x-BLOCK_SIZE, self.head.y),
      Point(self.head.x-BLOCK_SIZE*2, self.head.y)
    ]

    # Reset game state
    self.speed = 15
    self.score = 0
    self.food = None
    self._place_food()
    self.frame_iteration = 0


  # Place food somewhere in the field
  def _place_food(self):
    x = random.randint(0, (self.width-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
    y = random.randint(0, (self.height-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
    self.food = Point(x, y)

    if self.food in self.snake:
      self._place_food()


  # Play one step
  def play_step(self, action):
    self.frame_iteration += 1
    for event in pygame.event.get():
      # If we close the game
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    
    # Move
    self._move(action)
    self.snake.insert(0, self.head)

    reward = 0

    # Check if game over
    game_over = False
    if self.is_collision() or self.frame_iteration > 100*len(self.snake):
      game_over = True
      reward = -10
      return reward, game_over, self.score

    # Place new food
    if self.head == self.food:
      self.speed += 2
      reward = 10
      self.score += 1
      self._place_food()
    else:
      self.snake.pop()

    # Update UI and clock
    self._update_ui()
    self.clock.tick(self.speed)

    # Return game over and score
    return reward, game_over, self.score


  # Move
  def _move(self, action):
    # Define directions and check which one is ours
    clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    id = clock_wise.index(self.direction)

    # action = [straight, right, left]
    if np.array_equal(action, [1, 0, 0]):
      new_dir = clock_wise[id]
    elif np.array_equal(action, [0, 1, 0]):
      new_dir = clock_wise[(id+1) % 4]
    else:
      new_dir = clock_wise[(id-1) % 4]

    self.direction = new_dir

    # Get current head's x and y
    x = self.head.x
    y = self.head.y

    # Update head position
    if self.direction == Direction.RIGHT:
      x += BLOCK_SIZE
    elif self.direction == Direction.LEFT:
      x -= BLOCK_SIZE
    elif self.direction == Direction.DOWN:
      y += BLOCK_SIZE
    elif self.direction == Direction.UP:
      y -= BLOCK_SIZE

    self.head = Point(x, y)

  # Colision detection
  def is_collision(self, pt=None):
    if pt == None:
      pt = self.head
    
    # Hits boundary
    if pt.x > self.width-BLOCK_SIZE or pt.x < 0 or pt.y > self.height-BLOCK_SIZE or pt.y < 0:
      return True

    # Hits itself
    if pt in self.snake[1:]:
      return True

    return False

  # Update UI
  def _update_ui(self):
    # Display background
    self.display.fill('black')

    # Draw snake
    for p in self.snake:
      pygame.draw.rect(self.display, 'darkgreen', pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
      pygame.draw.rect(self.display, 'lightgreen', pygame.Rect(p.x+4, p.y+4, 12, 12))

    # Draw food
    pygame.draw.rect(self.display, 'red', pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

    # Display score
    text = font.render('Score: ' + str(self.score), True, 'white')
    self.display.blit(text, [0, 0])

    # Update full display service
    pygame.display.flip()