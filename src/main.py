from gridworld import *
from qlearningAgents import *
import graphicsGridworldDisplay
import sys

if __name__ == '__main__':

    if len(sys.argv) == 1:
        model = "all"
    else:
        model = sys.argv[1]

    width = 4
    height = 16

    grid = Gridworld(width, height, model)
    grid.makeGrid()
    agent = QLearningAgent(grid, model)

    NumOfEpisode = 20

    display = graphicsGridworldDisplay.GraphicsGridworldDisplay(grid, 60, 1)

    for episode in range(0, NumOfEpisode):
        grid.runEpisode(agent, episode, display)