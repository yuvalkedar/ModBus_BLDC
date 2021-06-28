from time import sleep
from pymodbus.client.sync import ModbusSerialClient # pip install modbus

CONTROLLER_ID = 1
CONTROLLER_PORT = '/dev/cu.usbserial-0001'

client=ModbusSerialClient('rtu', port=CONTROLLER_PORT, baudrate=9600, stopbits=2)

# set P000 to 0x18 panel control mode and 485 communication control mode

def swap_reg(val):
    return (val >> 8) | ((val & 255) << 8)

def read_reg(address):
    return swap_reg(client.read_holding_registers(address, unit=CONTROLLER_ID).registers[0])

def write_reg(address, value):
    client.write_register(address, swap_reg(value), unit=CONTROLLER_ID)

def set_speed(rpm=2000):
    # must manually set P010 to 1
    write_reg(0x8005, rpm)

def set_motor(en=0, dir=0, stop=0):
    # 0x04xx = 4 poles pairs for 8 poles motor
    # 0xxx18 = NW1 + NW are set to 1
    val = 0x0418 | en * 0x01 | dir * 0x02 | stop * 0x04
    write_reg(0x8000, val)

def set_acc_dec(acc_s=0, dec_s=0):
    # acc_s, dec_s in seconds (0-25.5)
    acc_s *= 10
    dec_s *= 10
    val = acc_s | (dec_s << 8)
    write_reg(0x8003, val)

def get_status():
    return read_reg(0x801b)

def get_speed5():
    # retuens speed (rpm) / 5
    return read_reg(0x8018)

def get_analog():
    # sv pin input from GND to 5V
    return read_reg(0x801a) >> 8

def print_status():
    status = get_status()
    for i, e in enumerate(('stall', 'over current', 'hall abnormality', 'low bus voltage', 'over bus voltage', 'peak current alarm', 'temperature alarm')):
        if (status >> i) & 1:
            print(e)


set_motor(1)
sleep(1)
set_speed(1000)
sleep(1)
set_motor(1, 1) # reverse
sleep(1)
set_motor(0)
