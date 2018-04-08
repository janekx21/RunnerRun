from pygame import *
import random
WIDTH = 256
HEIGHT = 144
DRAWS = (WIDTH,HEIGHT)
SIZE = (WIDTH*4,HEIGHT*4)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)

init()
screen = display.set_mode(SIZE)
draws = Surface(DRAWS)
SIZE = screen.get_size()
loop = True
clock = time.Clock()
T = 0
mapdata = {}
mapimgs = None
camx = 0
camy = 0
itemframe = image.load("pics/itemframe.png")



def lerp(a,b,t):
	return a*(1-t)+b*t

def loadArray(path,**options):
	arr = []
	img = image.load(path).convert_alpha()
	w,h = img.get_size()
	size = options.get('size',16)

	for y in range(h//size):
		for x in range(w//size):
			s = Surface((size,size),flags=SRCALPHA)
			s.set_alpha(0)
			s.blit(img,(0,0),(x*size,y*size,size,size))
			arr.append(s)
	return arr

itempics = loadArray("pics/itempics.png")

class Item:
	items = []
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.imgs = loadArray("pics/items.png")
		self.items.append(self)
		self.lastcollect = 0
		self.canbecollected = True
	def draw(self,screen):
		if (T - self.lastcollect) > 60*5:
			self.canbecollected = True
		if self.canbecollected:
			screen.blit(self.imgs[T//6%len(self.imgs)],(self.x-camx,self.y-camy))

	def collect(self,player):
		if(self.canbecollected):
			rindex = random.randrange(0,3)
			self.canbecollected = False
			self.lastcollect = T
			player.currentItem = rindex
			player.lastpickup = T


class JumpPad:
	items = []
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.imgs = loadArray("pics/spring.png")
		self.items.append(self)
	def draw(self,screen):
		screen.blit(self.imgs[T//6%len(self.imgs)],(self.x-camx,self.y-camy))

	def activate(self,player):
		player.vy = -4
		player.lastonground = T

particles = []
dieparticles = []
class Particle:
	path = "pics/explosion.png"
	maxlive = 60
	size = 32
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.imgs = loadArray(self.path,size =self.size)
		self.livetime = 0
		particles.append(self)
	def draw(self,screen):
		index = self.livetime//6%(len(self.imgs)-1)
		screen.blit(self.imgs[index],(self.x-camx-self.size//2,self.y-camy-self.size//2))
		self.livetime+=1
		if self.livetime>self.maxlive:
			self.die()
	def die(self):
		dieparticles.append(self)

class Explosion(Particle):
	path = "pics/explosion.png"
	maxlive = 53
	size = 32

class Dust(Particle):
	path = "pics/dust.png"
	maxlive = 6*4-1
	size = 8
	def __init__(self,x,y):
		Particle.__init__(self,x,y)
		self.offset = random.randrange(0,4) # wegen 4 verschidenen partikeln
	def draw(self,screen):
		index = self.livetime//6%4 + self.offset*5
		screen.blit(self.imgs[index],(self.x-camx-self.size//2,self.y-camy-self.size//2))
		self.livetime+=1
		if self.livetime>self.maxlive:
			self.die()




class Runner:
	runners = []
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.idl = loadArray("pics/charidl.png")
		self.idlR = [(transform.flip(z,True,False)) for z in self.idl]
		self.running = loadArray("pics/charrunnig.png")
		self.runningR = [(transform.flip(x,True,False)) for x in self.running]
		self.jump = loadArray("pics/charjump.png")
		self.jumpR = [(transform.flip(x,True,False)) for x in self.jump]
		self.state = "idl"
		self.speed = 2
		self.lastmovedir = 0
		self.onground = False
		self.lastonground = 0
		#Adding
		self.accaleration = .1
		#Multiplaying
		self.deaccaleration = .9

		self.currentItem = -1
		self.lastpickup = 0
		self.runners.append(self)
	def update(self):
		self.state = "idl"
		state = key.get_pressed()
		self.lastmovedir *= .99
		canmoveright = canmoveleft = True

		#logic
		if self.currentItem == 1:
			self.vy+=.01 #gravity
		else:
			self.vy+=.1 #gravity
		self.onground = False

		arr = []
		j = 1 # under
		for i in range(-1,2):
			ix,iy = (self.x+8)//16+i,(self.y+8)//16+j
			try:
				mapdata[(ix,iy)]
				arr.append(Rect((ix*16,iy*16,16,16)))
			except:pass
		index = Rect((self.x,self.y,16,16)).inflate(-2,2).collidelist(arr)
		if index >= 0:
			self.vy = 0
			self.y = self.y//16*16
			self.onground = True

		arr = []
		j = -1 # over
		for i in range(-1,2):
			ix,iy = (self.x+8)//16+i,(self.y+8)//16+j
			try:
				mapdata[(ix,iy)]
				arr.append(Rect((ix*16,iy*16,16,16)))
			except:pass
		index = Rect((self.x,self.y,16,16)).inflate(-2,2).collidelist(arr)
		if index >= 0:
			self.vy = 2

		arr = []
		j = -1 # over
		for i in range(-1,2):
			ix,iy = (self.x+8)//16+i,(self.y+8)//16+j
			try:
				mapdata[(ix,iy)]
				arr.append(Rect((ix*16,iy*16,16,16)))
			except:pass
		index = Rect((self.x,self.y,16,16)).inflate(-2,1).collidelist(arr)
		if index >= 0:
			self.vy = 2


		arr = []
		i = -1 # left
		j = 0
		ix,iy = (self.x+8)//16+i,(self.y+8)//16+j
		try:
			mapdata[(ix,iy)]
			arr.append(Rect((ix*16,iy*16,16,16)))
		except:pass
		index = Rect((self.x,self.y,16,16)).collidelist(arr)
		if index >= 0:
			self.vx = 0
			self.x = self.x//16*16+16
			canmoveleft = False

		arr = []
		i = 1 # right
		j = 0
		ix,iy = (self.x+8)//16+i,(self.y+8)//16+j
		try:
			mapdata[(ix,iy)]
			arr.append(Rect((ix*16,iy*16,16,16)))
		except:pass
		index = Rect((self.x,self.y,16,16)).inflate(2,0).collidelist(arr)
		if index >= 0:
			self.vx = 0
			self.x = self.x//16*16
			canmoveright = False

		if T - self.lastpickup > 120:
			if self.currentItem == 2:
				Explosion(self.x+8,self.y+8)
			self.currentItem = -1

		maxspeed = self.speed
		if self.currentItem == 0:
			maxspeed+=1

		if state[K_RIGHT] and canmoveright:
			self.vx+=self.accaleration
			if self.vx > maxspeed:
				self.vx = maxspeed
			self.lastmovedir = 1
		if state[K_LEFT] and canmoveleft:
			self.vx-=self.accaleration
			if self.vx < -maxspeed:
				self.vx = -maxspeed
			self.lastmovedir = -1
		
		if abs(self.lastmovedir)==1:
			self.state = "running"
			if self.onground and T%6==0:
				Dust(self.x+8,self.y+14)
		else:
			self.vx*=self.deaccaleration

		if state[K_UP] and self.onground:
			self.vy -= 3#Jumpheight is 3
			self.lastonground = T
		
		if not self.onground:
			self.state = "jump"

		for item in Item.items:
			if(Rect((self.x,self.y,16,16)).colliderect(Rect((item.x,item.y,16,16)))):
				item.collect(self)

		for item in JumpPad.items:
			if(Rect((self.x,self.y,16,16)).colliderect(Rect((item.x,item.y,16,16)).inflate(-16,0))):
				item.activate(self)

		self.x += self.vx
		self.y += self.vy
		global camx,camy
		# do cam lerping not includet jet
		camx = lerp(camx,self.x- WIDTH//2 + 8,1)
		camy = lerp(camy,self.y- HEIGHT//2 + 8,1)


	def draw(self,screen):
		
		#drawing
		if self.state == "idl":
			if self.lastmovedir > 0:
				pic = self.idl[T//6%len(self.idl)]
			else:
				pic = self.idl[T//6%len(self.idlR)]
		elif self.state == "running":
			if self.lastmovedir > 0:
				pic = self.running[T//6%len(self.running)]
			else:
				pic = self.runningR[T//6%len(self.runningR)]
		elif self.state == "jump":
			pic = Surface((16,16))
			if self.vy < 0:
				off = (T - self.lastonground) // 10
				if off > 3: off = 3
			if self.vy > 0:
				off = 3 + int(self.vy)
				if off > 7: off = 7
			if self.lastmovedir > 0:
				pic = self.jump[off]
			else:
				pic = self.jumpR[off]
				
		screen.blit(pic,(self.x-camx,self.y-camy))

def loadMap(path):
	img = image.load(path)
	w,h = img.get_size()
	for y in range(h):
		for x in range(w):
			c = img.get_at((x,y))
			if c == BLACK:
				mapdata[(x,y)] = random.randrange(0,16)//1
			if c == RED:
				Runner(x*16,y*16)
			if c == GREEN:
				Item(x*16,y*16)
			if c == BLUE:
				JumpPad(x*16,y*16)

mapimgs = loadArray("pics/blocks.png")
loadMap("maps/donwtown.png")


while loop:
	clock.tick(60)
	for e in event.get():
		if e.type == QUIT:
			loop = False
		if e.type == KEYDOWN:
			if e.key == K_ESCAPE:
				loop = False
	draws.fill(WHITE)
	#updates
	for r in Runner.runners:
		r.update()



	

	#draw map
	for pos,item in mapdata.iteritems():
		x,y = pos
		draws.blit(mapimgs[item],(x*16-camx,y*16-camy))
	for item in Item.items:
		item.draw(draws)
	for item in JumpPad.items:
		item.draw(draws)
	for runner in Runner.runners:
		runner.draw(draws)
	for particle in particles:
		particle.draw(draws)

	for particle in dieparticles:
		if particle in particles:
			particles.remove(particle)
	#draw ui
	
	for runner in Runner.runners:
		draws.blit(itempics[runner.currentItem],(16+8,16+8))
		draws.blit(itemframe,(16,16))

	#updatescreen
	screen.blit(transform.scale(draws,SIZE),(0,0))
	display.flip()
	T+=1