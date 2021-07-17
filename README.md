
# MultipleObjectTracking

Multiple Object Trajectory tracking task on Python, using the <a href=https://www.psychopy.org/> Psychopy's </a> open source library. <br>

This code was created for the research purposes of a psychology PhD student, Veronica Hadjipanayi, at the University of Bristol. <br>

<p align="center" width="100%">
    <img width="49%" src="https://user-images.githubusercontent.com/31161911/120081947-13955000-c0b8-11eb-8c1c-4789b98460e4.gif"> 
    <img width="49%" src="https://user-images.githubusercontent.com/31161911/120081950-16904080-c0b8-11eb-8ecc-1611df15c9a2.gif"> 
</p>


## Task Details

Participants are asked to track the moving targets around and then report the direction towards which one of these targets was moving. <br>

Numbers presented at the beginning of every trial represent the probability of the queried target appearing in each screen region respectively. <br>

The white line represents the participant's resonce. Participants are provided with feedback regarding the actual correct direction of the target through a green arrow which appears after participant's responce. <br>

Error is calculated in degrees as the difference between the correct direction of the target and that specified by the participant. <br>

At the end of each block a score is calculated giving one point to the participant whenever having an error within 20 degrees of the correct direction. <br>

A CSV file is created as an output that includes the necessary information for every trial. <br>


