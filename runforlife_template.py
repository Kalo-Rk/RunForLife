#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Calipsomulator - a simple CA and Agent-based simulator
# 2026, nb@su
# 
# GUI: curseur, z, shift+z, d, shift+d, reset, shift-reset
#

import random
import numpy as np
#try numba fallback to plain python
try:
	from numba import njit
except ImportError:
	def njit(*args, **kwargs):
		def wrapper(f):
			return f
		return wrapper

import calipsolib
from calipsolib import Agent
# =-=-= Defining cell types

#COLORS ZONE 1 :
SAND1= 4    
SAND2= 5   
SLOPE= 6   
VALLEY= 7  

#COLORS ZONE 2 : 
GRASS1= 8
GRASS2= 9 
TREE= 10  
FIRE= 11
ASH1= 12
ASH2= 13

#COLORS ZONE 3 :
ICE1 = 14
ICE2=18 
SNOW= 15
FIRECAMP= 16
LUMIERE =17

#COLORS RUN :
START = 0
WHITE = 1
BLACK = 2
BORDER = 3


colors_ca = {

    SAND1:    (254,225,195),
    SAND2:    (227,186,156),
    SLOPE:    (172, 103, 64),
    VALLEY:   (113, 49, 47),
    
    GRASS1:    (143, 170, 93),
    GRASS2:    (98, 128, 75),
    TREE:    (56, 68, 44),
    FIRE:     (174, 51, 15),
    ASH1:     ( 85, 83, 82),
    ASH2:     (123,120,118),
    
    ICE1:    (251, 252, 254),
    ICE2:    (179, 186, 190),
    LUMIERE : (141, 159, 73),
    FIRECAMP: (130, 85, 30),
    

    START:    (255, 40, 40),
    WHITE:    (255,255,255),
    BLACK:    (  0,  0,  0),
    BORDER : (1,1,1)
}

# =-=-= Defining agent types

RUNNER = 9
HUNTER = 10

colors_agents = {
    RUNNER: (0,0,255),
    HUNTER:  (128,0,0),
}

# =-=-= simulation parameters

params = {
    "NbValley": 0, "densityValley": 0.10, "Nbhunt" : 1, "Nbrun" : 1, "Victoire" : 0, "densityTree" :0.35, "Hunter" : [], "Runner" : [], "nbfc":8, "nbSmart" : 0, "nbNotSmart" : 0,
    "hunter_positions" : [], "runner_positions" : [], "tempMax" : 90, "mortFroid" : 0, "mortFeu" : 0, "mortHunt" : 0, "mortSmart" : 0, "mortNotSmart" : 0, "nbArbreBrulee" :0,"PDB":False, "mortRun" : 0,
    "Voisinage3" : [(-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
    (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (1, -3), (1, -2), (1, -1),
    (1, 0), (1, 1), (1, 2), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]
}

# =-=-= user-defined agents

class Hunter(Agent):
    def __init__(self, x: float, y: float, params):
        super().__init__(x, y,"Hunter",params)
        self.type = HUNTER
        self.running = True

    def move(self, grid, agents):
        delta_y = random.choice((-1, 0, 1))
        runner_positions = params["runner_positions"]

        #Le feu tue le chasseur
            
        if (grid[self.x,self.y] == FIRE):
            self.running = False
            params["Nbhunt"] -= 1

        #Instinct de chasseur

        for (xV, yV) in params["Voisinage3"]:
            rvoisin = (self.x + xV, (self.y + yV) % self.dy)
            if rvoisin in runner_positions:
                rx, ry = rvoisin
                if rx > self.x:
                    delta_x = 1
                elif rx < self.x:
                    delta_x = -1
                if ry > self.y:
                    delta_y = 1
                elif ry < self.y:
                    delta_y = -1
                break

        self.y = (self.y + delta_y) % self.dy

        #Evite les bordures latérales périodiques et les frontières

        if (self.x > 0) and ((grid[self.x - 1,self.y] == START) or (grid[self.x - 1,self.y] == BORDER)) :
            delta_x = random.choice((0, 1))

        elif (self.x < self.dx - 1) and ((grid[self.x + 1,self.y] == BLACK) or (grid[self.x + 1,self.y] == WHITE) or (grid[self.x + 1,self.y] == BORDER)) :
            delta_x = random.choice((0, -1))

        else :
            delta_x = random.choice((-1, 0, 1))
        self.x = max(0, min(self.x + delta_x, self.dx - 1))

class Runner(Agent):
    def __init__(self, x: float, y: float, params):
        super().__init__(x, y,"Runner",params)
        self.type = RUNNER
        self.running = True

    def move(self, grid, agents):
        Voisins = params["Voisinage3"] + [(0,0)]
        current_cell = grid[self.x,self.y]
        hunter_positions = params["hunter_positions"]
        delta_x, delta_y = random.choice(( (0, -1), (0, +1), (1, -1), (1, 0), (1, +1) ))
        tempMax = params["tempMax"]

        #Le coureur prend des dégâts de température dans le zone de froid
        #Zone de froid : (2*dx//3)+1,dx-1

        if (current_cell == ICE1) or (current_cell == ICE2) :
            self.temp -= 1 #Dégats de froid
        elif (current_cell == LUMIERE) or (current_cell == FIRECAMP) :
            self.temp = min(self.temp + 1, tempMax) #Réchauffe au chaud

        #Le chasseur mange le courreur, le feu tue le coureur ou le coureur meurt de froid
            
        if ((self.x,self.y) in hunter_positions)  :
            self.running = False
            params["Nbrun"] -= 1
            params["mortHunt"] += 1
            params["mortRun"] += 1
            if (self.smart) :
                params["mortSmart"] += 1
                params["nbSmart"] -= 1
            else :
                params["mortNotSmart"] += 1
                params["nbNotSmart"] -= 1
        
        if (current_cell == FIRE) :
            self.running = False
            params["Nbrun"] -= 1
            params["mortFeu"] += 1
            params["mortRun"] += 1
            if (self.smart) :
                params["mortSmart"] += 1
                params["nbSmart"] -= 1
            else :
                params["mortNotSmart"] += 1
                params["nbNotSmart"] -= 1

        
        if (self.temp <= 0) :
            self.running = False
            params["Nbrun"] -= 1
            params["mortFroid"] += 1
            params["mortRun"] += 1
            if (self.smart) :
                params["mortSmart"] += 1
                params["nbSmart"] -= 1
            else :
                params["mortNotSmart"] += 1
                params["nbNotSmart"] -= 1

        #Les arbres cachent les coureurs

        if current_cell == TREE:
            self.cache = True
        elif current_cell != TREE:
            self.cache = False
        
        #Coureur intelligent, fuit et peut placer des feux de camps.

        if self.smart:

            #Fuite
            for (xV, yV) in Voisins :
                hvoisin = (self.x + xV, (self.y + yV) % self.dy)
                if hvoisin in hunter_positions :
                    hx , hy = hvoisin
                    if (hx > self.x) and (current_cell != START) :
                        delta_x = -1
                    if (hx < self.x) :
                        delta_x = 1

                    if (hy > self.y) :
                        delta_y = -1
                    if (hy < self.y) :
                        delta_y = 1
                    break

            #Placer un feu de camps    
            if self.x in range((10+(2*self.dx)//3), ((self.dx)-10)) :
                if (current_cell == ICE1) or (current_cell == ICE2) :
                    if self.fc == 1 :
                        if random.random() < 0.001 : 
                            # Rayon du cercle de lumière (diamètre 7, donc rayon = 3)
                            rayon = 8
                            for i in range(-rayon, rayon+1):  # Boucle sur x autour du feu
                                for j in range(-rayon, rayon+1):  # Boucle sur y autour du feu
                                    # Vérifier si (i, j) est dans le cercle
                                    if (i**2 + j**2) <= rayon**2:
                                        # S'assurer que la cellule est dans les limites de la grille
                                        if 0 <= self.x + i < self.dx and 0 <= self.y + j < self.dy:
                                            grid[self.x + i, self.y + j] = LUMIERE
                            grid[self.x, self.y] = FIRECAMP
                            params["nbfc"] += 1
                            self.fc = 0


        #Sur une pente, vitesse / 2

        if current_cell == SLOPE: 
            if (self.age%2 != 0) :
                self.x = (self.x + delta_x)
                self.y = (self.y + delta_y) % self.dy
        
        #Dans une vallée, vitesse / 3

        elif (current_cell == VALLEY):
            if (self.age%3 != 0) :
                self.x = (self.x + delta_x)
                self.y = (self.y + delta_y) % self.dy

        #Arrivée à la fin du monde

        elif ((current_cell == BLACK) or (current_cell == WHITE)) :
            params["Victoire"] += 1
            self.nbTour += 1
            if self.smart == False :
                self.smart = True
                params["nbSmart"] += 1
            self.x = (self.x + delta_x) % self.dx
            self.temp = tempMax
                        
        else :
            self.x = (self.x + delta_x)
            self.y = (self.y + delta_y) % self.dy
        
        self.age += 1


def make_agents(params):
    dx = params["dx"]
    dy = params["dy"]
    l = []
    nbR = 80
    nbH = 30
    for loop in range(nbR//4):
        r = Runner(x=0, y=random.randint(0,dy-1), params=params)
        r.smart = True
        l.append(r)
        (params["Runner"]).append(r)
        params["Nbrun"] += 1
        params["nbSmart"] += 1

    for loop in range(3*nbR//4):
        r = Runner(x=0, y=random.randint(0,dy-1), params=params)
        r.smart = False
        l.append(r)
        (params["Runner"]).append(r)
        params["Nbrun"] += 1
        params["nbNotSmart"] += 1

    # Chasseur ZONE 1

    for loop in range(nbH//3):
        h = Hunter(x=random.randint(0,(dx//3)-1), y=random.randint(0,dy-1), params=params)
        l.append(h)
        (params["Hunter"]).append(h)
        params["Nbhunt"] += 1
    
    # Chasseur ZONE 2

    for loop in range(nbH//3):
        h = Hunter(x=random.randint((dx//3)+1,(2*dx//3)-1), y=random.randint(0,dy-1), params=params)
        l.append(h)
        (params["Hunter"]).append(h)
        params["Nbhunt"] += 1

    # Chasseur ZONE 3    

    for loop in range(nbH//3):
        h = Hunter(x=random.randint((2*dx//3)+1,dx-1), y=random.randint(0,dy-1), params=params)
        l.append(h)
        (params["Hunter"]).append(h)
        params["Nbhunt"] += 1

    return l


# =-=-= user-defined callular automata

def init_simulation(params):
    densityValley = params["densityValley"]
    nbValley = params["NbValley"]
    dx = params["dx"]
    dy = params["dy"]

    grid = np.zeros((dx, dy), dtype=np.uint8)
    newgrid = np.empty((dx, dy), dtype=np.uint8)

    for x in range(dx): #Initialisation of the 3 climats
        for y in range(dy):
            if (x<=(dx/3)):
                grid[x,y]=random.choice((SAND1,SAND2))
                
            if (x>(dx/3)) and (x<=(2*dx/3)):
                grid[x,y]=random.choice((GRASS1,GRASS2)) 
            
            if (x>(2*dx/3)):
                if random.random()<0.6:
                    grid[x,y]=ICE1
                else:
                    grid[x,y]=ICE2
                
                
            if x==0:
                grid[x,y]=START

            if (x==(dx-1)) and (y%2==0):
                grid[x,y]=WHITE
            if (x==(dx-1)) and (y%2==1):
                grid[x,y]=BLACK    
                
            if ( (x==dx//3) or (x==2*dx//3) ):
                grid[x,y]=BORDER
    
    #INITIALISATION DES VALLEY DANS ZONE 1 :

    for i in range(16):
        x= random.randint(10,(dx-1)//3)
        y= random.randint(0,(dy-1))
        grid[x,y]=VALLEY
     

    while (nbValley < 1500): #Spreading of the valleys
        for x in range((10+dx)//3):
            for y in range (dy):
                n = random.random()
                if (nbValley < 1500) and (n < densityValley) and (grid[x,y]==SAND1 or grid[x,y]==SAND2)  and ((grid[x,(y+1)%dy] == VALLEY) or (grid[x,(y-1)%dy] == VALLEY) or (grid[(x-1)%dx,y] == VALLEY) or (grid[(x+1)%dx,y] == VALLEY)):
                    grid[x,y] = VALLEY
                    nbValley += 1
    
    
    for x in range(dx): #Addition of the slope
        for y in range (dy):
            if (grid[x,y] != VALLEY) and (grid[x,y]==SAND1 or grid[x,y]==SAND2) and ((grid[x,(y+1)%dy] == VALLEY) or (grid[x,(y-1)%dy] == VALLEY) or (grid[(x-1)%dx,y] == VALLEY) or (grid[(x+1)%dx,y] == VALLEY)):
                grid[x,y] = SLOPE
    
    params["nbValley"] = nbValley

    #INITIALISATION DE LA FORET DANS ZONE 2 :
    
    densityTree = params["densityTree"]

    for x in range(dx):
        if (x>=((dx+1)//3)) and (x<=(2*(dx-2)//3)):
            for y in range(dy): 
                if (random.random()<densityTree):
                    grid[x,y]=TREE
      
    #INITIALISATION DU DESERT GLACIAL DANS ZONE 3 : 
    
    #placement aleatoire des feux de camps : 
    nbfc= params["nbfc"]
    Liste_feux = []
    for i in range(nbfc):
        x= random.randint(10+(2*dx)//3,dx-10)
        y= random.randint(0,(dy-1))
        Liste_feux.append((x,y))
         

    # Rayon du cercle de lumière (diamètre 7, donc rayon = 3)
    rayon = 8
   
    for x,y in Liste_feux:
        for i in range(-rayon, rayon+1):  # Boucle sur x autour du feu
            for j in range(-rayon, rayon+1):  # Boucle sur y autour du feu
                # Vérifier si (i, j) est dans le cercle
                if (i**2 + j**2) <= rayon**2:
                    # S'assurer que la cellule est dans les limites de la grille
                    if 0 <= x + i < dx and 0 <= y + j < dy:
                        grid[x + i, y + j] = LUMIERE
    for x,y in Liste_feux:
        grid[x,y]=FIRECAMP 
    
    return grid, newgrid
    

@njit(cache=True) # A suprimer sur gedit
def ca_step(grid, newgrid, params):  
    dx, dy = grid.shape
    for x in range(dx):
        for y in range(dy):
            newgrid[x,y] = grid[x,y]
            if (x>((dx+3)/3)) and (x<=(2*(dx-2)/3)):
                newgrid[x,y] = grid[x,y]
                
                #Repousse des arbres 
                
                if grid[x,y]==GRASS1 or grid[x,y]==GRASS2:
                    if random.random()<0.001:
                        newgrid[x,y] = TREE
                        
                #Feux de foret        
                
                elif grid[x,y]==TREE:
                    if grid[(x+1)%dx,y] == FIRE or grid[(x-1)%dx,y] == FIRE or grid[x,(y+1)%dy] == FIRE or grid[x,(y-1)%dy] == FIRE:
                        newgrid[x,y] = FIRE
                        params["nbArbreBrulee"] += 1
                
                    elif random.random()<0.0005:
                        newgrid[x,y] = FIRE
                        params["nbArbreBrulee"] += 1

                        
                #Step ashe
                
                elif grid[x,y]==FIRE:
                    newgrid[x,y] = ASH1
                elif grid[x,y]==ASH1:
                    newgrid[x,y] = ASH2
                elif grid[x,y]==ASH2:
                    newgrid[x,y] = GRASS1

    #Point de bascule

    if params["PDB"]==False :
        if (params["nbArbreBrulee"] >= 5000) or (params["nbfc"] >= 12): 
            for x in range (((2*dx)//3)+1,dx-1):
                for y in range (dy):
                    newgrid[x,y]=random.choice((GRASS1,GRASS2))
            params["PDB"] = True    


if __name__ == "__main__":
    calipsolib.run(
        params=params, # user-defined
        init_simulation=init_simulation, # user-defined
        ca_step=ca_step, # user-defined
        make_agents=make_agents, # user-defined
        colors_ca=colors_ca,
        colors_agents=colors_agents,
        dx=200, # CA width
        dy=100, # CA height
        display_dx=1200,
        display_dy=900,
        title="Run For Life CA", 
        verbose=True, # display stuff (can be used by user)
        fps=60 # steps per seconds (default: 60)
    )
 