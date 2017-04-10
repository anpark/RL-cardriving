import random, util, math
from gridworld import *;


class QLearningAgent():
    def __init__(self, grid):
        self.QValues = util.Counter()
        self.grid = grid
        self.epsilon = 0.05
        self.alpha = 1
        self.gamma = 0.8

    def getQValue(self, state, action):
        return self.QValues[(state, action)]

    def getValue(self, state):
        actions = self.grid.getPossibleActions(state)
        if len(actions) < 1:
            return 0.0

        return max([self.QValues[(state, action)] for action in actions])

    def getPolicy(self, state):
        maxqval = float("-inf")
        bestAction = []
        actions = self.grid.getPossibleActions(state)
        if len(actions) == 0:
            return None
        for action in actions:
            qValue = self.QValues[(state, action)]
            if qValue > maxqval:
                maxqval = qValue
                bestAction = [action]
            elif qValue == maxqval:
                bestAction.append(action)
        return random.choice(bestAction)

    def getAction(self, state):
        # Pick Action
        legalActions = self.grid.getPossibleActions(state)
        action = None

        if len(legalActions) == 0:
            return action
        if util.flipCoin(self.epsilon):
            return random.choice(legalActions)
        else:
            return self.getPolicy(state)

    def update(self, state, action, nextState, reward):

        if state == "TERMINAL_STATE":
            return
        env = state
        nextenv = nextState
        oldQsa = self.QValues[(env, action)]
        nextActions = self.grid.getPossibleActions(nextState)
        if len(nextActions) == 0:
            maxFutureValue = self.QValues[(nextenv, action)]
        else:
            maxFutureValue = max([self.QValues[(nextenv, nextAction)] for nextAction in nextActions])
        self.QValues[(env, action)] = oldQsa + self.alpha * (reward + self.gamma * (maxFutureValue) - oldQsa)
