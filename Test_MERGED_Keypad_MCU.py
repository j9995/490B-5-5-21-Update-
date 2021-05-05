import RPi.GPIO as GPIO    
import serial
import random
from time import sleep
GPIO.setmode(GPIO.BCM)          # configure GPIO numbering
GPIO.setwarnings(False)

# Global Var
r1 = 0
count = 0

#set gpio for key pad
COL = [18,23,24,25]
ROW = [4,17,27,22]
GPIO.setup(8, GPIO.OUT)

for j in range(4):
    GPIO.setup(COL[j], GPIO.OUT)
    GPIO.output(COL[j], 1)
for i in range(4):
    GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

# set up class for key pad
def check_keypad(length):

    COL = [18,23,24,25]
    ROW = [4,17,27,22]

    MATRIX = [["1","2","3","A"],
              ["4","5","6","B"],
              ["7","8","9","C"],
              ["*","0","#","D"]]
    result = ""
    while(True):
        for j in range(4):
            GPIO.output(COL[j], 0)

            for i in range(4):
                if GPIO.input(ROW[i]) == 0:
                    sleep(0.02)
                    result = result + MATRIX[i][j]
                    print(result)
                    while(GPIO.input(ROW[i]) == 0):
                        sleep(0.02)

            GPIO.output(COL[j], 1)
            if len(result) >= length:
                return result
                
# Function to generate passcode!
def rcode():
    global r1
    r1 = random.randint(100,999)
    print(r1)


print("Your specialized code is\n")
rcode()
port = serial.Serial ("/dev/serial0", 9600)
GPIO.output(8,True) # Turn on electromagnet 

electro = 0

while True:
    ######################################################################
    # Get welcome message from MCU1
    print("Waiting for response from MCU2")
    r_data = port.readline(1)
    sleep(0.3)
    data_left = port.inWaiting()
    r_data += port.readline(data_left)
    print(r_data)
    ######################################################################
    
    ######################################################################
    # Main Menu
    print("Press 1 to expand or retract your device")
    print("Press 2 to open or close your device's panel")
    print("Press 3 to control electromagnet")
    print("or Press # to use the barcode scanner")
    function = check_keypad(1)
    while ((function != "1") and (function != "2") and (function != "3") and (function != "#")):
            print("Enter only a 1, 2, or #: ")
            function = check_keypad(1)
    ######################################################################
    
    if (function == "#"):
        u = 'bar'
        b = bytes(u,'ascii')
        port.write(b)
    
    elif (function == "1"):
        u = '1'
        b = bytes(u,'ascii')
        port.write(b)
        
        ######################################################################
        # Functionality Menu 
        print('Press A to move forward or B to move backward ')
        result1 = check_keypad(1) # Enter only one character
        while ((result1 != "A") and (result1 != "B")):
            print("Enter only an A or B: ")
            result1 = check_keypad(1)
        ######################################################################
      
        if (result1 == "A"):
            u = 'A'
            b = bytes(u,'ascii')
            port.write(b)
            #print(b) # debug
        else:
            u = 'B'
            b = bytes(u,'ascii')
            port.write(b)
            #print(b) # debug
      
    elif (function == "2"):
        u = '2'
        b = bytes(u,'ascii')
        port.write(b)
        
        ######################################################################
        # Passcode Menu
        print("Please enter your passcode to unlock and open")
        print("or enter 000 to close ")
        in_code = check_keypad(3)
        result2 = int(in_code, 10) # Convert to int base 10
        while ((result2 != r1) and (in_code != "000") and (count < 11)):
            print("Incorrect passcode")
            print("Please enter your passcode to unlock and open")
            print("or enter 000 to close ")
            in_code = check_keypad(1)
            result2 = int(in_code, 10)
            
            count = count + 1
            if (count == 10):
                print("You have entered the code incorrectly too many times and are momentarily locked out!\n ")
                sleep(1000)
                count = 0
        ######################################################################
        
        # Code matched open door
        if (result2 == r1): 
            GPIO.output(8, False) # Turn off electromagnet 
            u = 'o'
            b = bytes(u,'ascii')
            port.write(b)
    
        # close door
        elif (in_code == "000"):
            GPIO.output(8, True) # Turn it back on
            u = 'c'
            b = bytes(u,'ascii')
            port.write(b)
       
        else:
            print("Uh-oh")
            
    elif (function == "3"):
        # Turn electro off
        if (electro == 1):
            GPIO.output(8,False)
            print("magnet off")
            u = 'e'
            b = bytes(u,'ascii')
            port.write(b)
            electro = 0
        # Turn electro on
        else:
            GPIO.output(8,True)
            print("magnet on")
            u = 'e'
            b = bytes(u,'ascii')
            port.write(b)
            electro = 1
        
    
