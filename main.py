from machine import Pin, PWM
from time import sleep
import _thread

#Global vars
status = 0
triggerBtnPush = False
cueDelayTime = 3.0

#setup pwm for the servo
pwm = PWM(Pin(15))
pwm.freq(50)

#build an empty object of ins and outs
class CueObj:
    # constructor of CueObj class
    def __init__(self):
        self.RelayOutput = None
    def SkeletonMotor(motorPos):
        print("    - run motor to position " + str(motorPos))
        pwm.duty_u16(motorPos)     
   
        
#instantiation
Cue1 = CueObj() 
Cue2 = CueObj()
Cue3 = CueObj()
Cue4 = CueObj()
Cue5 = CueObj()
Cue6 = CueObj()
Cue7 = CueObj()

#populate the objects
Cue1.RelayOutput = Pin(5, Pin.OUT) #blue wire - hole in the balcony
Cue2.RelayOutput = CueObj.SkeletonMotor
Cue3.RelayOutput = Pin(6, Pin.OUT) #white wire - skeleton arms and legs
Cue4.RelayOutput = Pin(7, Pin.OUT) #yellow wire - 
Cue5.RelayOutput = Pin(8, Pin.OUT) #black wire
Cue6.RelayOutput = Pin(9, Pin.OUT) #blue wire
Cue7.RelayOutput = Pin(10, Pin.OUT) #yellow wire
#Cue8.RelayOutput = Pin(11, Pin.OUT) #


#empty array
CueArray = [] 
#populate the array
CueArray.insert(0, [Cue1,1,0,0.25])
CueArray.insert(1, [Cue2,5000,2000,0.55])
CueArray.insert(2, [Cue3,0,0,0.25])
CueArray.insert(3, [Cue4,1,0,0.25])
CueArray.insert(4, [Cue5,1,0,0.25])
CueArray.insert(5, [Cue6,1,0,0.25])
CueArray.insert(6, [Cue7,1,0,0.25])

print("There are " + str(len(CueArray)) + " cues in the show")

def input_thread_core0():
    global status
    global triggerBtnPush
    global cueDelayTime
    
    triggerBtn = Pin(0, Pin.IN, Pin.PULL_DOWN)
    stopBtn = Pin(1, Pin.IN, Pin.PULL_DOWN)
    triggerWireles =  Pin(4, Pin.IN, Pin.PULL_DOWN)

    while True:
        if triggerBtn.value():
            #Start preformance
            #Must push the green trigger btn to start the show
            if status == 0:
                print("Start the show")
                print("Cue 1 Is Next")
                triggerBtnPush = True
                status = 1
                #turn on the skeleton              
                Cue3.RelayOutput(1)
                #set the motor to default position
                pwm.duty_u16(2000)
                #How long before aother click
                sleep(cueDelayTime)                
                continue
            
        if status > 0:
            if triggerBtn.value() or triggerWireles.value():
                triggerBtnPush = True
                print("Fire Cue " + str(status)) 
                Cue = CueArray[status - 1][0].RelayOutput
                print("  - fire 1 with value  " + str(CueArray[status - 1][1]))
                Cue(CueArray[status - 1][1])                
                #How long to hold fire
                print("  - sleep for " + str(CueArray[status - 1][3]))
                sleep(CueArray[status - 1][3])
                #fire
                print("  - fire 2 with value " + str(CueArray[status - 1][2]))
                Cue(CueArray[status - 1][2])          
                sleep(cueDelayTime)
                status += 1                
                if status > len(CueArray):
                    status = 0
                    print("Thats the end of this show, start a new show")
                    continue
                print("Cue " + str(status) + " Is Next") 
               
           
        if stopBtn.value():
            print("Emergency STOP SHOW!!!!")     
            status = -1 
            sleep(10.5)
            status = 0 
            continue
        
     
            
       
        
def status_thread_core1():
    global status
    global triggerBtnPush
    triggerLed = Pin(2, Pin.OUT)
    stopLed = Pin(3, Pin.OUT)
    
    blinkCount = 0
    while True:
        if triggerBtnPush:
            triggerBtnPush = False
            triggerLed(1)
            sleep(cueDelayTime)
            triggerLed(0)
            continue
        else:            
            if status == -1:
                #Blink the stop button fast
                #Indicats that the green btn must be pushed to start the show
                triggerLed(0)         
                stopLed.toggle()
                sleep(0.1)
                continue
            if status == 0:
                #Blink the trigger button fast
                #Indicats that the green btn must be pushed to start the show
                stopLed(0)           
                triggerLed.toggle()
                sleep(0.1)
                continue
            else:
                stopLed(1)
                #Blink the trigger button the status number of times
                #Indicats that the we are going to play cue# (green btn) or stop (red btn)
                i = 0
                while i < status:                
                    triggerLed(1)
                    sleep(0.10)
                    triggerLed(0)
                    sleep(0.10)
                    i = i + 1
                sleep(0.80)
                continue

        #This should never run  
        triggerLed(0)
        stopLed(0)


#Start the threads
second_thread = _thread.start_new_thread(status_thread_core1, ())
input_thread_core0()