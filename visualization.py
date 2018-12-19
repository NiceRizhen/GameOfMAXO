'''
  This files contains visualization functions
  for observing the performance of our policy.

  @Author: Jingcheng Pang
'''

import time
import numpy as np
import tkinter as tk
from GameEnv import Game
from PPOPolicy import PPOPolicy
from RandomPolicy import RandomPolicy
from collections import deque

# visualization params
UNIT   = 40
MAZE_H = 10
MAZE_W = 10

# units in env
GROUND   = 0
WALL     = 1
OPPONENT = 2
TREASURE = 3

class Maze(tk.Tk, object):
    def __init__(self, space):
        super(Maze, self).__init__()
        self.action_space = ['u', 'd', 'l', 'r']
        self.n_actions = len(self.action_space)
        self.title('Grid World')
        self.geometry('{0}x{1}'.format(MAZE_H * UNIT, MAZE_H * UNIT))
        self.wall = []
        self.treasure = []
        self._build_maze(space)

    def _build_maze(self, space):
        self.wall = []
        self.canvas = tk.Canvas(self, bg='white',
                           height=MAZE_H * UNIT,
                           width=MAZE_W * UNIT)

        # create grids
        for c in range(0, MAZE_W * UNIT, UNIT):
            x0, y0, x1, y1 = c, 0, c, MAZE_H * UNIT
            self.canvas.create_line(x0, y0, x1, y1)
        for r in range(0, MAZE_H * UNIT, UNIT):
            x0, y0, x1, y1 = 0, r, MAZE_W * UNIT, r
            self.canvas.create_line(x0, y0, x1, y1)

        # create origin
        origin = np.array([20, 20])

        player = 0
        for x in range(10):
            for y in range(10):

                # create walls
                if space[x, y] == WALL:
                    wall_center = origin + np.array([UNIT * y, UNIT * x])
                    self.wall.append(self.canvas.create_rectangle(
                        wall_center[0] - 15, wall_center[1] - 15,
                        wall_center[0] + 15, wall_center[1] + 15,
                        fill='black'))

                # create treasure
                elif space[x, y] == TREASURE:
                    oval_center = origin + np.array([UNIT * y, UNIT * x])
                    self.treasure.append(self.canvas.create_oval(
                        oval_center[0] - 15, oval_center[1] - 15,
                        oval_center[0] + 15, oval_center[1] + 15,
                        fill='yellow'))

                # create players
                elif space[x, y] == OPPONENT:
                    if player is 0:
                        player += 1
                        rect_center = origin + np.array([UNIT * y, UNIT * x])
                        self.player1 = self.canvas.create_rectangle(
                            rect_center[0] - 15, rect_center[1] - 15,
                            rect_center[0] + 15, rect_center[1] + 15,
                            fill='red')
                    else:
                        rect_center = origin + np.array([UNIT * y, UNIT * x])
                        self.player2 = self.canvas.create_rectangle(
                            rect_center[0] - 15, rect_center[1] - 15,
                            rect_center[0] + 15, rect_center[1] + 15,
                            fill='blue')

        # pack all
        self.canvas.pack()

    def step(self, action1, action2, who_takes):
        s1 = self.canvas.coords(self.player1)
        s2 = self.canvas.coords(self.player2)

        # player1
        base_action1 = np.array([0, 0])
        if action1 == 0:   # up
            if s1[1] > UNIT:
                base_action1[1] -= UNIT
        elif action1 == 1:   # down
            if s1[1] < (MAZE_H - 1) * UNIT:
                base_action1[1] += UNIT
        elif action1 == 2:   # left
            if s1[0] > UNIT:
                base_action1[0] -= UNIT
        elif action1 == 3:   # right
            if s1[0] < (MAZE_W - 1) * UNIT:
                base_action1[0] += UNIT

        # player2
        base_action2 = np.array([0, 0])
        if action2 == 0:   # up
            if s2[1] > UNIT:
                base_action2[1] -= UNIT
        elif action2 == 1:   # down
            if s2[1] < (MAZE_H - 1) * UNIT:
                base_action2[1] += UNIT
        elif action2 == 2:   # left
            if s2[0] > UNIT:
                base_action2[0] -= UNIT
        elif action2 == 3:   # right
            if s2[0] < (MAZE_W - 1) * UNIT:
                base_action2[0] += UNIT

        self.canvas.move(self.player1, base_action1[0], base_action1[1])  # move player1
        self.canvas.move(self.player2, base_action2[0], base_action2[1])  # move player2

        s_1 = self.canvas.coords(self.player1)  # next state
        s_2 = self.canvas.coords(self.player2)  # next state

        for tr in self.treasure:
            if s_1 == self.canvas.coords(tr):
                self.canvas.delete(tr)

            elif s_2 == self.canvas.coords(tr):
                self.canvas.delete(tr)

        if s_1 in [self.canvas.coords(wal) for wal in self.wall]:
            self.canvas.move(self.player1, -base_action1[0], -base_action1[1])

        if s_2 in [self.canvas.coords(wal) for wal in self.wall]:
            self.canvas.move(self.player2, -base_action2[0], -base_action2[1])

        if who_takes == 1:
            self.canvas.itemconfig(self.player1, fill='yellow', outline='red', width=10)
            self.canvas.itemconfig(self.player2, fill='blue', width = 0)
        if who_takes == 2:
            self.canvas.itemconfig(self.player1, fill='red', width = 0)
            self.canvas.itemconfig(self.player2, fill='yellow', outline='blue', width=10)


    def render(self):
        time.sleep(0.15)
        self.update()

if __name__ == '__main__':
    space = []

    ga = Game(8,8)

    pi1 = PPOPolicy(is_training=False, model_path='model/2-3(150000)/1.ckpt', k=4)
    pi2 = PPOPolicy(is_training=False, model_path='model/2-3(150000)/5.ckpt', k=4)

    while True:
        s, space = ga.reset()
        s1 = s[0]
        s2 = s[1]
        env = Maze(space)
        t = 0

        p1_state = deque(maxlen=4)
        p2_state = deque(maxlen=4)

        for i in range(4):
            zero_state = np.zeros([45])
            p1_state.append(zero_state)
            p2_state.append(zero_state)

        while True:
            env.render()

            p1_state.append(s1)
            p2_state.append(s2)

            state1 = np.array([])
            for obs in p1_state:
                state1 = np.hstack((state1, obs))

            state2 = np.array([])
            for obs in p2_state:
                state2 = np.hstack((state2, obs))

            a1 = pi1.choose_action_full_state(state1)
            a2 = pi2.choose_action_full_state(state2)
            env.step(a1, a2, ga.who_takes_it)

            s1_,s2_,r1,r2,done = ga.step(a1,a2)

            s1 = s1_
            s2 = s2_
            t += 1
            if t > 100:
                break

            if done:
                env.render()
                time.sleep(0.2)
                break

        env.destroy()

