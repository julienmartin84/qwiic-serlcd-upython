# MicroPython library for I2C control of the SparkFun Serial LCDs (QWIIC)
# Written by Julien Martin, February 2022
#-----------------------------------------------------------------------------
#
# Compatible with:
#   SparkFun 16x2 SerLCD - RGB Backlight (Qwiic) https://www.sparkfun.com/products/16396
#   SparkFun 16x2 SerLCD - RGB Text (Qwiic) https://www.sparkfun.com/products/16397
#   SparkFun 20x4 SerLCD - RGB Backlight (Qwiic) https://www.sparkfun.com/products/16398
#
# More information on qwiic is at https://www.sparkfun.com/qwiic
#-----------------------------------------------------------------------------
# This is a port of the SparkFun existing Python library
#

import utime

MAX_ROWS = 4
MAX_COLUMNS = 20

# OpenLCD command characters
SPECIAL_COMMAND = 254  # used to send a special command
SETTING_COMMAND = 0x7C # used to change settings: baud, lines, width, backlight, splash, etc

# OpenLCD commands
CLEAR_COMMAND = 0x2D # used to clear and home the display
CONTRAST_COMMAND = 0x18 # used to change the contrast setting
ADDRESS_COMMAND = 0x19 # used to change the i2c address
SET_RGB_COMMAND = 0x2B # used to set backlight RGB value
ENABLE_SYSTEM_MESSAGE_DISPLAY = 0x2E  # used to enable system messages being displayed
DISABLE_SYSTEM_MESSAGE_DISPLAY = 0x2F # used to disable system messages being displayed
ENABLE_SPLASH_DISPLAY = 0x30 # used to enable splash screen at power on
DISABLE_SPLASH_DISPLAY = 0x31 # used to disable splash screen at power on
SAVE_CURRENT_DISPLAY_AS_SPLASH = 0x0A # used to save current text on display as splash

# Special commands
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_SETDDRAMADDR = 0x80

# Flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

class QwiicSerlcdU:
    
    _displayControl = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
    _displayMode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
    _defaultValue = 20
    
    # Constructor parameters
    # i2c: i2c driver object of the lcd
    # i2c_address: the i2c address of the lcd
    # lcd_columns: number of columns of the lcd
    # lcd_rows: number of rows of the lcd
    def __init__(self, i2c, i2c_address, lcd_columns, lcd_rows):
        self.i2c = i2c
        self.address = i2c_address
        self.lcd_columns = lcd_columns
        self.lcd_rows = lcd_rows
        self.last_refreshed = utime.ticks_ms()
        self.index = 0
    
    # Initialize the operation of the SerLCD module
    # Also wait 1 second for i2c to be ready before doing anything
    def begin(self):
        # wait for i2c initialization
        utime.sleep(1)
        result0 = self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
        result1 = self.send_commands([SPECIAL_COMMAND, LCD_ENTRYMODESET | self._displayMode])
        result2 = self.clear_display()
        return (bool(result0) & bool(result1) & bool(result2))
    
    # Set default settings
    def default_settings(self):
        # disable display and system messages to speed up settings
        self.disable_display()
        self.disable_system_messages()
        # set default contrast and backlight, enable splash and clear display
        self.set_contrast(self._defaultValue)
        self.set_rgb_backlight(self._defaultValue, self._defaultValue, self._defaultValue)
        self.enable_splash()
        self.clear_display()
        # enable display and system messages
        self.enable_system_messages()
        self.enable_display()
    
    # Internal I2C function to send block of commands to the screen
    # Do not use
    def send_commands(self, block):
        result = self.i2c.writeto(self.address, bytearray(block))
        utime.sleep(0.01)
        return result
    
    # Internal I2C function to send text to the screen
    # Do not use
    def send_text(self, text):
        result = self.i2c.writeto(self.address, text)
        utime.sleep(0.01)
        return result
    
    # Display a message on the screen
    # Screen is previously cleared and cursor position reseted
    def display(self, message):
        self.send_commands([SETTING_COMMAND, CLEAR_COMMAND])
        self.send_text(message[0:self.lcd_columns*self.lcd_rows])
    
    # Display a message without clearing the screen
    # Cursor position is also not reseted, we use last cursor position
    def append_display(self, message):
        return self.send_text(message)
    
    # Display the 2 given lines on the screen
    # Lines are truncated to fit the columns of the screen
    def display_lines(self, first_line, second_line):
        line_1 = first_line[0:self.lcd_columns]
        line_2 = second_line[0:self.lcd_columns]
        for i in range(len(line_1), self.lcd_columns):
            line_1 += " "
        self.display(line_1 + line_2)
    
    # Display a scrolling message. Duration is in milliseconds
    def display_scrolling(self, message, duration):
        if utime.ticks_diff(utime.ticks_ms(), self.last_refreshed) > duration:
            visible_message = message[self.index:self.lcd_columns*self.lcd_rows+self.index]
            if self.lcd_columns*self.lcd_rows+self.index > len(message):
                visible_message += message[0:self.lcd_columns*self.lcd_rows+self.index-len(message)]
            self.display(visible_message)
            self.last_refreshed = utime.ticks_ms()
            self.index += 1
            if self.index > len(message):
                self.index = 0
    
    # Clear the content of the screen and reset the cursor position
    def clear_display(self):
        return self.send_commands([SETTING_COMMAND, CLEAR_COMMAND])
    
    # Set the contrast to a new value
    # Value from 0 to 255
    def set_contrast(self, contrast):
        return self.send_commands([SETTING_COMMAND, CONTRAST_COMMAND, contrast])
    
    # Set RGB backlight color
    # RGB values from 0 to 255
    def set_rgb_backlight(self, r, g, b):
        return self.send_commands([SETTING_COMMAND, SET_RGB_COMMAND, r, g, b])
    
    # Set the cursor position to a particular column and row
    def set_cursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        row = max(0, row)
        row = min(row, (MAX_ROWS - 1))
        return self.send_commands([SPECIAL_COMMAND, LCD_SETDDRAMADDR | (col + row_offsets[row])])
    
    # Turn the underline cursor on
    def enable_cursor(self):
        self._displayControl |= LCD_CURSORON
        return self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
    
    # Turn the underline cursor off
    def disable_cursor(self):
        self._displayControl &= ~LCD_CURSORON
        return self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
    
    # Turn the blink cursor on
    def enable_cursor_blink(self):
        self._displayControl |= LCD_BLINKON
        return self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
    
    # Turn the blink cursor off
    def disable_cursor_blink(self):
        self._displayControl &= ~LCD_BLINKON
        return self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
    
    # Show display content
    def enable_display(self):
        self._displayControl |= LCD_DISPLAYON
        return self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
    
    # Hide display content
    def disable_display(self):
        self._displayControl &= ~LCD_DISPLAYON
        return self.send_commands([SPECIAL_COMMAND, LCD_DISPLAYCONTROL | self._displayControl])
    
    # Enable system messages like 'Contrast: 5'
    def enable_system_messages(self):
        return self.send_commands([SETTING_COMMAND, ENABLE_SYSTEM_MESSAGE_DISPLAY])
    
    # Disable system messages like 'Contrast: 5'
    def disable_system_messages(self):
        return self.send_commands([SETTING_COMMAND, DISABLE_SYSTEM_MESSAGE_DISPLAY])
    
    # Enable splash screen at power on
    def enable_splash(self):
        return self.send_commands([SETTING_COMMAND, ENABLE_SPLASH_DISPLAY])
    
    # Disable splash screen at power on
    def disable_splash(self):
        return self.send_commands([SETTING_COMMAND, DISABLE_SPLASH_DISPLAY])
    
    # Saves whatever is currently being displayed into EEPROM
    # This will be displayed at next power on as the splash screen
    def save_splash(self):
        return self.send_commands([SETTING_COMMAND, SAVE_CURRENT_DISPLAY_AS_SPLASH])
    
    # Change the i2c address of the display, 0x72 is the default. This change is persistent
    # If anything goes wrong you may need to do a hardware reset to unbrick the display
    def set_address(self, new_address):
        result = self.send_commands([SETTING_COMMAND, ADDRESS_COMMAND, new_address])
        utime.sleep(0.05)
        self.address = new_address # update our own address
        return result
