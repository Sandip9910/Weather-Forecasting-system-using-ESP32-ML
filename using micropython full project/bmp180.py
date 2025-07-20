# bmp180.py - BMP180 sensor driver for MicroPython

import time
from ustruct import unpack

class BMP180:
    def __init__(self, i2c, addr=0x77):
        self.i2c = i2c
        self.addr = addr
        self._read_calibration_data()

    def _read_signed(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return unpack('>h', data)[0]

    def _read_unsigned(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return unpack('>H', data)[0]

    def _read_calibration_data(self):
        self.AC1 = self._read_signed(0xAA)
        self.AC2 = self._read_signed(0xAC)
        self.AC3 = self._read_signed(0xAE)
        self.AC4 = self._read_unsigned(0xB0)
        self.AC5 = self._read_unsigned(0xB2)
        self.AC6 = self._read_unsigned(0xB4)
        self.B1 = self._read_signed(0xB6)
        self.B2 = self._read_signed(0xB8)
        self.MB = self._read_signed(0xBA)
        self.MC = self._read_signed(0xBC)
        self.MD = self._read_signed(0xBE)

    def _read_raw_temp(self):
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x2E')
        time.sleep_ms(5)
        return self._read_unsigned(0xF6)

    def _read_raw_pressure(self, oss=0):
        self.i2c.writeto_mem(self.addr, 0xF4, bytes([0x34 + (oss << 6)]))
        time.sleep_ms(8)
        msb = self.i2c.readfrom_mem(self.addr, 0xF6, 1)[0]
        lsb = self.i2c.readfrom_mem(self.addr, 0xF7, 1)[0]
        xlsb = self.i2c.readfrom_mem(self.addr, 0xF8, 1)[0]
        return ((msb << 16) + (lsb << 8) + xlsb) >> (8 - oss)

    @property
    def temperature(self):
        UT = self._read_raw_temp()
        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) // (X1 + self.MD)
        self.B5 = X1 + X2
        temp = ((self.B5 + 8) >> 4) / 10.0
        return temp

    @property
    def pressure(self):
        oss = 0
        UP = self._read_raw_pressure(oss)
        B6 = self.B5 - 4000
        X1 = (self.B2 * (B6 * B6 >> 12)) >> 11
        X2 = self.AC2 * B6 >> 11
        X3 = X1 + X2
        B3 = (((self.AC1 * 4 + X3) << oss) + 2) >> 2

        X1 = self.AC3 * B6 >> 13
        X2 = (self.B1 * (B6 * B6 >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = self.AC4 * (X3 + 32768) >> 15
        B7 = (UP - B3) * (50000 >> oss)
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        return p


