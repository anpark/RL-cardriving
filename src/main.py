from gridworld import *
from qlearningAgents import *
import graphicsGridworldDisplay

if __name__ == '__main__':
	width = 4
	height = 20

	grid = Gridworld(width, height)
	grid.makeGrid()
	agent = QLearningAgent(grid)

	NumOfEpisode = 20

	display = graphicsGridworldDisplay.GraphicsGridworldDisplay(grid, 40, 1)

	for episode in range(0, NumOfEpisode):
		grid.runEpisode(agent, episode, display)