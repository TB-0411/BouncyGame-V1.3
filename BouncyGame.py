import pygame, sys 
import names
import math
import random
from pygame.locals import *

SCREEN_SIZE = [640,480]
TICK = 160

VECTOR_ZERO = pygame.Vector2(0,0)

game = None
ball_sac = []
custom_balls = []

class Balls():
    # Attributes
    def __init__(self, name, color, size, speed, max_speed, position, direction):
        # Render
        self.name = name
        self.color = color or (random.randint(10,255),random.randint(10,255),random.randint(10,255))
        if game.is_acade_style: self.width = 2
        else: self.width = 0
        self.size = size or 20
        # Speed
        self.speed = speed or 1
        self.max_speed = max_speed or 2
        self.deformation = 0
        # Vector2
        self.position = position or BouncyGame.get_screen_center()
        self.direction = direction or BouncyGame.create_random_direction()
        # Collision stuff
        self.collision_count = 0
        self.collision_type = None
        self.can_collide = not game.wait_first_border_collision
        
    # Boolean
    
    def is_front_collision(self):
        return
    def is_side_collision(self):
        return
    def is_diagonal_collision(self):
        return
    def is_back_collision(self):
        return
    
    # Utility function
    
    def add_vectors(Vector1, Vector2):
        Vector1 = Vector1 + Vector2
        if Vector1.x >= 2 : Vector1.x = 1
        elif Vector1.y >= 2 : Vector1.y = 1
        if Vector1.x <= -2 : Vector1.x = -1
        elif Vector1.y <= -2 : Vector1.y = -1
        return Vector1
    
    def add_collison_factor(self,speed_bonus):
        self.collision_count += 1
        self.speed += speed_bonus
    
    # Function  
    
    # Movement
    def move(self):
        #if self.collision_count >= 2: # Can be blocked or Exploded
        self.position += self.direction
        
    # Draw   
    def affect_color(color):
        new_color = color
        if color == "RGB":
            new_color = (0,0,0)
        elif color == "Epileptic":
            new_color = (random.randint(10,255),random.randint(10,255),random.randint(10,255))
            
        return new_color
            
        
    def draw_rect_angle(surface, color, rect, angle, width=0): # Credit to Rabbid76
        target_rect = pygame.Rect(rect)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, (0, 0, *target_rect.size), width)
        rotated_surf = pygame.transform.rotate(shape_surf, angle)
        surface.blit(rotated_surf, rotated_surf.get_rect(center = target_rect.center))
        
    def draw_ellipse_angle(surface, color, rect, angle, width=0): # Credit to Rabbid76
        target_rect = pygame.Rect(rect)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(shape_surf, color, (0, 0, *target_rect.size), width)
        rotated_surf = pygame.transform.rotate(shape_surf, angle)
        surface.blit(rotated_surf, rotated_surf.get_rect(center = target_rect.center))    
        
    def draw(self):  
        self.deformation = (abs(self.direction.x)+abs(self.direction.y))*(self.speed/2)
        rect = pygame.Rect(self.position.x,self.position.y,(self.size*2),self.size*2+self.deformation)
        rect.center = self.position
        Balls.draw_ellipse_angle(game.window, Balls.affect_color(self.color), rect, pygame.Vector2.angle_to(self.direction,pygame.Vector2(0,1)), self.width)
        
    # Collision Detection
    def check_window_collision(self): # check whenever a ball touch the borders
        if (self.size >= self.position.x or self.position.x >= (game.window.get_width() - self.size)) and ((0 + self.size) >= self.position.y or self.position.y >= (game.window.get_height() - self.size)):
            # execute when in a corner
            Balls.add_collison_factor(self,0.1)
            self.collision_type = "Border"
            self.direction = -self.direction
        elif (self.size >= self.position.x or self.position.x >= (game.window.get_width() - self.size)):
            # execute when on the sides
            Balls.add_collison_factor(self,0.1)
            self.collision_type = "Border"
            self.direction.x = -self.direction.x
        elif (self.size >= self.position.y or self.position.y >= (game.window.get_height() - self.size)):
            # execute when on the top and bottom
            Balls.add_collison_factor(self,0.1)
            self.collision_type = "Border"
            self.direction.y = -self.direction.y
            
        if not self.can_collide : 
            self.can_collide = (self.collision_type == "Border")

    def check_collision(self):
        for ball in game.balls:
            distance = math.sqrt((self.position.x - ball.position.x)**2+(self.position.y - ball.position.y)**2)
            if distance <= (self.size + ball.size) and self != ball and ball.collision_count == 0 and (self.can_collide and ball.can_collide):
                
                Balls.add_collison_factor(ball,0.1) 
                self.collision_type = "Others"
                
                # distance = math.sqrt((self.position.x - (self.position.x+self.direction.x))**2+(self.position.y - (self.position.y+self.direction.y))**2)
                
                angle = math.atan2(self.position.y - ball.position.y, self.position.x - ball.position.x) # Angle from ball's distance
                ax = round(1 * math.cos(angle), 1) / 10 # Adjacent = Hypothenuse * cos(angle)
                ay = round(1 * math.sin(angle), 1) / 10
                # 1 -> abs(distance) slimy material
        
                self.direction = Balls.add_vectors(self.direction, pygame.Vector2(ax,ay))
                ball.direction = Balls.add_vectors(ball.direction, -pygame.Vector2(ax,ay))  # not - = gravity

                               
class BouncyGame():
    
    def __init__(self, participant, is_acade_style, are_all_epileptic, is_background_epileptic, full_screen, can_explode, can_knockout, wait_first_border_collision, do_speed_multiply):
        # Attributes
        self.balls = []
        self.window = None
        self.clock = 0
        self.participant = participant or 2
        self.is_loaded = False
        #Style
        self.is_acade_style = is_acade_style
        self.are_all_epileptic = are_all_epileptic
        self.is_background_epileptic = is_background_epileptic
        self.full_screen = full_screen
        # Gamerules
        self.can_explode = can_explode
        self.can_knockout = can_knockout
        self.wait_first_border_collision = wait_first_border_collision
        self.do_speed_multiply = do_speed_multiply
  
    def get_screen_center():
        x,y = game.window.get_size()
        return pygame.Vector2(x//2,y//2)
        
    def create_random_direction():
        direction = VECTOR_ZERO
        while direction == VECTOR_ZERO:
            direction = pygame.Vector2(random.randint(-1,1),random.randint(-1,1))
        return direction
        
    def generate_balls():
        for n in range(game.participant):           
            if n >= len(custom_balls):
                name = names.get_first_name()
                color = None
                size = random.choices([x for x in range(10,60,5)],[2**x for x in range(10,0,-1)])[0]
                speed = random.choices([x for x in range(1,11,1)],[2**x for x in range(10,0,-1)])[0]
                max_speed = speed * random.choices([1+x/10 for x in range(0,20,1)],[x for x in range(20,0,-1)])
                position = BouncyGame.get_screen_center()
                direction = BouncyGame.create_random_direction()
            else: name, color, size, speed, max_speed, position, direction = custom_balls[n]
            
            if game.are_all_epileptic :
                color = "Epileptic"

            ball_sac.append( Balls(name, color, size, speed, max_speed, position, direction) )
        
    def spawn_ball():
        if len(game.balls) != len(ball_sac): 
            game.balls.append(ball_sac[len(game.balls)])
        else: game.is_loaded = True

    def load():
        #execute once before starting the game
        if game.full_screen: game.window = pygame.display.set_mode()
        else: game.window = pygame.display.set_mode((SCREEN_SIZE[0],SCREEN_SIZE[1]))
        BouncyGame.generate_balls()
        pygame.time.Clock().tick(TICK//2)
        BouncyGame.tick()
      
    def tick():
        #called every tick
        has_to_stop = False
        while not has_to_stop:
            pygame.time.Clock().tick(TICK)
            game.clock += 1
            
            for ball in game.balls:
                Balls.draw(ball)
                for _ in range(int(round(ball.speed,0))):
                    Balls.check_window_collision(ball)
                    Balls.check_collision(ball)
                    Balls.move(ball)
                    ball.collision_count = 0

            # Allow to quit program
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                        
            pygame.display.update()
            if game.is_background_epileptic :
                game.window.fill([random.randint(10,255),random.randint(10,255),random.randint(10,255)])
            else : game.window.fill([0,0,0])
            
            if not game.is_loaded or len(game.balls) > 1:  # Game loop
                if not game.is_loaded and (game.clock % 10) == 0: BouncyGame.spawn_ball() 
            else: # Win Blablabla
                has_to_stop = True
        sys.exit()
            

            
game = BouncyGame(30,True,True,False,True,True,True,False,True)

pygame.display.init()

custom_balls = [
    ("Jeremy",(250,250,250),20,2,4,None,None),
    ("Youtube",(0,250,0),2,2,3,None,None),
    ("Blyat","Epileptic",30,10,20,None,None),
    #("Florio",(0,0,250),30,100,110,None,None),
    #("Draco",(150,0,0),49,101,110,None,None),
]

BouncyGame.load()

            
            
