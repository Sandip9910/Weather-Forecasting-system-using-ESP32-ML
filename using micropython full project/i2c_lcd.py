from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

class I2cLcd(LcdApi):
    MASK_RS = 0x01
    MASK_RW = 0x02
    MASK_E = 0x04
    MASK_BACKLIGHT = 0x08

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = self.MASK_BACKLIGHT
        self._write_init_nibble(0x03)
        sleep_ms(5)
        self._write_init_nibble(0x03)
        sleep_ms(1)
        self._write_init_nibble(0x03)
        self._write_init_nibble(0x02)

        super().__init__(num_lines, num_columns)

    def init_lcd(self):
        self.send_command(0x28)  # 4-bit mode, 2 line, 5x8 font
        self.send_command(0x0C)  # Display ON, Cursor OFF, Blink OFF
        self.send_command(0x06)  # Increment cursor
        self.clear()

    def _write_byte(self, data):
        self.i2c.writeto(self.i2c_addr, bytes([data | self.backlight]))

    def _pulse_enable(self, data):
        self._write_byte(data | self.MASK_E)
        sleep_ms(1)
        self._write_byte(data & ~self.MASK_E)
        sleep_ms(1)

    def _write_init_nibble(self, nibble):
        data = nibble << 4
        self._pulse_enable(data)

    def send_command(self, cmd):
        self._write4bits(cmd & 0xF0)
        self._write4bits((cmd << 4) & 0xF0)

    def send_data(self, data):
        self._write4bits(data & 0xF0, self.MASK_RS)
        self._write4bits((data << 4) & 0xF0, self.MASK_RS)

    def _write4bits(self, data, mode=0):
        self._pulse_enable(data | mode)

    def hal_write_command(self, cmd):
        self.send_command(cmd)

    def hal_write_data(self, data):
        self.send_data(data)


