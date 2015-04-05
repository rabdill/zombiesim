import curses
import random
import sys

class Agent:
	def __init__(self,status,y,x):
		self.status = status
		self.location = [y,x]
		self.sightline = 3

	def reasses(self,locations):
		deltay = 0
		deltax = 0

		if self.status == 'human':
			for searchy in range(-self.sightline,self.sightline+1):
				for searchx in range(-self.sightline,self.sightline+1):
					if [self.location[0] + searchy,self.location[1] + searchx,2] in locations: #zombie
						if searchy < 0:	#if it's somewhere above
							deltay += 1
						elif searchy > 0: #if it's somewhere below
							deltay -= 1
						if searchx < 0: #if it's to the left
							deltax += 1
						elif searchx > 0: #if it's somewhere to the right
							deltax -= 1
			# figure out which way to run:
			if deltay > 0:
				self.location[0] += 1
			elif deltay < 0:
				self.location[0] -= 1

			if deltax > 0:
				self.location[1] += 1
			elif deltax < 0:
				self.location[1] -= 1
		else:	# if it's a zombie already
			move_test = random.randint(0,100)
			if move_test < move_odds:
				self.location[0] += random.randint(-1,1)
				self.location[1] += random.randint(-1,1)


		randomizer_test = random.randint(0,100)
		if randomizer_test < randomizer_odds:
			self.location[random.randint(0,1)] += random.randint(-1,1)

		#wraparound
		if self.location[0] < 0:
			self.location[0] += height-1
		if self.location[1] < 0:
			self.location[1] += width-1
		if self.location[0] > height-1:
				self.location[0] -= height-1
		if self.location[1] > width-1:
			self.location[1] -= width-1

		#if it's in the troublesome bottom right corner:
		if self.location[0] == height - 1 and self.location[1] == width - 1:
			self.location[0] -= 1
			

def init_game(width, height, occupied_odds, zombie_odds):
	# randomize the first population
	for y in range(0,height):
		for x in range(0,width):
			occupied_test = random.randint(0,100)
			if occupied_test < occupied_odds:
				zombie_test = random.randint(0,100)
				if zombie_test < zombie_odds:
					agent_type = "zombie"
				else:
					agent_type = "human"

				current.append(Agent(agent_type,y,x))
	return current

def print_pop(population, height, width):
	# fill everything in with periods
	for y in range(0,height):
		for x in range(0,width):
			if not (y == height - 1 and x == width - 1):
				try:
					pad.addstr(y, x, ".", curses.color_pair(0))
				except curses.error as err:
					print "%s: %d | %d type: ." % (err, y, x)
					pass
	locations = []
	# place all the agents in a grid
	for agent in population:
		if agent.status == 'human':
			colorpair = 1
		else:
			colorpair = 2
		locations.append([agent.location[0],agent.location[1],colorpair])

	# parse the grid to print it
		for spot in locations:
			try:
				pad.addstr(spot[0],spot[1], "#", curses.color_pair(spot[2]))
			except curses.error as err:
				print "%s: %d | %d type: %d" % (err, spot[0], spot[1],spot[2])
				pass
	pad.refresh(0,0, 2,2, myscreen.getmaxyx()[0]-1,myscreen.getmaxyx()[1]-1)
	return locations

def nextgen(population,locations):
	for agent in population:
		agent.reasses(locations)
	return population



if __name__ == '__main__':
	if len(sys.argv) < 3:
		width = 20
		height = 20
	else:
		width = int(sys.argv[1])
		height = int(sys.argv[2])

	occupied_odds = 40
	zombie_odds = 1

	move_odds = 90 #odds that a zombie will move

	randomizer_odds = 31 #odds that a move will randomly get knocked out of whack

	current = []
	locations = []
	myscreen = curses.initscr()	#initialize the window
	pad = curses.newpad(height, width)	# new pad
	curses.start_color()	# turn on color
	curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE) # set the human color pair
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN) # set the zombie color pair
	curses.noecho()  # don't print keyboard output to screen
	curses.cbreak()  # react to keypresses without waiting for 'enter'

	current = init_game(width, height, occupied_odds, zombie_odds)

	pause = ''
	while pause != "x":
		locations = print_pop(current, height,width)
		current = nextgen(current,locations)