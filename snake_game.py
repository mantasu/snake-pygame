import sys
import pygame
import random
from enum import Enum
from collections import namedtuple


pygame.init()
font = pygame.font.Font('arial.ttf', 25)

speed = 10
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
class SnakeGame:
  # Init object
  def __init__(self, width=640, height=480):
    # Set width and height of the game
    self.width = width
    self.height = height

    # Init display
    self.display = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption('Snake')
    self.clock = pygame.time.Clock()

    # Init body state
    self.direction = Direction.RIGHT
    self.head = Point(self.width/2, self.height/2)
    self.snake = [
      self.head,
      Point(self.head.x-BLOCK_SIZE, self.head.y),
      Point(self.head.x-BLOCK_SIZE*2, self.head.y)
    ]

    # Init game state
    self.score = 0
    self.food = None
    self._place_food()


  # Place food somewhere in the field
  def _place_food(self):
    x = random.randint(0, (self.width-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
    y = random.randint(0, (self.height-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
    self.food = Point(x, y)

    if self.food in self.snake:
      self._place_food()


  # Play one step
  def play_step(self):
    # Collect input
    for event in pygame.event.get():
      # If we close the game
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
      # If we move the snake
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
          self.direction = Direction.LEFT
        elif event.key == pygame.K_RIGHT:
          self.direction = Direction.RIGHT
        elif event.key == pygame.K_UP:
          self.direction = Direction.UP
        elif event.key == pygame.K_DOWN:
          self.direction = Direction.DOWN
    
    # Move
    self._move(self.direction)
    self.snake.insert(0, self.head)

    # Check if game over
    game_over = False
    if self._is_collision():
      game_over= True
      return game_over, self.score

    # Place new food
    if self.head == self.food:
      global speed
      speed += 1
      self.score += 1
      self._place_food()
    else:
      self.snake.pop()

    # Update UI and clock
    self._update_ui()
    self.clock.tick(speed)

    # Return game over and score
    return game_over, self.score


  # Move
  def _move(self, direction):
    # Get current head's x and y
    x = self.head.x
    y = self.head.y

    # Update head position
    if direction == Direction.RIGHT:
      x += BLOCK_SIZE
    elif direction == Direction.LEFT:
      x -= BLOCK_SIZE
    elif direction == Direction.DOWN:
      y += BLOCK_SIZE
    elif direction == Direction.UP:
      y -= BLOCK_SIZE

    self.head = Point(x, y)

  # Colision detection
  def _is_collision(self):
    # Hits boundary
    if self.head.x > self.width-BLOCK_SIZE or self.head.x < 0 or self.head.y > self.height-BLOCK_SIZE or self.head.y < 0:
      return True

    # Hits itself
    if self.head in self.snake[1:]:
      return True

    return False

  # Update UI
  def _update_ui(self):
    # Display background
    self.display.fill('black')

    # Draw snake
    for p in self.snake:
      pygame.draw.rect(self.display, 'blue', pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
      pygame.draw.rect(self.display, 'lightblue', pygame.Rect(p.x+4, p.y+4, 12, 12))

    # Draw food
    pygame.draw.rect(self.display, 'red', pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

    # Display score
    text = font.render('Score: ' + str(self.score), True, 'white')
    self.display.blit(text, [0, 0])

    # Update full display service
    pygame.display.flip()


if __name__ == '__main__':
  if len(sys.argv) > 1:
    start_speed = int(sys.argv[1])
    speed = start_speed

  game = SnakeGame()

  # Game loop
  while True:
    game_over, score = game.play_step()

    # Break if game over
    if game_over == True:
      break
  
  print('Final score', game.score)
  pygame.quit()