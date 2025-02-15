import pygame
import random
import math
import time
from pygame import mixer
import json

#Initialise pygame
pygame.init()

# Window Settings
HEIGHT = 800 # Defines the Height of my window
WIDTH = 1260   # Defines the WIDTH of my window
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT)) # Creates the game window
pygame.display.set_caption("Aim Trainer") #The text to be displayed on the top left of the window
ICON = pygame.image.load("assets/icon.png") #Stores the icon image into the variable ICON
pygame.display.set_icon(ICON) #Sets the image as the window icon
BACKGROUND = pygame.image.load("assets/background.jpg") # Loads the image and stores it into the variable BACKGROUND


#Global variables
STATS_FONT = pygame.font.SysFont("Georgia", 30, True)
targets = []
TARGET_IMAGE = pygame.image.load("assets/target.png")
score = 0
accuracy = 0
shots = 0
START_TIME = time.monotonic()
timer = 0
game_finished = False
pause = False
minimum_distance = 100
global Game
global StatsClass
statistics = {
    "score_easy": [],
    "accuracy_easy": [],
    "score_medium":[],
    "accuracy_medium": [],
    "score_hard": [],
    "accuracy_hard":[]
   
    }


class Button:
    def __init__(self, x, y, text): # Constructor of the Class
        self.width = 90 #Width of the button Rectangle
        self.height = 192 #Height of the button Rectangle
        self.color = (100, 100, 100) # The color of the rectangle
        self.color2 = (250, 250, 250)# The color of the text of the Button
        self.color3 = (50, 50 , 50) # The color of the button rectangle when the mouse hovers over it
        self.font = pygame.font.SysFont("Georgia", 40, True)
        self.x = x #X Coordinate of the Button
        self.y = y # Y Coordinate of the Button
        self.text = text # The text to be displayed on the rectangle
        self.button = pygame.Rect(self.x, self.y, self.height, self.width) # Creation of the rectangle
        self.rendered_text = self.font.render(self.text, True, self.color2) # Render the text
        self.collision = True

    def draw(self): # Draws the rectangle and the text when called
        pygame.draw.rect(SCREEN, self.color, self.button) #Draws the rectangle
        SCREEN.blit(self.rendered_text, (self.x , self.y)) # Displays the text on the button

    def change_color(self): # Changes color of the button/ rectangle when the mouse hovers over it
        if self.button.collidepoint(pygame.mouse.get_pos()): # Checks if the mouse hovers over it
            pygame.draw.rect(SCREEN, self.color3, self.button) # Draws the new rectangle
            SCREEN.blit(self.rendered_text, (self.x + 5, self.y + 5))#Blits the new Text
           
    def collide(self):
        if pygame.mouse.get_pressed()[0] == 1 and self.button.collidepoint(pygame.mouse.get_pos()) and events.type == pygame.MOUSEBUTTONDOWN: # Checks if the user is clicking on button
            if self.collision == True:
                return True
        else:
            self.collision = False
            return False
       
class Crosshair:
    def __init__(self, image): # Constructor of the class - Takes the crosshair image
        self.image = image  #stores the image as an attribute
        self.rect = self.image.get_rect() #Creates a rectangle

    def draw(self):
        self.rect.center = pygame.mouse.get_pos() #Dynamically updates the crosshair position
        SCREEN.blit(self.image, self.rect) #Draws the crosshair with respect to the rectangle object's position

crosshairimage = pygame.image.load("assets/crosshair.png")
crosshair = Crosshair(crosshairimage)


class Target:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect() # Create a rectangle in which the image is inscribed
        self.rect.topleft = (x, y) # Sets the x and y coordinates of the rectangle
        self.radius =  self.rect.height / 2

    def draw(self):
        SCREEN.blit(self.image, self.rect) #Draw the target

    def collision(self):
        mouse_position = pygame.mouse.get_pos() #Getting mouse position
        dx = self.rect.centerx - mouse_position[0] # Difference in x coordinate between the target and cursor
        dy = self.rect.centery - mouse_position[1] # Difference in y coordinate between the target and cursor
        distance = math.sqrt(dx ** 2 + dy ** 2) # The Distance between the target and cursor
        if distance <= self.radius and events.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == 1:
            #Above conditions check if target has collided with the mouse
            return True
    def generate_position(self, remaining_targets, minimum_distance):
        for remaining_target in remaining_targets: # Looping through the remaining targets
            #Distance bewteen the existing targets and the newly generated target
            dx = self.rect.centerx - remaining_target.rect.centerx #Difference in x coordinate between the new target and existing
            dy = self.rect.centery - remaining_target.rect.centery # Difference in y coordinate between the target and existing
            distance = math.sqrt(dx ** 2 + dy ** 2) #Get the distance
            if distance < minimum_distance: 
                return True
        return False
   

class Statistics:
    def __init__ (self):
        self.border = 100
        self.GRAPH_FONT = pygame.font.SysFont("Georgia", 15, True)
        self.STATISTICSBOARD_FONT = pygame.font.SysFont("Georgia", 40, True)
    def mode(self, list):
        most_frequent = 0
        for element in list:
            if list.count(element) > list.count(most_frequent): #If the current elements appears more than the the element inside of most frequent
                most_frequent = element #Set most frequent to current element
        return most_frequent
    
    def rounder(self, list):
        temporary = []
        for element in list: #Round each element inside of the list to the nearest integer and store it inside of the temporary list
            temporary.append(round(element)) 
            
        list = temporary #The temporary list is now the parameter list
        return list
           
       
    def statisticsboard(self, score_list, accuracy_list, difficulty):
        HIGH_SCORE = max(score_list) #Stores the maximum inside of the variable
        HIGH_ACCURACY = max(accuracy_list) #Stores the maximum inside of the variable
        MEAN_SCORE = round(sum(score_list) / len(score_list), 2) #Calculates the mean score & rounds to 2dp
        MEAN_ACCURACY = round(sum(accuracy_list) / len(accuracy_list), 2) #Calculates the mean accuracy & rounds to 2dp
        MODE_SCORE = self.mode(score_list) #Gets the mode element
        accuracy_list = self.rounder(accuracy_list) #Rounds all the accuracy values to the nearest integer
        MODE_ACCURACY = self.mode(accuracy_list) #Gets the mode element
       # Render all the texts
        highscore = self.STATISTICSBOARD_FONT.render(f"{HIGH_SCORE}", True, "White")
        highscore_text = self.STATISTICSBOARD_FONT.render(f"High Score", True, "White")
        highaccuracy = self.STATISTICSBOARD_FONT.render(f"{HIGH_ACCURACY}", True, "White")
        highaccuracy_text = self.STATISTICSBOARD_FONT.render(f"High Accuracy", True, "White")
        meanscore = self.STATISTICSBOARD_FONT.render(f"{MEAN_SCORE}", True, "White")
        meanscore_text = self.STATISTICSBOARD_FONT.render(f"Mean Score", True, "White")
        meanaccuracy = self.STATISTICSBOARD_FONT.render(f"{MEAN_ACCURACY}", True, "White")
        meanaccuracy_text = self.STATISTICSBOARD_FONT.render(f"Mean Accuracy", True, "White")
        modescore = self.STATISTICSBOARD_FONT.render(f"{MODE_SCORE}", True, "White")
        modescore_text = self.STATISTICSBOARD_FONT.render(f"Mode Score", True, "White")
        modeaccuracy = self.STATISTICSBOARD_FONT.render(f"{MODE_ACCURACY}", True, "White")
        modeaccuracy_text = self.STATISTICSBOARD_FONT.render(f"Mode Accuracy", True, "White")
        difficulty_text = self.STATISTICSBOARD_FONT.render(f"Difficulty : {difficulty.upper()}", True, "White")
        #Draw them
        SCREEN.blit(highscore, (480 , 300))
        SCREEN.blit(highaccuracy, (480, 400))
        SCREEN.blit(meanscore, (480 , 500))
        SCREEN.blit(meanaccuracy, (480, 600))
        SCREEN.blit(modescore, (480, 100))
        SCREEN.blit(modeaccuracy, (480, 200))
        SCREEN.blit(highscore_text, (140 , 300))
        SCREEN.blit(highaccuracy_text, (140, 400))
        SCREEN.blit(meanscore_text, (140 , 500))
        SCREEN.blit(meanaccuracy_text, (140, 600))
        SCREEN.blit(difficulty_text, (380, 50))
        SCREEN.blit(modescore_text, (140, 100))
        SCREEN.blit(modeaccuracy_text, (140, 200))
       
    def draw_graph(self,list , scoreaccuracy):
        coordinates = []
        width = SCREEN.get_width()
        height = SCREEN.get_height()
        list = self.rounder(list) #Round the elements inside of the list to the nearest integer
        highest = max(list) #Highest value from the list
        lowest = min(list) #Lowest value from the list
        listrange = highest-lowest
        # Prevent zero division error
        if listrange == 0:
            listrange = 1
        # Intervals - the ratio between the values and the coordinates
        # Borders to keep x and y distance of 100 away from the screen from both ends  
        x_interval = (width-(self.border*2))/((len(list))-1)
        y_interval = (height-(self.border*2))/listrange

        #making x and y axis
        for index in range(len(list)):
            x = self.border + x_interval*index
            y = height-self.border-((list[index]-lowest)*y_interval)

            coordinates.append([x, y])

        #draws horizontal line for x axis
        pygame.draw.line(SCREEN, (0, 0, 0), (self.border, (height-self.border)), ((width-self.border), (height-self.border)), 3)
        #draws vertical line for y axis
        pygame.draw.line(SCREEN, (0, 0, 0), (self.border, (height-self.border)), (self.border, self.border), 3)
       
        #Draws both axis and their points
        for index in range(len(coordinates)):
            #x axis
            pygame.draw.circle(SCREEN, (255, 255, 255), (self.border+(x_interval*(index)), (height-self.border)), 3)
            value_x = self.GRAPH_FONT.render(f"{index + 1}", True, "White")
            SCREEN.blit(value_x, (self.border+(x_interval*(index))-10, height-self.border))
           
            #y axis
            pygame.draw.circle(SCREEN, (255, 255, 255), (self.border, coordinates[index][1]), 3)
            value_y = self.GRAPH_FONT.render(f"{round(list[index])}", True, "White")
            SCREEN.blit(value_y, (self.border-60, -20+coordinates[index][1]))

        #Draws the actual line graph
        for index in range(len(coordinates) - 1):
            pygame.draw.line(SCREEN, (255, 0, 0), coordinates[index], coordinates[index+1], 3)

        #Draws title of the graph
        title = self.GRAPH_FONT.render(f"{scoreaccuracy} against attempts", True, "White")
        SCREEN.blit(title, (width/3,20))
        
def hit_sound():
    try:
        hit_sound = mixer.Sound("assets/hitsound.wav") # Get the waves file
        hit_sound.play() #Play the sound
    except:
        pass
   
def gameover_screen():
    global score
    global accuracy
    global shots
    SCREEN.fill((0,0, 0)) 
    SCREEN.blit(BACKGROUND, (0, 0)) #Set the background
    # Displaying all the metrics to the user.
    gameover_text = STATS_FONT.render(f"GAME OVER", True, "White")
    SCREEN.blit(gameover_text, (490, 50))
    scoretext = STATS_FONT.render(f"Score {score}", True, "White")
    SCREEN.blit(scoretext, (300, 500))
    accuracytext = STATS_FONT.render(f"Accuracy {accuracy}%", True, "White")
    SCREEN.blit(accuracytext, (300, 400))
    timetext = STATS_FONT.render(f"Session Length : 30 Seconds", True, "White")
    SCREEN.blit(timetext, (300, 300))
    back_button = Button(50, 700, "Back")
    back_button.draw()
    back_button.change_color()
    if back_button.collide(): #If user clicks back on the game over screen
        Game.state = "menu"
        score = 0
        accuracy = 0
        shots = 0
       
       
def store_stats():
    global statistics
    try:
        with open ("statistics_file.txt") as statistics_file: #Open the file as the variable statistics_file
            statistics = json.load(statistics_file) #Stores inside the statistics variable
    except:
        pass
    global game_finished
    if game_finished: #Checks if the game is finished
        #Checks if the game is at a specified difficulty
        #If yes then stores the score and accuracy to their relating lists based on the difficulty
        if Game.difficulty == "easy":
            statistics["score_easy"].append(score)
            statistics["accuracy_easy"].append(accuracy)
        elif Game.difficulty == "medium":
            statistics["score_medium"].append(score)
            statistics["accuracy_medium"].append(accuracy)
        elif Game.difficulty == "hard":
            statistics["score_hard"].append(score)
            statistics["accuracy_hard"].append(accuracy)
        with open ("statistics_file.txt", "w") as statistics_file:#Open the file as the variable statistics_file
            json.dump(statistics, statistics_file)#Write the updated data inside of the file
        game_finished = False
 


def display_stats():
    global timer
    timer = 30 - round((time.monotonic() - (START_TIME)))
    global accuracy
    if shots > 0 and timer > 0:
        accuracy = round(((score / shots) * 100), 2)
    scoretext = STATS_FONT.render(f"Score {score}", True, "White")
    SCREEN.blit(scoretext, (20, 25))
    accuracytext = STATS_FONT.render(f"Accuracy {accuracy}%", True, "White")
    SCREEN.blit(accuracytext, (1000, 35))
    timetext = STATS_FONT.render(f"Time {timer}", True, "White")
    SCREEN.blit(timetext, (500, 35))
    if timer <= 0:
        #If timer hits this number execute the following
        Game.state = "gameover_screen"
        global game_finished
        game_finished = True
 

def store_targets(): # Initialising the first 4 targets
    for target in range(0, 4):
        targets.append(Target(random.randint(0, 1000),random.randint(50, 700), TARGET_IMAGE)) #Stores the targets with random x,y attributes        

store_targets()

def manage_targets():
    global minimum_distance
    #Set the minimum distance based on the difficulty
    if Game.difficulty == "easy":
        minimum_distance = 100
    if Game.difficulty == "medium":
        minimum_distance = 230
    if Game.difficulty == "hard":
        minimum_distance = 330
    for target in targets: # Looping over the targets list
        target.draw() # Drawing all the targets inside of the list
        if target.collision(): # Checking for collision
            global score # calling the score variable declared outside of the function
            targets.pop(targets.index(target)) # If a collision has occured with a target, pop that target
            new_target = Target(random.randint(0, 1000), random.randint(80, 700), TARGET_IMAGE)
            while new_target.generate_position(targets , minimum_distance): # Create new targets until an appropriate target is found
                new_target = Target(random.randint(0, 1000), random.randint(80, 700), TARGET_IMAGE)
            targets.append(new_target)
            score = score + 1 #Increments the score by 1 for each collision.    
            if Game.sound == "on":
                hit_sound()

       
       
class GameStates: # Coordinates all the game states
    def __init__(self):
        self.state = "menu" # Sets the current state as menu which acts as the default
        self.difficulty = "easy"
        self.sound = "on"
    def mainMenu(self):
        # The code for the main menu goes here
        menufont = pygame.font.SysFont("Georgia", 80, True)
        menutext = menufont.render("Main Menu", True, "white")
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(BACKGROUND, (0, 0)) # Implementing background image
        SCREEN.blit(menutext, (400, 80)) # Displaying the menutext
        buttons = (   #All the instances of the button
            Button(540, 300, "Play"),
            Button(540, 400, "Statistics"),
            Button(540, 500, "Options"),
            Button(540, 600, "Exit")
        )
        for button in buttons:
            button.draw()
            button.change_color()
            # Change the current game state to the corresponding state if a button is pressed
            if button.collide() and button.text == "Play":
                global START_TIME
                START_TIME = time.monotonic() # Store the monotonic time the moment user presses play 
                self.state = "game"
            elif button.collide() and button.text == "Options":
                self.state = "options"
            elif button.collide() and button.text == "Exit":
                pygame.quit()
            elif button.collide() and button.text == "Statistics":
                self.state = "statistics"
        pass
    def game(self):
        SCREEN.fill((122, 122, 122))
        pygame.mouse.set_visible(False)
        manage_targets()
        crosshair.draw()
        display_stats()
    def options(self):
        SCREEN.blit(BACKGROUND, (0, 0)) # Implementing background image
        difficulty_text = STATS_FONT.render(f"Difficulty", True, "White")
        sound_text = STATS_FONT.render(f"Sound", True, "White")
        SCREEN.blit(difficulty_text, (50, 100))
        SCREEN.blit(sound_text, (50, 300))
        buttons = (   #All the instances of the button
            Button(240, 100, "Easy"),
            Button(560, 100, "Medium"),
            Button(900, 100, "Hard"),
            Button(240, 300, "Off"),
            Button(560, 300, "On"),
            Button(50, 700, "Back")
        )
               
        for button in buttons:
            #Change the colour of the button if pressed
            if self.difficulty == "easy":
                buttons[0].color = (50, 50, 50)
               
            if self.difficulty == "medium":
                buttons[1].color = (50, 50, 50)
               
            if self.difficulty == "hard":
                buttons[2].color = (50, 50, 50)
            if self.sound == "off":
                buttons[3].color = (50, 50, 50)
            if self.sound == "on":
                buttons[4].color = (50, 50, 50)
               
            button.draw()
            button.change_color()
            #Set the difficulty or sound based on the user input
            if button.collide() and button.text == "Back":
                self.state = "menu"
            if button.collide() and button.text == "Easy":
                self.difficulty = "easy"
            if button.collide() and button.text == "Medium":
                self.difficulty = "medium"
            if button.collide() and button.text == "Hard":
                self.difficulty = "hard"
            if button.collide() and button.text == "Off":
                self.sound = "off"
            if button.collide() and button.text == "On":
                self.sound = "on"            
               
           
           
           
    def statistics(self):
        try:
            #Draw the necessary texts and create buttons
            SCREEN.blit(BACKGROUND, (0, 0))
            back_button = Button(950, 400, "Back")
            graph_text = STATS_FONT.render(f"Graph" , True , "White")
            SCREEN.blit(graph_text, (950, 500))
            score_graph_button = Button(950, 700, "Score")
            accuracy_graph_button = Button(950, 600, "Accuracy")
            buttons = (
                    Button(950, 400, "Back"),
                    Button(950, 700, "Score"),
                    Button(950, 600, "Accuracy")
                )
            for button in buttons:
                button.draw()
                button.change_color()

                if button.collide() and button.text == "Back": #Take back to the menu if back is pressed
                    self.state = "menu"
                if button.collide() and button.text == "Score": #Score graph state
                    self.state = "score_graph"
                if button.collide() and button.text == "Accuracy": #Accuracy graph state
                    self.state = "accuracy_graph"
           
            with open ("statistics_file.txt") as statistics_file:
                statistics = json.load(statistics_file)
            #Pass the list of the corresponding difficulty based on the current diffiuclty
            if self.difficulty == "easy":
                StatsClass.statisticsboard(statistics["score_easy"], statistics["accuracy_easy"], self.difficulty)
               
            if self.difficulty == "medium":
                StatsClass.statisticsboard(statistics["score_medium"], statistics["accuracy_medium"], self.difficulty)
           
            if self.difficulty == "hard":
                StatsClass.statisticsboard(statistics["score_hard"], statistics["accuracy_hard"], self.difficulty)
        except:
            SCREEN.blit(BACKGROUND, (0, 0))
            text = STATS_FONT.render(f"Insufficient data for scoreboard", True, "White")
            back_button = Button(50, 700, "Back")
            back_button.draw()
            back_button.change_color()
            SCREEN.blit(text, (50, 200))
            if back_button.collide():
                self.state = "menu"
           
    def pause_screen(self):
        pygame.mouse.set_visible(True)
        global pause
        global START_TIME
        #Render and display the text
        SCREEN.blit(BACKGROUND, (0,0))
        pause_text = STATS_FONT.render(f"Paused", True, "White")
        SCREEN.blit(pause_text, (550, 100))
        buttons = (Button(550, 300, "Resume"), #Buttons inside the pause screen
                   Button(550, 400, "Quit"),
                   Button(100, 700, "Menu")
            )
        for button in buttons:
            button.draw()
            button.change_color()
            if button.collide() and button.text == "Resume": #If resume is clicked
                Game.state = "game"
                pause = False
                START_TIME = time.monotonic() - (30 - timer) # Start time is changed
            if button.collide() and button.text == "Quit": #If exit is clicked
                pygame.quit()
            if button.collide() and button.text == "Menu":#If menu is clicked
                Game.state = "menu" #Take user to menu
                pause = False
               
    def gameover_screen(self):
        pygame.mouse.set_visible(True)
        gameover_screen()
       
    def score_graph(self):
        SCREEN.blit(BACKGROUND, (0, 0))
        with open ("statistics_file.txt") as statistics_file:#Open the file
            statistics = json.load(statistics_file)#Store the data inside of the variable
        #Pass the related list to the draw_graph method based on the difficulty
        if self.difficulty == "easy":
            if len(statistics["score_easy"]) >= 5:  #Does the list contain at least 5 elements?
                StatsClass.draw_graph(statistics["score_easy"], "Score") #Draw the graph
            else: #If it does not contain at least 5 elements, draw the following texts
                text = STATS_FONT.render("Not enough data for a graph. Consider playing more sessions.", True, "White")
                SCREEN.blit(text, (100, 100))
               
           
        if self.difficulty == "medium":
            if len(statistics["score_medium"]) >= 5: #Does the list contain at least 5 elements?
                StatsClass.draw_graph(statistics["score_medium"],"Score") #Draw the graph
            else: #If it does not contain at least 5 elements, draw the following texts
                text = STATS_FONT.render("Not enough data for a graph. Consider playing more sessions.", True, "White")
                SCREEN.blit(text, (100, 100))
       
        if self.difficulty == "hard":
            if len(statistics["score_hard"]) >= 5: #Does the list contain at least 5 elements?
                StatsClass.draw_graph(statistics["score_hard"], "Score" )
            else: #If it does not contain at least 5 elements, draw the following texts
                text = STATS_FONT.render("Not enough data for a graph. Consider playing more sessions.", True, "White")
                SCREEN.blit(text, (100, 100))
               
        #A button to go back to the statistics section from the graph
        back_button = Button(20, 740, "Back")
        back_button.draw()
        back_button.change_color()
        if back_button.collide():
            self.state = "statistics"
           
    def accuracy_graph(self):
        SCREEN.blit(BACKGROUND, (0, 0))
        with open ("statistics_file.txt") as statistics_file:#Open the file
            statistics = json.load(statistics_file)#Store the data inside of the variable
        #Pass the related list to the draw_graph method based on the difficulty
        if self.difficulty == "easy":
            if len(statistics["accuracy_easy"]) >= 5:  #Does the list contain at least 5 elements?
                StatsClass.draw_graph(statistics["accuracy_easy"], "Accuracy")
            else: #If it does not contain at least 5 elements
                text = STATS_FONT.render("Not enough data for a graph. Consider playing more sessions.", True, "White")
                SCREEN.blit(text, (100, 100))
           
        if self.difficulty == "medium": #Does the list contain at least 5 elements?
            if len(statistics["accuracy_medium"]) >= 5:
                StatsClass.draw_graph(statistics["accuracy_medium"], "Accuracy")
            else: #If it does not contain at least 5 elements
                text = STATS_FONT.render("Not enough data for a graph. Consider playing more sessions.", True, "White")
                SCREEN.blit(text, (100, 100))
               
        if self.difficulty == "hard": #Does the list contain at least 5 elements?
            if len(statistics["accuracy_hard"]) >= 5:
                StatsClass.draw_graph(statistics["accuracy_hard"], "Accuracy" )
            else: #If it does not contain at least 5 elements
                text = STATS_FONT.render("Not enough data for a graph. Consider playing more sessions.", True, "White")
                SCREEN.blit(text, (100, 100))
        back_button = Button(20, 740, "Back")
        back_button.draw()
        back_button.change_color()
        if back_button.collide(): #If back is pressed take the user to the statistics section
            self.state = "statistics"


running = True
Game = GameStates()
StatsClass = Statistics()
while running:
    for events in pygame.event.get(): #Event handling
        if events.type == pygame.QUIT:
            running = False
        if events.type == pygame.MOUSEBUTTONDOWN and Game.state == "game" and pygame.mouse.get_pressed()[0] == 1: #If one single left click is pressed, register a shot at that instant
            shots = shots + 1
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_ESCAPE and Game.state == "game": #If escape is key pressed
                Game.state ="pause"
                pause = True
    #Checks what is the current state
    # Based on the current state execute its corresponding method.
    if Game.state == "menu":
        Game.mainMenu()
    elif Game.state == "game":
        Game.game()
    elif Game.state == "statistics":
        Game.statistics()
    elif Game.state == "options":
        Game.options()
    elif Game.state == "gameover_screen":
        Game.gameover_screen()
    elif Game.state == "score_graph":
        Game.score_graph()
    elif Game.state == "accuracy_graph":
        Game.accuracy_graph()
    elif Game.state == "pause":
        Game.pause_screen()
    store_stats()
    pygame.display.update()
   
pygame.quit()