# Example usage of MicroPython library for SparkFun Serial LCDs
# Written by Julien Martin, February 2022
#-----------------------------------------------------------------------------

from machine import Pin, I2C
from qwiic_serlcd_u import QwiicSerlcdU
import utime

# i2c settings
sda = Pin(0) # blue qwiic wire
scl = Pin(1) # yellow qwiic wire
i2c = I2C(0, sda=sda, scl=scl, freq=400000)

# create the lcd object with i2c driver, screen address, columns and rows numbers
lcd = QwiicSerlcdU(i2c, 0x72, 16, 2)

# lcd initialization, mandatory
lcd.begin()

# load default settings
lcd.default_settings()

# display a simple message
lcd.display("Hello world")
utime.sleep(2)

# append text
lcd.append_display(" HEY!")
utime.sleep(2)

# display lines
lcd.display_lines("This is line 1", "This is line 2")
utime.sleep(2)

# clear lcd
lcd.clear_display()

# show cursor
lcd.display("Cursor is on")
lcd.enable_cursor()
utime.sleep(2)

# hide cursor
lcd.display("Cursor is off")
lcd.disable_cursor()
utime.sleep(2)

# enable cursor blink
lcd.display("Cursor blink")
lcd.enable_cursor_blink()
utime.sleep(2)

# hide cursor
lcd.display("Cursor no blink")
lcd.disable_cursor_blink()
utime.sleep(2)

# display a scrolling message for 5 seconds
now = utime.ticks_ms()
while utime.ticks_diff(utime.ticks_ms(), now) < 5000:
    lcd.display_scrolling("This is a long scrolling message! Awesome... ", 300)

# disable system messages
lcd.disable_system_messages()

# show different contrast settings
contrasts = [80, 70, 60, 50, 40, 30, 20]
for contrast in contrasts:
    lcd.set_contrast(contrast)
    lcd.display("Contrast: " + str(contrast))
    utime.sleep(0.5)

# enable system messages
lcd.enable_system_messages()
utime.sleep(1)

# set backlight to red
lcd.display("RED")
lcd.set_rgb_backlight(255, 0, 0)
utime.sleep(1)

# set backlight to green
lcd.display("GREEN")
lcd.set_rgb_backlight(0, 255, 0)
utime.sleep(1)

# set backlight to blue
lcd.display("BLUE")
lcd.set_rgb_backlight(0, 0, 255)
utime.sleep(1)

# fade back to white backlight
lcd.display("RGB transition")
i = 254
j = 0
while i!=20:
    lcd.set_rgb_backlight(j, j, i)
    if i < 41:
        j += 1
    i -= 1

# end of demo
lcd.display("The end")
