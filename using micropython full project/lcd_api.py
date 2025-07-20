# lcd_api.py - Base class for HD44780-compatible LCDs

import time

class LcdApi:
    # LCD commands
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_CTRL = 0x08
    LCD_CURSOR_SHIFT = 0x10
    LCD_FUNCTION_SET = 0x20
    LCD_SET_CGRAM = 0x40
    LCD_SET_DDRAM = 0x80

    # Flags for display entry mode
    ENTRY_RIGHT = 0x00
    ENTRY_LEFT = 0x02
    ENTRY_SHIFT_INC = 0x01
    ENTRY_SHIFT_DEC = 0x00

    # Flags for display on/off control
    DISPLAY_ON = 0x04
    DISPLAY_OFF = 0x00
    CURSOR_ON = 0x02
    CURSOR_OFF = 0x00
    BLINK_ON = 0x01
    BLINK_OFF = 0x00

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.init_lcd()

    def init_lcd(self):
        raise NotImplementedError

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)

    def home(self):
        self.hal_write_command(self.LCD_HOME)
        time.sleep_ms(2)

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3F
        if cursor_y & 1:
            addr += 0x40
        self.hal_write_command(self.LCD_SET_DDRAM | addr)

    def putstr(self, string):
        for char in string:
            if char == '\n':
                self.cursor_y += 1
                self.move_to(0, self.cursor_y)
            else:
                self.hal_write_data(ord(char))
                self.cursor_x += 1
                if self.cursor_x >= self.num_columns:
                    self.cursor_x = 0
                    self.cursor_y += 1
                    self.move_to(self.cursor_x, self.cursor_y)

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError


