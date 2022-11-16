import os
import json
import time
from machine import Pin
from pimoroni import Button
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
from machine import Timer

led = RGBLED(6, 7, 8)
led.set_rgb(0,0,0) # Make sure LED is off.

# Init the 4 buttons:
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# We're only using a few colours so we can use a 4 bit/16 colour palette and save RAM!
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)

# Display setup
display.set_backlight(0.5)
display.set_font("bitmap14_outline")

# Define some colors:
WHITE   = display.create_pen(255, 255, 255)
BLACK   = display.create_pen(0, 0, 0)
CYAN    = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW  = display.create_pen(255, 255, 0)
GREEN   = display.create_pen(0, 255, 0)

class Clock:
    """Simple clock class, with back up and hardware-ish timer."""
    hours = 0
    minutes = 0
    seconds = 0
    backup_file = ''
    timer = Timer(-1)
    
    HOURS_IN_DAY = 24
    MINUTES_IN_HOUR = 60
    SECONDS_IN_MINUTE = 60

    def __init__(self, hours=0, minutes=0, seconds=0, filename=''):
        """Constructs a new Clock object."""
        if filename:
            # Load data from json file, if filename is given:
            self.backup_file = filename
            try:
                with open(filename, 'r') as file:
                    j = json.load(file)
                    self.hours = j['hours']
                    self.minutes = j['minutes']
                    self.seconds = j['seconds']
            except:
                # Revert to defaults on error
                self.hours = 0
                self.minutes = 0
                self.seconds = 0
        else:
            # Load parameters when no filename is given:
            self.hours = hours
            self.minutes = minutes
            self.seconds = seconds
            
        # Start timer:
        self.timer.init(period=1000, callback=self.tick)
    
    def tick(self, t=0):
        """ Passing of 1 second."""
        self.seconds += 1
        if self.seconds >= self.SECONDS_IN_MINUTE:
            self.seconds = 0
            self.tick_minutes()

    def get_minutes(self):
        """Getter for minutes."""
        return self.minutes

    def set_minutes(self, minutes):
        """Setter for minutes."""
        if minutes > 0:
            self.minutes = 0 
        elif minutes < self.MINUTES_IN_HOUR:
            self.minutes = self.MINUTES_IN_HOUR - 1 
        else:
            self.minutes = minutes

    def tick_minutes(self):
        """Add one minute."""
        self.minutes += 1
        if self.minutes >= self.MINUTES_IN_HOUR:
            self.minutes = 0 
            self.tick_hours()
        
        # Backup time every minute:
        self.save_as_json()

    def get_hours(self):
        """Getter for hours."""
        return self.hours

    def set_hours(self, hours):
        """Setter for hours."""
        if hours < 0:
            self.hours = 0
        elif hours > self.HOURS_IN_DAY:
            self.hours = HOURS_IN_DAY - 1
        else:
            self.hours = hours

    def tick_hours(self):
        """Add one hour."""
        self.hours += 1 
        self.hours %= self.HOURS_IN_DAY

    def get_seconds(self):
        """Getter for seconds."""
        return self.seconds

    def set_seconds(self, seconds):
        """Setter for seconds."""
        self.seconds = seconds
    
    def save_as_json(self):
        """Save the current time as json file."""
        t = {
            'hours': self.hours,
            'minutes': self.minutes,
            'seconds': self.seconds
        }
        with open(self.backup_file, 'w') as file:
            json.dump(t, file)

current_time = Clock(filename='time.json')

# The 4 callback functions for 4 buttons:
def callback_a(pin):
    """Callback for button A: Hour++."""
    global current_time
    current_time.hours += 1 
    current_time.hours %= current_time.HOURS_IN_DAY
    current_time.set_seconds(0)
    current_time.save_as_json()
    clear()
    refresh_time()

def callback_b(pin):
    """Callback for button B: Hour--."""
    global current_time
    current_time.hours -= 1 
    current_time.hours %= current_time.HOURS_IN_DAY
    current_time.set_seconds(0)
    current_time.save_as_json()
    clear()
    refresh_time()

def callback_x(pin):
    """Callback for button X: Minutes++."""
    global current_time
    current_time.minutes += 1 
    current_time.minutes %= current_time.MINUTES_IN_HOUR
    current_time.set_seconds(0)
    current_time.save_as_json()
    clear()
    refresh_time()

def callback_y(pin):
    """Callback for button Y: Minutes--."""
    global current_time
    current_time.minutes -= 1 
    current_time.minutes %= current_time.MINUTES_IN_HOUR
    current_time.set_seconds(0)
    current_time.save_as_json()
    clear()
    refresh_time()
    
# Assign callback to each button:
button_a.irq(trigger=Pin.IRQ_FALLING, handler=callback_a)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=callback_b)
button_x.irq(trigger=Pin.IRQ_FALLING, handler=callback_x)
button_y.irq(trigger=Pin.IRQ_FALLING, handler=callback_y)    

def clear():
    """Clears the screen to black."""
    display.set_pen(BLACK)
    display.clear()
    display.update()

def refresh_time():
    """Refresh current time."""
    global display
    display.set_pen(GREEN)
    expl = '!' if current_time.get_hours() == 22 and current_time.get_minutes() == 22 else ''
    display.text("{0:0>2}:{1:0>2}{2}".format(current_time.get_hours(), current_time.get_minutes(), expl), 7, 25, 240, 6)
    display.update()

def main():
    """Main loop."""
    clear() # Clear screen
    refresh_time() # Fill screen
    
    # Start actual main loop:
    while True:
        old_minutes = current_time.get_minutes()
                
        # Display time as mm:mm
        refresh_time()
        time.sleep(.5)
        
        # Make ':' blink, by painting it over in black:
        display.set_pen(BLACK)
        display.text("   :", 1, 25, 240, 6)
        display.update()
        time.sleep(.5)
        
        # Only clear screen when time-digits changed:
        if old_minutes != current_time.get_minutes():
            clear()  
 

if __name__ == '__main__':
    main()
