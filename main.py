import time
from pimoroni import Button
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4

led = RGBLED(6, 7, 8)
led.set_rgb(0,0,0) # LED off.

# We're only using a few colours so we can use a 4 bit/16 colour palette and save RAM!
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)

display.set_backlight(0.5)
display.set_font("bitmap14_outline")

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

WHITE   = display.create_pen(255, 255, 255)
BLACK   = display.create_pen(0, 0, 0)
CYAN    = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW  = display.create_pen(255, 255, 0)
GREEN   = display.create_pen(0, 255, 0)


# sets up a handy function we can call to clear the screen
def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()

# set up
clear()

hours = 13
minutes = 41
seconds = 30

def update_time():
    global hours
    global minutes
    global seconds
    
    seconds += 1
    if seconds >= 60:
        seconds = 0
        minutes += 1
        if minutes >= 60:
            minutes = 0
            hours += 1
            hours %= 24

while True:
    old_minutes = minutes
    update_time()
    if old_minutes != minutes:
        clear()  # Only clear screen when necessary
    
    # Display time as mm:mm
    display.set_pen(GREEN)
    display.text("{0:0>2}:{1:0>2}".format(hours, minutes), 7, 25, 240, 6)
    display.update()
    time.sleep(.5)
    
    # Make ':' blink
    display.set_pen(BLACK)
    display.text("   :", 1, 25, 240, 6)
    display.update()
    time.sleep(.5)  
    
    # Check buttons: #TODO: use callbacks
    if button_a.read():
        hours += 1
        hours %= 24
    elif button_b.read():
        hours -= 1
        hours %= 24
    elif button_x.read():
        minutes += 1
        minutes %= 60
    elif button_y.read():
        minutes -= 1
        minutes %= 24
