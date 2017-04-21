import random, util, math
from gridworld import *;
from pedestrianQLearningAgent import PedestrianQLearningAgent
from trafficQLearningAgent import TrafficQLearningAgent
from parkedCarQLearningAgent import ParkedCarQLearningAgent
from overtakingCarQLearningAgent import OvertakingCarQLearningAgent
from staticQLearningAgent import StaticQLearningAgent
from graphicsGridworldDisplay import Obstacle


class QLearningAgent():
    def __init__(self, grid, model):
        self.model = model
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

        if self.model == 'all':
            self.weights = [0.15, 0.25, 0.20, 0.15, 0.25]
        elif model == 'pedestrian':
            self.weights = [0.15, 0.85, 0, 0, 0]
        elif model == 'traffic_signal':
            self.weights = [0.15, 0, 0.85, 0, 0]
        elif model == 'parked_car':
            self.weights = [0.15, 0, 0, 0.85, 0]
        elif model == 'overtaking_car':
            self.weights = [0.15, 0, 0, 0, 0.85]
        print 'self.weights: ', self.weights

    def getStaticWeights(self):
        if self.model == 'all':
            self.weights = [0.15, 0.25, 0.20, 0.15, 0.25]
        elif self.model == 'pedestrian':
            self.weights = [0.15, 0.85, 0, 0, 0]
        elif self.model == 'traffic_signal':
            self.weights = [0.15, 0, 0.85, 0, 0]
        elif self.model == 'parked_car':
            self.weights = [0.15, 0, 0, 0.85, 0]
        elif self.model == 'overtaking_car':
            self.weights = [0.15, 0, 0, 0, 0.85]
        return self.weights

    def getDynamicWeights(self, pedestrianState, trafficState, parkedCarState, overtakingCarState):
        temp_weights = self.getStaticWeights()
        print 'temp_weights: ', temp_weights
        if pedestrianState == Obstacle.EMPTY:
            temp_weights[1] = 0
        if trafficState == Obstacle.EMPTY:
            temp_weights[2] = 0
        if parkedCarState == Obstacle.EMPTY:
            temp_weights[3] = 0
        if overtakingCarState == (0, 0):
            temp_weights[4] = 0

        print 'temp_weights: ', temp_weights
        total = 0.0
        for i in range(len(temp_weights)):
            total += temp_weights[i]
        print 'total: ', total
        for i in range(len(temp_weights)):
            temp_weights[i] = temp_weights[i] / total
        print 'temp_weights: ', temp_weights
        return temp_weights

    def getQValue(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action):
        dynamic_weights = self.getDynamicWeights(pedestrianState, trafficState, parkedCarState, overtakingCarState)
        print 'dynamic_weigths: ', dynamic_weights
        return dynamic_weights[0] * self.staticAgent.getQValue(state, action) + dynamic_weights[
                                                                                 1] * self.pedestrianAgent.getQValue(
            pedestrianState, action) \
               + dynamic_weights[2] * self.trafficAgent.getQValue(trafficState, action) + dynamic_weights[
                                                                                           3] * self.parkedCarAgent.getQValue(
            parkedCarState, action) \
               + dynamic_weights[4] * self.overtakingCarAgent.getQValue(overtakingCarState, action)

    def getValue(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState):
        actions = self.grid.getPossibleActions(state)
        if len(actions) < 1:
            return 0.0
        return max(
            [self.getQValue(state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action) for action
             in actions])

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
    def update(self, state, pedestrianState, trafficState, parkedCarState, overtakingCarState, action, nextStates,
               rewards):

        self.staticAgent.update(state, action, nextStates[0], rewards[0])
        self.pedestrianAgent.update(pedestrianState, action, nextStates[1], rewards[1])
        self.trafficAgent.update(trafficState, action, nextStates[2], rewards[2])
        self.parkedCarAgent.update(parkedCarState, action, nextStates[3], rewards[3])
        self.overtakingCarAgent.update(overtakingCarState, action, nextStates[4], rewards[4])
