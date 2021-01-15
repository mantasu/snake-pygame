import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
  # Initialize agent's parameters
  def __init__(self):
    self.n_games = 0
    self.epsilon = 0    # randomness
    self.gamma = 0.9    # discount rate
    self.memory = deque(maxlen=MAX_MEMORY)
    self.model = Linear_QNet(11, 258, 3)
    self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
  
  # 11 values represent the state of the game
  def get_state(self, game):
    head = game.snake[0]

    # Clok-wise directions and angles
    cw_dirs = [
      Direction.RIGHT == game.direction, 
      Direction.DOWN == game.direction,
      Direction.LEFT == game.direction,
      Direction.UP == game.direction
      ]
    cw_angs = np.array([0, np.pi/2, np.pi, -np.pi/2])

    # Position - in front: 0, on right: 1, on left: -1; BLOCK_SIZE = 20
    getPoint = lambda pos: Point(
      head.x + 20*np.cos(cw_angs[(cw_dirs.index(True)+pos) % 4]),
      head.y + 20*np.sin(cw_angs[(cw_dirs.index(True)+pos) % 4]))

    state = [
      # Danger
      game.is_collision(getPoint(0)),
      game.is_collision(getPoint(1)),
      game.is_collision(getPoint(-1)),

      # Move direction
      cw_dirs[2],
      cw_dirs[0],
      cw_dirs[3],
      cw_dirs[1],

      # Food location
      game.food.x < head.x,
      game.food.x > head.x,
      game.food.y < head.y,
      game.food.y > head.y
    ]

    return np.array(state, dtype=int)

  # Add information of one frame iteration (when play step happens) to memory
  def remember(self, state, action, reward, next_state, done):
    self.memory.append((state, action, reward, next_state, done))

  # Train the model with information based on one full game
  def train_long_memory(self):
    if len(self.memory) > BATCH_SIZE:
      mini_sample = random.sample(self.memory, BATCH_SIZE)    # List of tuples
    else:
      mini_sample = self.memory

    states, actions, rewards, next_states, dones = zip(*mini_sample)
    self.trainer.train_step(states, actions, rewards, next_states, dones)

  # Train the model with information based on one frame iteration
  def train_short_memory(self, state, action, reward, next_state, done):
    self.trainer.train_step(state, action, reward, next_state, done)

  def get_action(self, state):
    # Random moves: tradeoff exploration / exploitation
    self.epsilon = 80 - self.n_games
    final_move = [0, 0, 0]

    # The bigger the epsilon, the more likely randint is lower
    if random.randint(0, 200) < self.epsilon:
      move = random.randint(0, 2)
      final_move[move] = 1
    else:
      state0 = torch.tensor(state, dtype=torch.float)
      prediction = self.model(state0)
      move = torch.argmax(prediction).item()
      final_move[move] = 1

    return final_move


# Train function
def train():
  plot_scores = []
  plot_mean_scores = []
  total_score = 0
  highscore = 0
  agent = Agent()
  game = SnakeGameAI()

  while True:
    # Get old state
    state_old = agent.get_state(game)

    # Get move
    final_move = agent.get_action(state_old)

    # Perform move and get new state
    reward, done, score = game.play_step(final_move)
    state_new = agent.get_state(game)

    # Train short memory
    agent.train_short_memory(state_old, final_move, reward, state_new, done)

    # Remember
    agent.remember(state_old, final_move, reward, state_new, done)

    if done:
      # Train long memory
      game.reset()
      agent.n_games += 1
      agent.train_long_memory()

      if score > highscore:
        highscore = score
        agent.model.save()

      print('Game', agent.n_games, 'Score', score, 'Highscore:', highscore)

      plot_scores.append(score)
      total_score += score
      mean_score = total_score / agent.n_games
      plot_mean_scores.append(mean_score)
      plot(plot_scores, plot_mean_scores)


# Launch function
if __name__ == '__main__':
  train()