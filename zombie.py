import curses
import random
import sys

def end_game():
	pad.getch()
	curses.nocbreak()
	curses.echo()
	curses.curs_set(1)
	curses.endwin()
	sys.exit(0)

class Agent:
	def __init__(self,status,y,x):
		self.status = status
		self.location = [y,x]

		# human traits
		self.sightline = 3

		self.infection_proximity = 1 # how close a zombie has to be to infect a human
		self.infection_odds = 1 # out of 100. odds a zombie successfully infects

		self.torn_apart = 3 # how many zombies need to be direct neighbors to make a human die
		self.torn_apart_radius = 1 # how close a zombie has to be to tear up a human
		self.torn_apart_odds = 30 # odds a human will get torn apart if it's possible

		# zombie traits
		self.speed = 1 # max squares a zombie can move in one turn
		self.overwhelmed_limit = 5 # how many human neighbors it takes to kill a zombie
		self.overwhelmed_radius = 1 # how far from a zombie a human neighbor can be

	def reasses(self,locations):
		deltay = 0
		deltax = 0

		if self.status == 'human':
			torn_apart_neighbors = 0 # number of zombies close enough to tear up the numan
			
			# look for zombies
			for searchy in range(-self.sightline,self.sightline+1):
				targety = self.location[0] + searchy
				if targety < 0:
					targety += height
				elif targety > height - 1:
					targety -= height
				for searchx in range(-self.sightline,self.sightline+1):
					targetx = self.location[1] + searchx
					if targetx < 0:
						targetx += width
					elif targetx > width - 1:
						targetx -= width
					if [targety,targetx, 2] in locations: #zombie
						# check if it's close enough for infection
						if abs(searchy) <= abs(self.infection_proximity) and abs(searchx) <= abs(self.infection_proximity):
							infection_test = random.randint(0,100)
							if infection_test < self.infection_odds:
								self.status = 'zombie'

						# check if the zombie is close enough to tear human apart
						if abs(searchy) <= abs(self.overwhelmed_radius) and abs(searchx) <= abs(self.overwhelmed_radius):
							torn_apart_neighbors += 1

						# figure out where to run away
						if searchy < 0:	#if it's somewhere above
							deltay += 1
						elif searchy > 0: #if it's somewhere below
							deltay -= 1
						if searchx < 0: #if it's to the left
							deltax += 1
						elif searchx > 0: #if it's somewhere to the right
							deltax -= 1
			# check if human gets torn apart
			if torn_apart_neighbors >= self.torn_apart:
				torn_apart_test = random.randint(0,100)
				if torn_apart_test < self.torn_apart_odds:
					self.status = 'dead human'

			# if they're still alive, figure out which way to run:
			if self.status == 'human':
				if deltay > 0:
					self.location[0] += 1
				elif deltay < 0:
					self.location[0] -= 1

				if deltax > 0:
					self.location[1] += 1
				elif deltax < 0:
					self.location[1] -= 1

				randomizer_test = random.randint(0,100)
				if randomizer_test < randomizer_odds:
					self.location[random.randint(0,1)] += random.randint(-1,1)

		elif self.status == 'zombie':
			neighbors = 0
			for searchy in range(-self.overwhelmed_radius,self.overwhelmed_radius+1):
				for searchx in range(-self.overwhelmed_radius,self.overwhelmed_radius+1):
					if [self.location[0] + searchy,self.location[1] + searchx, 1] in locations: #humans
						neighbors += 1
			if neighbors >= self.overwhelmed_limit:
				self.status = 'dead zombie'
			else:
				move_test = random.randint(0,100) #should it randomly move?
				if move_test < move_odds:
					self.location[0] += random.randint(-self.speed,self.speed+1)
					self.location[1] += random.randint(--self.speed,self.speed+1)

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
	init_zombies = 0
	init_humans = 0 #starting pops

	# randomize the first population
	for y in range(0,height):
		for x in range(0,width):
			occupied_test = random.randint(0,100)
			if occupied_test < occupied_odds:
				zombie_test = random.randint(0,100)
				if zombie_test < zombie_odds:
					agent_type = "zombie"
					init_zombies += 1
				else:
					agent_type = "human"
					init_humans += 1

				current.append(Agent(agent_type,y,x))
	return [current,init_zombies,init_humans]

def print_pop(population, height, width):
	zombies = 0
	deadzombies = 0
	humans = 0
	deadhumans = 0

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
			humans += 1
		elif agent.status == 'zombie':
			colorpair = 2
			zombies += 1
		elif agent.status == 'dead zombie':
			colorpair = 3
			deadzombies += 1
		elif agent.status == 'dead human':
			colorpair = 4
			deadhumans += 1
		locations.append([agent.location[0],agent.location[1],colorpair])

	# parse the grid to print it
		for spot in locations:
			try:
				pad.addstr(spot[0],spot[1], "X", curses.color_pair(spot[2]))
			except curses.error as err:
				print "%s: %d | %d type: %d" % (err, spot[0], spot[1],spot[2])
				pass
	pad.refresh(0,0, 2,2, myscreen.getmaxyx()[0]-1,myscreen.getmaxyx()[1]-1)

	# print scores
	turned = init_humans - humans - deadhumans

	scorepad.clear()
	scorepad.addstr(1,1, "Humans: %d alive" % humans)
	scorepad.addstr(2,3, "%d dead" % deadhumans)
	scorepad.addstr(3,3, "%d turned to zombies" % turned)

	scorepad.addstr(4,1, "Zombies: %d" % zombies)
	scorepad.addstr(5,3, "%d dead" % deadzombies)
	scorepad.refresh(0,0, 2,width+1, myscreen.getmaxyx()[0]-1,myscreen.getmaxyx()[1]-1)
	
	# If it's over:
	if zombies == 0 or humans == 0:
		end_game()
	else:
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
		height = int(sys.argv[1])
		width = int(sys.argv[2])

	occupied_odds = 40
	zombie_odds = 10

	move_odds = 90 #odds that a zombie will move

	randomizer_odds = 31 #odds that a move will randomly get knocked out of whack

	current = []
	locations = []
	myscreen = curses.initscr()	#initialize the window
	pad = curses.newpad(height, width)	# new pad
	scorepad = curses.newpad(10,25) # scoreboard
	curses.start_color()	# turn on color
	curses.init_pair(1, 7, 7) # human color pair
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN) # zombie color pair
	curses.init_pair(3, curses.COLOR_BLACK, 10) # dead zombie
	curses.init_pair(4, curses.COLOR_BLACK, 15) # dead human
	curses.noecho()  # don't print keyboard output to screen
	curses.cbreak()  # react to keypresses without waiting for 'enter'
	curses.curs_set(0) # no blinking cursor

	initialize = init_game(width, height, occupied_odds, zombie_odds)
	current = initialize[0]
	init_zombies = int(initialize[1])
	init_humans = int(initialize[2])

	pause = ''
	while pause != "x":
		locations = print_pop(current, height,width)
		current = nextgen(current,locations)