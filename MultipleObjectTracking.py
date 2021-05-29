from psychopy import core, visual, event, gui, data, sound
from random import randint, sample, choice, shuffle
from itertools import chain
import numpy as np
import math
import os, csv
import pandas
import time
import random

#------ Define some utility functions ------
def display_instructions(window, message, size=1):
    """Display a message onscreen and wait for a keypress.

    Arguments:
        window -- the Psychopy window to draw to
        message -- the text to display
    """
    instructions = visual.TextStim(window, text=message, color='black', font='Helvetica',
    units = 'deg', height=size, wrapWidth=50)
    instructions.draw(window)
    window.flip()
    event.waitKeys()

def display_priorities(window, left_percentage, right_percentage):
    bg = visual.Rect(window, width=1200, height=900, fillColor='gray', units='pix')
    instructions_1 = visual.TextStim(window, text=left_percentage, color='black', font='Helvetica',
    units = 'pix', wrapWidth=100, pos = (-300, 0), height = 50)
    instructions_2 = visual.TextStim(window, text=right_percentage, color='black', font='Helvetica',
    units = 'pix', wrapWidth=100, pos = (300, 0), height = 50)
    bg.draw(window)
    instructions_1.draw(window)
    instructions_2.draw(window)
    visual.Line(window, start = [0, 450], end = [0, -450], lineWidth=3, units= 'pix', lineColor = 'black').draw(window)
    window.flip()
    time.sleep(0.5)


def write_data(filename, fieldnames, data):
    """Write data to a csv file with labelled columns.

    Arguments:
        filename -- string of the file name, including the extension
        fieldnames -- a list of column names
        data -- a list of lists; each sublist is one row in the csv file,
                and should be as long as the fieldnames
    """
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        writer.writeheader()
        print(fieldnames)
        for datum in data:
            print(data)

            writer.writerow(dict([(fieldnames[i], datum[i]) for i in range(0, len(fieldnames))]))
    print('Data saved successfully.')

def get_count_response(window, question_text):
    """Accept numeric keyboard input.

    Arguments:
        window -- the window to draw to
        question_text -- a string to be displayed as the question
    """
    question = visual.TextStim(window, text=question_text, font='Helvetica',
            units = 'deg', color='black', height=1, pos=(0, 5), wrapWidth = 50)
    question.setAutoDraw(True)
    response=''
    echo = visual.TextStim(window, text=response, color="red", units='deg', height = 1.5, wrapWidth = 12)
    echo.setAutoDraw(True)
    window.flip()
    #until return pressed, listen for letter keys & add to text string
    while event.getKeys(keyList=['return'])==[] or len(response) == 0:
        letterlist=event.getKeys([str(i) for i in range(0, 10)] + ['backspace'])
        for l in letterlist:
            if l =='backspace' and len(response) > 0:
                response=response[:-1]
            else:
                response += l
        #continually redraw text onscreen until return pressed
        echo.setText(response)
        window.flip()
    echo.setAutoDraw(False)
    question.setAutoDraw(False)
    event.clearEvents()
    return int(response)

def get_afc_response(window, mouse, question_text, responses):
    """Generates an n-AFC question that a subject responds to by
    clicking a button. Returns the response.

    Arguments:
        window -- the Psychopy window to draw to
        mouse -- the mouse to monitor for input
        question_text -- a string for the question
        responses -- a list of strings, each of which is a possible answer
    """
    if len(responses) == 2:
        colors = [(229, 103, 103), (102, 151, 232)]
    else:
        colors = [(138, 125, 163)]*len(responses)
    buttonSize = (8, 4) #w, h
    separation = 10
    positions = [((i - (len(responses)/2 - .5))*separation , -5) for i in range(len(responses))]
    question = visual.TextStim(window, text=question_text, font='Helvetica', units = 'deg', height=1,
    pos=(0,1), color='black', wrapWidth = 100)
    input = [(visual.Rect(window, width=buttonSize[0], height=buttonSize[1],
                fillColor=colors[i], fillColorSpace='rgb255', pos=positions[i], units='deg'),
              visual.TextStim(window, text=responses[i], units = 'deg', height=.75, pos=positions[i], bold=True),
              responses[i]) for i in range(len(responses))]
    question.setAutoDraw(True)
    [(button[0].setAutoDraw(True), button[1].setAutoDraw(True)) for button in input]
    mouse.setVisible(1)
    window.flip()
    response = False
    while not response:
        buttons, last_click = mouse.getPressed(getTime=True)
        response = [input[i][2] for i in range(len(input)) if (mouse.isPressedIn(input[i][0]) and last_click[0])]
    question.setAutoDraw(False)
    [(button[0].setAutoDraw(False), button[1].setAutoDraw(False)) for button in input]
    mouse.setVisible(0)
    mouse.clickReset()
    return response[0]

#------ Define classes for experiment objects -------#

class motObject:
    """A class for the display objects.
    """
    def __init__(self, window, size, pos, bounds, color, shape):
        """Initialize a display object.

        Arguments:
            window -- the Psychopy window to draw to
            radius -- the radius of the object
            pos -- the starting position of the object
            bounds -- the x coordinates of the left and right edges of the display window,
                      and the y coordinates of the top and bottom edges of the display window
        """
        self.window = window
        self.pos = pos
        self.size = size
        self.color = color
        self.shape = shape

        self.speed = 6 # initial speed

        self.velocity = [self.speed*choice([-1,1]), self.speed*choice([-1,1])]
        self.bounds = [(bounds[0][0] + 0.5*self.size, bounds[0][1] - 0.5*self.size),#left + right
                        (bounds[1][0] - 0.5*self.size, bounds[1][1] + 0.5*self.size)]#top + bottom
        self.bounces = 0
        self.rest_circles = []

    def create(self):
        pass

    def insert_rest_of_circles(self, circles): #we put this function in the mot Object
        for circle in circles:
            self.rest_circles += [circle]

    def clear(self):
        """Clear the object from the screen."""
        self.obj.setAutoDraw(False)

    def checkCollisionDiscs(self):
        for rest_circles in self.rest_circles:
            if ( (self.pos[0] - rest_circles.pos[0])**2 + (self.pos[1] - rest_circles.pos[1])**2 )**0.5 <= (self.size + rest_circles.size):  # mathematical calculation for distance between two points
                #calculations for elastic collisions
                m1 = 1
                m2 = 1

                M = m1 + m2
                r1 = np.array((self.pos[0], self.pos[1]))
                v1 = np.array((self.velocity[0], self.velocity[1]))
                r2 = np.array((rest_circles.pos[0], rest_circles.pos[1]))
                v2 = np.array((rest_circles.velocity[0], rest_circles.velocity[1]))
                d = np.linalg.norm(r1 - r2)**2

                u1 = v1 - 2*m2 / M * np.dot(v1-v2, r1-r2) / d * (r1 - r2)   #velocity on x and y axis of 1 ball
                u2 = v2 - 2*m1 / M * np.dot(v2-v1, r2-r1) / d * (r2 - r1)   #velocity on x and y axis of other ball
                #update one ball
                self.velocity[0] = u1[0] #x
                self.velocity[1] = u1[1] #y
                if (self.velocity[0] == 0) and (self.velocity[1] == 1):
                    self.velocity[0] = 1
                    self.velocity[1] = 1
                self.pos[0] += self.velocity[0]
                self.pos[1] += self.velocity[1]
                self.obj.setPos((self.pos[0], self.pos[1]))
                #update other ball
                rest_circles.velocity[0] = u2[0]
                rest_circles.velocity[1] = u2[1]
                if (rest_circles.velocity[0] == 0) and (rest_circles.velocity[1] == 1):
                    rest_circles.velocity[0] = 1
                    rest_circles.velocity[1] = 1
                rest_circles.pos[0] += rest_circles.velocity[0]
                rest_circles.pos[1] += rest_circles.velocity[1]
                rest_circles.obj.setPos((rest_circles.pos[0], rest_circles.pos[1]))


    def checkCollisionBounds(self):
        """Evaluate the object's current position, change the object's velocity if it collided with a wall.
        """
        if self.pos[0] < self.bounds[0][0]: #left
            self.pos[0] = self.bounds[0][0]
            self.velocity[0] *= -1
            self.bounces += 1
        if self.pos[0] > self.bounds[0][1]:#right
            self.pos[0] = self.bounds[0][1]
            self.velocity[0] *= -1
            self.bounces += 1
        if self.pos[1] > self.bounds[1][0]: #top.   ±
            self.pos[1] = self.bounds[1][0]
            self.velocity[1] *= -1
            self.bounces += 1
        if self.pos[1] < self.bounds[1][1]: #bottom
            self.pos[1] = self.bounds[1][1]
            self.velocity[1] *= -1
            self.bounces += 1


    def move(self):
        """Check for collisions with bounds/wall, does the bouncing with wall and then checks for collision with balls and does the bouncing with balls
        update the object's position accordingly.
        """
        self.checkCollisionBounds()
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.obj.setPos((self.pos[0], self.pos[1])) #redraws on new location
        self.checkCollisionDiscs()


class motCircle(motObject):
    def __init__(self, window, size, pos, bounds, color, shape):
        super().__init__(window, size, pos, bounds, color, shape)
        self.radius = size #*.75
        self.bounds = [(bounds[0][0] + self.radius, bounds[0][1] - self.radius),
                        (bounds[1][0] - self.radius, bounds[1][1] + self.radius)]

    def create(self):
        """Create a Psychopy circle stimulus with the correct features.
        """
        self.obj = visual.Circle(self.window, self.radius, pos=self.pos, lineColor=self.color, fillColor=self.color, units='pix')
        self.obj.setAutoDraw(True)

class Trial:
    """A class to run and store attributes for a single trial."""
    def __init__(self, window, mouse, background_color, fixation_color, num_objects, object_colors, object_size, object_shapes,
    trial_dur):
        """Initializes a trial.

        Arguments:
            window -- the Psychopy window to draw to
            mouse -- the active mouse to monitor for input
            num_objects -- the number of objects to draw on the trial
            trial_dur -- the duration of the trial, in seconds
    """
        self.window = window
        self.mouse = mouse
        self.background_color = background_color
        self.fixation_color = fixation_color
        self.num_objects = num_objects
        self.objects = []
        self.object_colors = object_colors
        self.object_size = object_size
        self.object_shapes = object_shapes
        self.trial_dur = trial_dur
        self.background = visual.Rect(self.window, width=1200, height=900, fillColor=self.background_color, units='pix')
        self.bounds_left=[(-self.background.width/2, 0), (self.background.height/2, -self.background.height/2)] #left
        self.bounds_right=[(0, self.background.width/2), (self.background.height/2, -self.background.height/2)] #right
        self.fixxvert = visual.Line(self.window, start = [0, 450], end = [0, -450], lineWidth=3, units= 'pix', lineColor=self.fixation_color)
        self.fixxhoriz = visual.Line(self.window, start = [-18, 0], end = [18, 0], lineWidth=3, units= 'pix', lineColor=self.fixation_color)
        self.bounces = 0
        self.count = 0
        self.to_stay = None
        self.object_maker = {'circle': motCircle}
        self.error = None
        self.activate_reaction_time = None
        self.response_reaction_time = None
        self.score = None


    def collision(self, x, y):
        for object in self.objects:
            if ( (object.pos[0] - x)**2 + (object.pos[1] - y)**2 )**0.5 <= (2 * object.size):
                return True
        return False


    def setup(self):
        #Set up the visuals for the trial and create all the objects.
        self.background.setAutoDraw(True)
        num_objects_half = int(self.num_objects/2) #an integer spliting the total number of objects
        for i in range(num_objects_half): # LEFT: pos 1 is x coordinate and pos 2 is y coordinate
            pos_1, pos_2 = (randint(-self.background.width/2 + 2*self.object_size, 0 - 2*self.object_size), #first line refers to pos 1
                       randint(-self.background.height/2 + 2*self.object_size, self.background.height/2 - 2*self.object_size)) #and second line refers to pos 2
            while self.collision(pos_1, pos_2):  #if next ball is drawn on another then it redraws
                pos_1, pos_2 = (randint(-self.background.width/2 + 2*self.object_size, 0 - 2*self.object_size),
                           randint(-self.background.height/2 + 2*self.object_size, self.background.height/2 - 2*self.object_size))

            self.objects += [self.object_maker[self.object_shapes[i]](self.window, self.object_size,
            pos=[pos_1,pos_2], #left
            bounds=self.bounds_left, color=self.object_colors[i], shape=self.object_shapes[i])]     #actually creates objects ON THE LEFT based on the x and y positions we have found on above lines
        for i in range(num_objects_half): #RIGHT
            pos_1, pos_2 = (randint(0 + 2*self.object_size, self.background.width/2 - 2*self.object_size),
                           randint(-self.background.height/2 + 2*self.object_size, self.background.height/2 - 2*self.object_size))
            while self.collision(pos_1, pos_2):
                pos_1, pos_2 = (randint(0 + 2*self.object_size, self.background.width/2 - 2*self.object_size),
                               randint(-self.background.height/2 + 2*self.object_size, self.background.height/2 - 2*self.object_size))
            self.objects += [self.object_maker[self.object_shapes[i]](self.window, self.object_size,
            pos=[pos_1,pos_2], #left
            bounds=self.bounds_right, color=self.object_colors[i], shape=self.object_shapes[i])]


        [object.create() for object in self.objects[::-1]] # actually draws objects based on motObject create

        # Give every disc access to other discs / each object has access to all other objects
        for i, object in enumerate(self.objects):
            rest_discs = []
            for j in range(self.num_objects): # in order to insert rest
                if (i != j): # if it is not the current object, insert it in the rest_disc list
                    rest_discs += [self.objects[j]]
            object.insert_rest_of_circles(rest_discs)

        self.fixxvert.setAutoDraw(True)
        self.fixxhoriz.setAutoDraw(True)
        window.flip()

    def clear(self):
        """Clear the display."""
        self.background.setAutoDraw(False)
        self.fixxhoriz.setAutoDraw(False)
        self.fixxvert.setAutoDraw(False)

        [object.clear() for object in self.objects]
        self.window.flip()


    def check_if_click_inside_ball(self, x, y):
        position_of_mouse = event.Mouse(visible = True, win = self.window)



    def draw_arrow(self, x, y, xcirc, ycirc, unknown, line):
        temp_x = x + self.objects[self.to_stay].velocity[0] * (unknown-2)
        temp_y = y + self.objects[self.to_stay].velocity[1] * (unknown-2)

        if (temp_x > x) and (temp_y > y): # quadrants
            vert = [(x,y),(xcirc,ycirc), (temp_x+math.cos(135)*10, temp_y+math.sin(45)*10), (temp_x-math.cos(135)*10, temp_y-math.sin(45)*10), (xcirc,ycirc)]
        elif (temp_x > x) and (temp_y < y):
            vert = [(x,y),(xcirc,ycirc), (temp_x+math.cos(315)*10, temp_y+math.sin(45)*10), (temp_x-math.cos(315)*10, temp_y-math.sin(45)*10), (xcirc,ycirc)] # katw dexia je panw aristera
        elif (temp_x < x) and (temp_y > y):
            vert = [(x,y),(xcirc,ycirc), (temp_x+math.cos(315)*10, temp_y+math.sin(45)*10), (temp_x-math.cos(315)*10, temp_y-math.sin(45)*10), (xcirc,ycirc)]
        else:
            vert = [(x,y),(xcirc,ycirc), (temp_x+math.cos(135)*10, temp_y+math.sin(45)*10), (temp_x-math.cos(135)*10, temp_y-math.sin(45)*10), (xcirc,ycirc)]
        arrow = visual.ShapeStim(self.window, vertices=vert, fillColor='green', size=.5, lineColor='green')
        arrow.units = 'pix'
        # while mouse.getPressed()[0] == False: # with first click, arrow appears
        #     pass
        arrow.setAutoDraw(True)
        self.window.flip()

        core.wait(2)
        arrow.setAutoDraw(False)
        line.setAutoDraw(False)

    def calculate_distance(self, x1, x2, y1, y2):
        distance = ((x1-x2)**2+(y1-y2)**2)**0.5
        return distance


    def find_angle(self, mouse_x, mouse_y, xcirc, ycirc): # cosine rule
        centre_x = self.objects[self.to_stay].pos[0]
        centre_y = self.objects[self.to_stay].pos[1]
        distance_1 = self.calculate_distance(mouse_x, centre_x, mouse_y,centre_y)
        distance_2 = self.calculate_distance(mouse_x, xcirc, mouse_y, ycirc)
        distance_3 = self.calculate_distance(centre_x, xcirc, centre_y, ycirc)
        theta = math.acos((distance_1**2 +distance_3**2 - distance_2**2)/(2*distance_1*distance_3))
        self.error = math.degrees(theta)
        print(self.error)
        if (self.error <= 20):
            self.score = 1
        else:
            self.score = 0



    def create_arrow(self, x, y):
        position_of_mouse = event.Mouse(visible = True, newPos = [x,y], win = self.window)
        x = x*2
        y = y*2

        # while mouse.getPressed()[0] == False: # with first click, arrow appears
        #     pass

        t0 = time.time()
        while True:
            if mouse.getPressed()[0] == True:
                pos_mouse = mouse.getPos()
                if ((pos_mouse[0] - x/2)**2 + (pos_mouse[1] - y/2)**2)**0.5 <= 50: # first response
                    t1 = time.time()
                    break
        ## Apparance of a moving arrow ###
        reaction_time_1 = t1 - t0
        self.activate_reaction_time = reaction_time_1

        #print(event.getKeys(keyList = 'space'))
        vert = [(x, y), (pos_mouse[0]*2, pos_mouse[1]*2)]
        line = visual.ShapeStim(self.window, vertices=vert, fillColor='white', size=.5, lineColor='white', lineWidth = 3)

        event.clearEvents()
        while len(event.getKeys(keyList = 'space')) == 0: # with second click, feedback appears
            pos_mouse = mouse.getPos()
            vert = [(x, y), (pos_mouse[0]*2, pos_mouse[1]*2)]
            line = visual.ShapeStim(self.window, vertices=vert, fillColor='white', size=.5, lineColor='white', lineWidth = 3)
            line.setAutoDraw(True)
            self.window.flip()
            line.setAutoDraw(False)
        line.setAutoDraw(True)
        t2 = time.time()
        reaction_time_2 = t2 - t1
        self.response_reaction_time = reaction_time_2

        ### End of the moving arrow ###

        ### SHOW FEEDBACK ###
        end_x = x / 2
        end_y = y / 2
        next_position_x = end_x + self.objects[self.to_stay].velocity[0]
        next_position_y = end_y + self.objects[self.to_stay].velocity[1]

        dist = math.sqrt((end_x-next_position_x)**2+(end_y-next_position_y)**2)
        unknown = 50 / dist # 8.8 RADIUS

        xcirc = end_x + self.objects[self.to_stay].velocity[0] * unknown
        ycirc = end_y + self.objects[self.to_stay].velocity[1] * unknown

        self.draw_arrow(x, y, xcirc*2, ycirc*2, unknown, line)
        ### END SHOWING FEEDBACK ###

        self.find_angle(pos_mouse[0], pos_mouse[1], xcirc, ycirc)

    def remove_smart(self, left, right): # if keep in left side, give 0, len(self.objects)/2. If keep in right side, give len(self.objects)/2, len(self.objects)
        self.to_stay = random.randrange(left, right) #creates a number between left and right (without right included) (i.e. stays left 0-3 (0,1,2) stays right 3-6 (3,4,5))
        for i, object in enumerate(self.objects):
            if (i != self.to_stay):
                object.clear()


    def clear_except_one(self, left_percentage, questioned):
        # Assume first len/2 objects are left and rest are right

        if left_percentage == 50:
            if questioned == 51:
                self.remove_smart(0, len(self.objects)/2) #stays on left
            else:
                self.remove_smart(len(self.objects)/2, len(self.objects)) #stays on right
        elif left_percentage == questioned: # stay on left
            self.remove_smart(0, len(self.objects)/2)
        else:
            self.remove_smart(len(self.objects)/2, len(self.objects))
        last_ball = self.objects[self.to_stay]
        #print(last_ball.pos[0])
        #print(last_ball.pos[1])
        self.window.flip()
        self.create_arrow(last_ball.pos[0], last_ball.pos[1])


    def run(self):
        """Start the animation for the trial."""
        self.timer = core.Clock()
        while self.timer.getTime() < self.trial_dur:
            [object.move() for object in self.objects]
            self.window.flip()

    def get_data(self):
        """Assemble the data for this trial and return it.

        Returns a list of the attended color, the number of objects, the color of the
        attended set, the color of the ignored set, the number of times the attended objects bounced,
        the subject's reported count, and, if it was an inattentional blindness trial, the shape of the
        ib object, the color of the ib object, whether the subject reported seeing it, what color they
        reported it being, and what shape they reported it being.
        """
        #if self.is_ib:
            #self.bounces = sum([object.bounces for object in self.objects[:-1] if object.color == self.attended_color])
        #self.bounces = sum([object.bounces for object in self.objects if object.color == self.attended_color])




# ------ Set up the experiment parameters -------
# Execution starts from here

set_up_trial = pandas.read_excel("Set_Up_Trial.xlsx", header=None) # CSV file witd index+type+prob. for left, prob. for right, what stays
set_up_trial.columns = ["Number", "Type", "Left", "Right", "Questioned"]

# Shuffle the excel rows between phases
np.random.shuffle(set_up_trial[:10].values)
np.random.shuffle(set_up_trial[10:40].values)
np.random.shuffle(set_up_trial[40:70].values)
np.random.shuffle(set_up_trial[70:100].values)
np.random.shuffle(set_up_trial[100:130].values)
np.random.shuffle(set_up_trial[-30:].values)

expInfo = {'SubjID': ''}
expInfoDlg = gui.DlgFromDict(dictionary = expInfo, title='Experiment Log')
expInfo['Date'] = data.getDateStr()

window = visual.Window([1200, 900],  units = 'pix', allowGUI=True, monitor='testMonitor', color='white', fullscr=True)
mouse = event.Mouse(visible=False)
background_color = 'gray'
fixation_color = 'black'
num_objects = 8
object_colors = ['black']*num_objects
object_size = 50 # radius
object_shapes = ['circle']*num_objects
trial_duration = randint(6,8)
#trial_order = set_up_trial[0:5] # uncommend this line to sub-sample the number of trials
fieldnames = ['Number', 'Type', 'Left', 'Right', 'Questioned', 'ERROR_D', 'ACTIVATE_RT', 'RESPONSE_RT', 'SCORE']
filename = expInfo['SubjID']+'_'+expInfo['Date']+'.csv'

# ------ Run the experiment -------

#run each trial



display_instructions(window, "Please wait until the experimenter has cleared you to start. " \
"Keep your eyes on the centre. "\
"Press any key when you're ready to start.")

total_score = 0

#trial_data = [attended_color, attended_shape]
trial_data = [[]]
for i, current in trial_order.iterrows(): #current: entire row for each trial in trial_order / FOR LOOP FOR WHOLE TRIAL
    if (i == 10) or (i == 40) or (i == 70) or (i == 100) or (i == 130): # this is not trial numbered 10 it is the 10th trial (having done 10)
        display_instructions(window, "You can take a break. "\
        "Press any key when you're ready to start again. Your total score is:" + str(total_score*100/i) + "%")

    display_priorities(window, current['Left'], current['Right']) # take each cell from left and right columns of the current

    trial = Trial(window, mouse, background_color, fixation_color, num_objects, object_colors, object_size, object_shapes,
    trial_duration)

    key = event.waitKeys() # waits any key to continue
    if key[0] == 'escape':  # escape to end the program
        core.quit()

    trial.setup()
    core.wait(1)

    trial.run()
    trial.clear_except_one(current['Left'], current['Questioned'])
    trial.clear()

    if (trial.score == 1):
        total_score += 1
    trial_data.append([current['Number'], current['Type'], current['Left'], current['Right'], current['Questioned'], trial.error, trial.activate_reaction_time, trial.response_reaction_time, trial.score])
del(trial_data[0])

#output data
with open(filename, 'w', newline = '') as csvfile:
    csv_writer = csv.writer(csvfile)
    for i, trial in enumerate(trial_data):
        csv_writer.writerow([otinane for otinane in trial])

#write_data(filename, fieldnames, [trial_data])

display_instructions(window, "Thank you for your participation. Your response has been recorded.")

window.close()
core.quit()
