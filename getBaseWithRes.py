'''
  We typically use this file to implement
  generating basic policy with Residual Method
'''

from GameEnv import Game
import random
from PPOPolicy import PPOPolicy

if __name__ == '__main__':
    policy_set1 = []
    policy_set2 = []
    MAX = 20

    env = Game(8,8)

    for iteration in range(MAX):

        print('iteration {0} starts'.format(iteration))
        epoch = 0

        np1 = PPOPolicy(k=4, log_path='model/logs')
        np2 = PPOPolicy(k=4, log_path='model/logs')

        # when iteration == 0 , we don't need to choose
        if iteration == 0:

            while epoch < 20000:
                t = 0
                epoch += 1
                s, space = env.reset()
                s1 = s[0]
                s2 = s[1]

                while True:
                    a1, v1 = np1.get_action_value(s1)

                    a2, v2 = np2.get_action_value(s2)

                    s1_, s2_, r1, r2, done = env.step(a1, a2)

                    np1.save_transition(s1, s1_, a1, r1, v1, done, t)
                    np2.save_transition(s2, s2_, a2, r2, v2, done, t)

                    s1 = s1_
                    s2 = s2_

                    t += 1

                    if t > 200:
                        epoch -= 1
                        np1.empty_traj_memory()
                        np2.empty_traj_memory()
                        break

                    if done:
                        break

                if epoch % 100 == 0:
                    np1.train()
                    np2.train()


            np1.save_model('model/1/{0}.ckpt'.format(iteration))
            np2.save_model('model/2/{0}.ckpt'.format(iteration))


        else:

            p1_time = 0
            p2_time = 0

            while epoch < 20000:

                # for player1
                flag1 = False
                if random.uniform() > 0.5:
                    p1_time += 1
                    pi1 = np1
                    flag1 = True
                else:
                    pi1 = random.choice(policy_set1)

                # for player2
                flag2 = False
                if random.uniform() > 0.5:
                    p2_time += 1
                    pi2 = np2
                    flag2 = True
                else:
                    pi2 = random.choice(policy_set2)

                t = 0
                epoch += 1
                s, space = env.reset()
                s1 = s[0]
                s2 = s[1]

                # run this epoch
                while True:
                    a1, v1 = np1.get_action_value(s1)

                    a2, v2 = np2.get_action_value(s2)

                    s1_, s2_, r1, r2, done = env.step(a1, a2)

                    if flag1:
                        np1.save_transition(s1, s1_, a1, r1, v1, done, t)

                    if flag2:
                        np2.save_transition(s2, s2_, a2, r2, v2, done, t)

                    s1 = s1_
                    s2 = s2_

                    t += 1

                    if t > 200:
                        epoch -= 1
                        np1.empty_traj_memory()
                        np2.empty_traj_memory()
                        break

                    if done:
                        break

                if p1_time % 100 == 0:
                    np1.train()

                if p2_time % 100 == 0:
                    np2.train()

            np1.save_model('model/1/{0}.ckpt'.format(iteration))
            np2.save_model('model/2/{0}.ckpt'.format(iteration))