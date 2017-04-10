import random
import util
from qlearningAgents import *
import graphicsGridworldDisplay


class Gridworld():
    """
    Gridworld
  """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [[0 for y in range(height)] for x in range(width)]
        self.terminalState = 'TERMINAL_STATE'
        self.noise = 0.2
        self.state = (0, 0)
        self.startState = (3, 0)
        self.fixedStartState = (3, 0)

    def makeGrid(self):
        self.data[self.width - 1][self.height - 1] = 10

    def getPossibleActions(self, state):
        if state == self.terminalState:
            return ()
        # x,y = state

        # if x == (self.width - 1) and y == (self.height - 1):
        #   return ('exit')
        return 'forward', 'left', 'right'

    def getStates(self):
        """
    Return list of all states.
    """
        # The true terminal state.
        states = [self.terminalState]
        for x in range(self.width):
            for y in range(self.height):
                state = (x, y)
                states.append(state)
        return states

    def getReward(self, state, action):

        if state == self.terminalState:
            return 0.0

        if action == 'forward':
            return 0.5
        else:
            return -0.5

    def getStartState(self):
        return self.startState

    def isTerminal(self, state):
        return state == self.terminalState

    def getTransitionStatesAndProbs(self, state, action):

        if action not in self.getPossibleActions(state):
            raise "Illegal action!"

        if self.isTerminal(state):
            return []

        x, y = state

        if x == (self.width - 1) and y == (self.height - 1):
            return [(self.terminalState, 1.0)]

        successors = []

        forwardState = (self.__isAllowed(y + 1, x) and (x, y + 1)) or state
        leftState = (self.__isAllowed(y, x - 1) and (x - 1, y)) or state
        rightState = (self.__isAllowed(y, x + 1) and (x + 1, y)) or state

        if action == 'left' or action == 'right':
            if action == 'left':
                successors.append((leftState, 1 - self.noise))
            else:
                successors.append((rightState, 1 - self.noise))

            massLeft = self.noise
            successors.append((forwardState, massLeft / 1.0))

        if action == 'forward':
            successors.append((forwardState, 1 - self.noise))

            massLeft = self.noise
            successors.append((leftState, massLeft / 2.0))
            successors.append((rightState, massLeft / 2.0))

        successors = self.__aggregate(successors)

        return successors

    def __aggregate(self, statesAndProbs):
        counter = util.Counter()
        for state, prob in statesAndProbs:
            counter[state] += prob
        newStatesAndProbs = []
        for state, prob in counter.items():
            newStatesAndProbs.append((state, prob))
        return newStatesAndProbs

    def __isAllowed(self, y, x):
        if y < 0 or y >= self.height: return False
        if x < 2 or x >= self.width: return False
        return True;

    def getCurrentState(self):
        return self.state

    def inferAction(self, state, nextState):
        if nextState == "TERMINAL_STATE":  # state=="TERMINAL_STATE" or
            return None
        x1, y1 = state
        x2, y2 = nextState
        action = None
        if (x1 == x2 and y2 == y1 + 1):
            action = 'forward'
        elif (y1 == y2 and x2 == x1 + 1):
            action = 'right'
        elif (y1 == y2 and x2 == x1 - 1):
            action = 'left'
        return action

    def doAction(self, action):
        # print 'doAction: ', action
        successors = self.getTransitionStatesAndProbs(self.state, action)
        # print 'successors: ', successors
        sum = 0.0
        rand = random.random()
        state = self.getCurrentState()
        for nextState, prob in successors:
            sum += prob
            if sum > 1.0:
                raise 'Total transition probability more than one; sample failure.'
            if rand < sum:
                actionTaken = self.inferAction(state, nextState)
                if actionTaken is not None:
                    action = actionTaken
                reward = self.getReward(state, action)
                if nextState == 'TERMINAL_STATE':
                    reward = 10.0
                self.state = nextState
                return nextState, reward, action
        raise 'Total transition probability less than one; sample failure.'

    def reset(self):
        self.state = self.getStartState()

    def runEpisode(self, agent, episode, display):

        returns = 0
        totalDiscount = 1.0
        self.reset()
        display.start()

        print ("Starting Episode: " + str(episode) + "\n")
        while True:

            # DISPLAY CURRENT STATE
            state = self.getCurrentState()
            display.displayQValues(agent, state)

            # END IF IN A TERMINAL STATE
            actions = self.getPossibleActions(state)
            if len(actions) == 0:
                print ("EPISODE " + str(episode) + " COMPLETE: RETURN WAS " + str(returns) + "\n")
                return returns

            # GET ACTION (USUALLY FROM AGENT)
            action = agent.getAction(state)
            if action is None:
                raise 'Error: Agent returned None action'

            # EXECUTE ACTION
            nextState, reward, actionTaken = self.doAction(action)
            print("Started in state: " + str(state) +
                  "\nSpecified action: " + str(action) +
                  "\nTook action: " + str(actionTaken) +
                  "\nEnded in state: " + str(nextState) +
                  "\nGot reward: " + str(reward) + "\n")
            # UPDATE LEARNER
            agent.update(state, actionTaken, nextState, reward)
