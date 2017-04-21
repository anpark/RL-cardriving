import random
import util
from qlearningAgents import *
from enum import IntEnum
import graphicsGridworldDisplay
from graphicsGridworldDisplay import Obstacle


class Gridworld():
    """
    Gridworld
  """

    def __init__(self, width, height, model):
        self.width = width
        self.height = height
        self.model = model
        self.data = [[Obstacle.EMPTY for y in range(height)] for x in range(width)]
        self.duration = [[0 for y in range(height)] for x in range(width)]
        self.terminalState = 'TERMINAL_STATE'
        self.noise = 0.2
        self.state = (3, 0)
        self.startState = (3, 0)
        self.fixedStartState = (3, 0)
        self.pedestrianState = self.getCurrentPedestrianState()
        self.trafficState = self.getCurrentTrafficState()
        self.parkedCarState = self.getCurrentParkedCarState()
        self.overtakingCarState = self.getCurrentOvertakingCarState()
        self.crashed = False

    def makeGrid(self):
        self.data[self.width - 1][self.height - 1] = 10

    def isRightLane(self):
        if self.state[0] == 3:
            return True
        return False

    def isLeftLane(self):
        if self.state[0] == 2:
            return True
        return False

    def getPossibleActions(self, state):
        if state == self.terminalState:
            return ()
        # x,y = state

        # if x == (self.width - 1) and y == (self.height - 1):
        #   return ('exit')
        return 'forward', 'left', 'right', 'stop'

    def getPositionStates(self):
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

    def getPedestrianStates(self):
        """
    Return list of all states for pedestrian (either pedestrian is present in next grid or not).
    """
        states = [Obstacle.PEDESTRIAN, Obstacle.EMPTY]
        return states

    def getTrafficStates(self):
        """
    Return list of all states for traffic signals (either red/yellow/green/no signal).
    """
        states = [Obstacle.TRAFFIC_RED, Obstacle.TRAFFIC_GREEN, Obstacle.TRAFFIC_YELLOW, Obstacle.EMPTY]
        return states

    def getOvertakingCarStates(self):
        """
    Return list of all states for overtaking cars (just see two grids back and two speeds 1 and 2).
    """
        # 0, 0 for no cars in previous two grids
        # first value -1 or -2 for one or two grids to the back
        # second value 1 or 2 for speed of the overtaking car
        states = [(0, 0), (-1, 1), (-1, 2), (-2, 1), (-2, 2)]
        return states

    def getParkedCarStates(self):
        """
    Return list of all states for parked cars (either parked car is present in next grid or not).
    """
        states = [Obstacle.PARKED_CAR, Obstacle.EMPTY]
        return states

    def getReward(self, state, action):

        if state == self.terminalState:
            return 0.0

        if action == 'forward':
            return 0.5
        else:
            return -0.5

    def getPedestrianReward(self, state, action):

        if state == Obstacle.PEDESTRIAN:
            if action == 'forward':
                self.crashed = True
                return -10
            if action == 'left' or action == 'right':
                self.crashed = True
                return -5
            if action == 'stop':
                return 5
        elif state == Obstacle.EMPTY:
            if action == 'forward':
                return 0.5
            else:
                return -0.5
        return 0

    def getTrafficReward(self, state, action):

        if state == Obstacle.TRAFFIC_RED:
            if action == 'forward':
                self.crashed = True
                return -7
            if action == 'left' or action == 'right':
                self.crashed = True
                return -7
            if action == 'stop':
                return 5
        elif state == Obstacle.TRAFFIC_GREEN:
            if action == 'forward':
                return 1.0
            elif action == 'stop':
                return -2
            else:
                return -1
        elif state == Obstacle.EMPTY:
            if action == 'forward':
                return 0.5
            else:
                return -0.5
        return 0

    def getParkedCarReward(self, state, action):

        if state == Obstacle.PARKED_CAR:
            if action == 'forward':
                self.crashed = True
                return -8
            if action == 'left':
                return 3
            if action == 'stop':
                return 1
            elif action == 'right':
                return -3
        elif state == Obstacle.EMPTY:
            if action == 'forward':
                return 0.5
            else:
                return -0.5
        return 0

    def getOvertakingCarReward(self, state, action):

        pos = state[0]
        speed = state[1]
        if pos == 0: # no overtaking cars
            if action == 'forward':
                return 0.5
            else:
                return -0.5

        if self.isRightLane():
            invalid = 'right'
            careful = 'left'
        else:
            invalid = 'left'
            careful = 'right'

        if pos == -1:
            if speed == 1:
                if action == careful:
                    self.crashed = True
                    return -10
                if action == 'forward':
                    return 2
                if action == 'stop' or action == invalid:
                    return -3
            if speed == 2:
                if action == careful:
                    return -2
                if action == 'forward':
                    return 2
                if action == 'stop' or action == invalid:
                    return -3
        if pos == -2:
            if speed == 1:
                if action == careful:
                    return 1
                if action == 'forward':
                    return 3
                if action == 'stop' or action == invalid:
                    return -3
            if speed == 2:
                if action == careful:
                    self.crashed = True
                    return -10
                if action == 'forward':
                    return 2
                if action == 'stop' or action == invalid:
                    return -3

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
        stopState = state

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

        if action == 'stop':
            successors.append((stopState, 1 - self.noise))

            massLeft = self.noise
            successors.append((forwardState, massLeft / 2.0))
            successors.append((rightState, massLeft / 4.0))
            successors.append((leftState, massLeft / 4.0))

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

    def getCurrentPedestrianState(self):
        state = self.state
        if state[1] < self.height - 1:
            for i in range(self.width):
                if self.data[i][state[1] + 1] == Obstacle.PEDESTRIAN:
                    return Obstacle.PEDESTRIAN
        return Obstacle.EMPTY

    def getCurrentTrafficState(self):
        state = self.state
        y = state[1]
        if y < self.height - 1:
            if self.data[self.width - 1][y + 1] in (Obstacle.TRAFFIC_GREEN, Obstacle.TRAFFIC_RED, Obstacle.TRAFFIC_YELLOW):
                return self.data[self.width - 1][y + 1]
        return Obstacle.EMPTY

    def getCurrentParkedCarState(self):
        state = self.state
        if state[1] < self.height - 1:
            if self.data[state[0]][state[1] + 1] == Obstacle.PARKED_CAR:
                return Obstacle.PARKED_CAR
        return Obstacle.EMPTY

    def getCurrentOvertakingCarState(self):
        state = self.state
        if state == 'TERMINAL_STATE':
            x = self.width - 1
            y = self.height - 1
        else:
            x = state[0]
            y = state[1]
        if x == 2:
            z = 3
        else:
            z = 2
        print self.data[z][y-1]
        if y > 0 and self.data[z][y-1] == Obstacle.OVERTAKING_CAR_1:
            return -1, 1
        if y > 0 and self.data[z][y-1] == Obstacle.OVERTAKING_CAR_2:
            return -1, 2
        if y > 1 and self.data[z][y-2] == Obstacle.OVERTAKING_CAR_1:
            return -2, 1
        if y > 1 and self.data[z][y-2] == Obstacle.OVERTAKING_CAR_2:
            return -2, 2
        return 0, 0

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
        print 'doAction: ', action, ' current state: ', self.state
        successors = self.getTransitionStatesAndProbs(self.state, action)
        print 'successors: ', successors
        sum = 0.0
        rand = random.random()

        state = self.getCurrentState()
        pedestrianState = self.getCurrentPedestrianState()
        trafficState = self.getCurrentTrafficState()
        print 'Traffic state: ', trafficState
        parkedCarState = self.getCurrentParkedCarState()
        overtakingCarState = self.getCurrentOvertakingCarState()

        for nextState, prob in successors:
            sum += prob
            if sum > 1.1:
                raise 'Total transition probability more than one; sample failure.'
            if rand < sum:
                actionTaken = self.inferAction(state, nextState)
                if actionTaken is not None:
                    action = actionTaken
                rewards = [self.getReward(state, action), self.getPedestrianReward(pedestrianState, action),
                           self.getTrafficReward(trafficState, action), self.getParkedCarReward(parkedCarState, action),
                           self.getOvertakingCarReward(overtakingCarState, action)]
                if nextState == 'TERMINAL_STATE':
                    rewards[0] = 10.0
                self.state = nextState
                self.pedestrianState = self.getCurrentPedestrianState()
                self.trafficState = self.getCurrentTrafficState()
                self.parkedCarState = self.getCurrentParkedCarState()
                self.overtakingCarState = self.getCurrentOvertakingCarState()

                nextStates = [self.state, self.pedestrianState, self.trafficState, self.parkedCarState, self.overtakingCarState]
                return nextStates, rewards, action
        raise 'Total transition probability less than one; sample failure.'

    def reset(self):
        self.state = self.getStartState()

    def updateOppositeLaneCarsPositions(self):
        for i in range(2):
            for j in range(self.height):
                if self.data[i][j] == Obstacle.OPPOSITE_LANE_CAR:
                    self.data[i][j] = Obstacle.EMPTY
                    if j-i-1 >= 0:
                        self.data[i][j-i-1] = Obstacle.OPPOSITE_LANE_CAR

    def generateOppositeLaneCars(self):
        self.updateOppositeLaneCarsPositions()

        if util.flipCoin(0.15): # Generate a car in opposite two lanes
            if util.flipCoin(0.5): # Generate in slow lane
                self.data[0][self.height-1] = Obstacle.OPPOSITE_LANE_CAR
            else: # Generate in fast lane
                if util.flipCoin(0.5):
                    self.data[1][self.height-1] = Obstacle.OPPOSITE_LANE_CAR
                else:
                    self.data[1][self.height-2] = Obstacle.OPPOSITE_LANE_CAR

    def updatePedestriansPositions(self):
        for j in range(self.height):
            for i in range(4):
                if self.data[i][j] == Obstacle.PEDESTRIAN:
                    self.data[i][j] = Obstacle.EMPTY
                    if i + 1 < self.width:
                        self.data[i + 1][j] = Obstacle.PEDESTRIAN
                        print 'Relocating pedestrian to ', i+1, j
                        break

    def generatePedestrians(self):
        self.updatePedestriansPositions()

        if util.flipCoin(0.4): # Generate a car in opposite two lanes
            y = random.randint(0, self.height - 1)
            alreadyPresent = False
            for i in range(self.width):
                if self.data[i][y] == Obstacle.PEDESTRIAN:
                    alreadyPresent = True
                    break
            if not alreadyPresent:
                print 'Generating pedestrian at row ', y
                self.data[0][y] = Obstacle.PEDESTRIAN

    def updateParkedCarsPositions(self):
        for j in range(self.height):
            if self.data[3][j] == Obstacle.PARKED_CAR:
                if self.duration[3][j] >= 10:
                    self.duration[3][j] = 0
                    self.data[3][j] = Obstacle.OVERTAKING_CAR_1
                else:
                    self.duration[3][j] += 1

    def generateParkedCars(self):
        self.updateParkedCarsPositions()

        if util.flipCoin(0.2):
            y = random.randint(1, self.height - 2)
            alreadyPresent = False
            if self.data[3][y-1] == Obstacle.PARKED_CAR or self.data[3][y] == Obstacle.PARKED_CAR or self.data[3][y+1] == Obstacle.PARKED_CAR:
                alreadyPresent = True
            if not alreadyPresent:
                print 'Generating parked car at row ', y
                self.data[3][y] = Obstacle.PARKED_CAR

    def updateTrafficSignal(self):
        for j in range(self.height):
            if self.data[3][j] == Obstacle.TRAFFIC_RED:
                if self.duration[3][j] >= 20:
                    self.duration[3][j] = 0
                    self.data[3][j] = Obstacle.TRAFFIC_GREEN
                else:
                    self.duration[3][j] += 1
            elif self.data[3][j] == Obstacle.TRAFFIC_GREEN:
                if self.duration[3][j] >= 10:
                    self.duration[3][j] = 0
                    self.data[3][j] = Obstacle.EMPTY
                else:
                    self.duration[3][j] += 1

    def generateTrafficSignal(self):
        self.updateTrafficSignal()

        if util.flipCoin(0.4):
            y = random.randint(3, self.height - 2)
            alreadyPresent = False
            for j in range(self.height):
                if self.data[3][j] == Obstacle.TRAFFIC_RED:
                    alreadyPresent = True
            if not alreadyPresent:
                print 'Generating traffic red signal at row ', y
                self.data[3][y] = Obstacle.TRAFFIC_RED

    def updateOvertakingCarsPositions(self):
        for j in reversed(range(self.height)):
            for i in range(4):
                if self.data[i][j] == Obstacle.OVERTAKING_CAR_1:
                    self.data[i][j] = Obstacle.EMPTY
                    if j + 1 < self.height:
                        self.data[i][j + 1] = Obstacle.OVERTAKING_CAR_1
                        print 'Relocating overtaking_car_1 to ', i, j + 1
                elif self.data[i][j] == Obstacle.OVERTAKING_CAR_2:
                    self.data[i][j] = Obstacle.EMPTY
                    if j + 2 < self.height:
                        self.data[i][j + 2] = Obstacle.OVERTAKING_CAR_2
                        print 'Relocating overtaking_car_2 to ', i, j + 2

    def generateOvertakingCars(self):
        self.updateOvertakingCarsPositions()

        if util.flipCoin(0.5):
            if util.flipCoin(0.8):
                x = 2
            else:
                x = 3
            y = random.randint(0, self.height - 2)
            alreadyPresent = False
            if self.data[x][y-1] != Obstacle.EMPTY or self.data[x][y] != Obstacle.EMPTY or self.data[x][y+1] != Obstacle.EMPTY:
                alreadyPresent = True
            if not alreadyPresent:
                print 'Generating overtaking car at row ', y, ' and col ', x
                if x == 2:
                    self.data[x][y] = Obstacle.OVERTAKING_CAR_2
                else:
                    self.data[x][y] = Obstacle.OVERTAKING_CAR_1

    def generateRandomObstacles(self):
        self.generateOppositeLaneCars()
        if self.model == 'all' or self.model == 'pedestrian':
            self.generatePedestrians()
        if self.model == 'all' or self.model == 'parked_car':
            self.generateParkedCars()
        if self.model == 'all' or self.model == 'overtaking_car':
            self.generateOvertakingCars()
        if self.model == 'all' or self.model == 'traffic_signal':
            self.generateTrafficSignal()

    def clearAllObstacles(self):
        for i in range(self.width):
            for j in range(self.height):
                self.data[i][j] = Obstacle.EMPTY
                self.duration[i][j] = 0

    def runEpisode(self, agent, episode, display):

        returns = 0
        totalDiscount = 1.0
        self.reset()
        display.start()

        self.clearAllObstacles()

        print ("Starting Episode: " + str(episode) + "\n")
        while True:

            # DISPLAY CURRENT STATE
            state = self.getCurrentState()
            pedestrianState = self.getCurrentPedestrianState()
            trafficState = self.getCurrentTrafficState()
            parkedCarState = self.getCurrentParkedCarState()
            overtakingCarState = self.getCurrentOvertakingCarState()

            display.displayQValues(agent.staticAgent, state)

            # END IF IN A TERMINAL STATE
            actions = self.getPossibleActions(state)
            if len(actions) == 0:
                print ("EPISODE " + str(episode) + " COMPLETE: RETURN WAS " + str(returns) + "\n")
                return returns

            # GET ACTION (USUALLY FROM AGENT)
            action = agent.getAction(state, pedestrianState, trafficState, parkedCarState, overtakingCarState)
            if action is None:
                raise 'Error: Agent returned None action'

            # EXECUTE ACTION
            nextStates, rewards, actionTaken = self.doAction(action)
            print("Started in state: " + str(state) +
                  "\nSpecified action: " + str(action) +
                  "\nTook action: " + str(actionTaken) +
                  "\nEnded in state: " + str(nextStates) +
                  "\nGot reward: " + str(rewards) + "\n")
            # UPDATE LEARNER
            agent.update(state, pedestrianState, trafficState, parkedCarState, overtakingCarState, actionTaken, nextStates, rewards)

            # If there's a crash, end the episode
            if self.crashed:
                self.crashed = False
                print 'Car crashed with some obstacle! Ending episode..'
                return returns

            # Generate random obstacles
            self.generateRandomObstacles()
