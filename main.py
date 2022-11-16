import time
from machine import Pin
from pimoroni import Button
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4

led = RGBLED(6, 7, 8)
led.set_rgb(0,0,0) # LED off.

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# We're only using a few colours so we can use a 4 bit/16 colour palette and save RAM!
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)

display.set_backlight(0.5)
display.set_font("bitmap14_outline")

WHITE   = display.create_pen(255, 255, 255)
BLACK   = display.create_pen(0, 0, 0)
CYAN    = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW  = display.create_pen(255, 255, 0)
GREEN   = display.create_pen(0, 255, 0)

class Clock:
    hours = 0
    minutes = 0
    seconds = 0
    
    HOURS_IN_DAY = 24
    MINUTES_IN_HOUR = 60
    SECONDS_IN_MINUTE = 60

    def __init__(self, hours=0, minutes=0, seconds=0):
        """Constructs a new Clock object."""
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def tick(self):
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

current_time = Clock(14, 22)

def callback_a(pin):
    """Callback for button A: Hour++."""
    global current_time
    current_time.hours += 1 
    current_time.hours %= current_time.HOURS_IN_DAY
    current_time.set_seconds(0)
    clear()
    refresh_time()

def callback_b(pin):
    """Callback for button B: Hour--."""
    global current_time
    current_time.hours -= 1 
    current_time.hours %= current_time.HOURS_IN_DAY
    current_time.set_seconds(0)
    clear()
    refresh_time()

def callback_x(pin):
    """Callback for button X: Minutes++."""
    global current_time
    current_time.minutes += 1 
    current_time.minutes %= current_time.MINUTES_IN_HOUR
    current_time.set_seconds(0)
    clear()
    refresh_time()

def callback_y(pin):
    """Callback for button Y: Minutes--."""
    global current_time
    current_time.minutes -= 1 
    current_time.minutes %= current_time.MINUTES_IN_HOUR
    current_time.set_seconds(0)
    clear()
    refresh_time()
    
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
    display.text("{0:0>2}:{1:0>2}".format(current_time.get_hours(), current_time.get_minutes()), 7, 25, 240, 6)
    display.update()

def main():
    clear() # Clear screen
    
    # Run main loop:
    while True:
        old_minutes = current_time.get_minutes()
        current_time.tick()
        if old_minutes != current_time.get_minutes():
            clear()  # Only clear screen when necessary

        # Display time as mm:mm
        display.set_pen(GREEN)
        expl = '!' if current_time.get_hours() == 22 and current_time.get_minutes() == 22 else ''
        display.text("{0:0>2}:{1:0>2}{2}".format(current_time.get_hours(), current_time.get_minutes(), expl), 7, 25, 240, 6)
        display.update()
        time.sleep(.5)
        
        # Make ':' blink
        display.set_pen(BLACK)
        display.text("   :", 1, 25, 240, 6)
        display.update()
        time.sleep(.5)  
 
if __name__ == '__main__':
    main()
