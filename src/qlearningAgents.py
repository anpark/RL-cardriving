import random, util, math
from gridworld import *;
from pedestrianQLearningAgent import PedestrianQLearningAgent
from trafficQLearningAgent import TrafficQLearningAgent
from parkedCarQLearningAgent import ParkedCarQLearningAgent
from overtakingCarQLearningAgent import OvertakingCarQLearningAgent
from staticQLearningAgent import StaticQLearningAgent


class QLearningAgent():
    def __init__(self, grid):
        self.QValues = util.Counter()
        self.grid = grid
        self.epsilon = 0.05
        self.alpha = 1
        self.gamma = 0.8

        self.staticAgent = StaticQLearningAgent(grid)
        self.pedestrianAgent = PedestrianQLearningAgent(grid)
        self.trafficAgent = TrafficQLearningAgent(grid)
        self.parkedCarAgent = ParkedCarQLearningAgent(grid)
        self.overtakingCarAgent = OvertakingCarQLearningAgent(grid)

        # self.weights = [0.15, 0.25, 0.20, 0.15, 0.25]
        self.weights = [1.0, 0, 0, 0, 0]

    def getQValue(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action):
        return self.weights[0] * self.staticAgent.getQValue(state, action) + self.weights[1] * self.pedestrianAgent.getQValue(pedestrianState, action) \
               + self.weights[2] * self.trafficAgent.getQValue(trafficState, action) + self.weights[3] * self.parkedCarAgent.getQValue(parkedCarState, action) \
               + self.weights[4] * self.overtakingCarAgent.getQValue(overtakingCarState, action)

    def getValue(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState):
        actions = self.grid.getPossibleActions(state)
        if len(actions) < 1:
            return 0.0
        return max([self.getQValue(state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action) for action in actions])

    def getPolicy(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState):
        maxqval = float("-inf")
        bestAction = []
        actions = self.grid.getPossibleActions(state)
        if len(actions) == 0:
            return None
        for action in actions:
            qValue = self.getQValue(state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action)
            if qValue > maxqval:
                maxqval = qValue
                bestAction = [action]
            elif qValue == maxqval:
                bestAction.append(action)
        return random.choice(bestAction)

    def getAction(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState):
        # Pick Action
        print 'state: ', state, ' pedestrianState: ', pedestrianState, ' trafficState: ', trafficState, ' parkedCarState: ', parkedCarState, ' overtakingCarState: ', overtakingCarState
        legalActions = self.grid.getPossibleActions(state)
        action = None

        if len(legalActions) == 0:
            return action
        if util.flipCoin(self.epsilon):
            return random.choice(legalActions)
        else:
            return self.getPolicy(state, pedestrianState, trafficState, parkedCarState, overtakingCarState)

    #
    # state - current position state
    # action - action taken
    # nextStates - array of next states for static, pedestrian, traffic, parked car and overtaking car modules
    # rewards - array of rewards for static, pedestrian, traffic, parked car and overtaking car modules
    #
    def update(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action, nextStates, rewards):

        self.staticAgent.update(state, action, nextStates[0], rewards[0])
        self.pedestrianAgent.update(pedestrianState, action, nextStates[1], rewards[1])
        self.trafficAgent.update(trafficState, action, nextStates[2], rewards[2])
        self.parkedCarAgent.update(parkedCarState, action, nextStates[3], rewards[3])
        self.overtakingCarAgent.update(overtakingCarState, action, nextStates[4], rewards[4])
