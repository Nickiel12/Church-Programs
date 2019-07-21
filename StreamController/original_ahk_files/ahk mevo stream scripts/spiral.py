import pyautogui as pg 

def drawSpiral(duration, distance):
    pg.click(354, 283)
    while distance > 0:
        pg.dragRel(distance, 0, duration=0.2)   # move right
        distance = distance - 5
        pg.dragRel(0, distance, duration=0.2)   # move down
        pg.dragRel(-distance, 0, duration=0.2)  # move left
        distance = distance - 5
        pg.dragRel(0, -distance, duration=0.2)  # move up
