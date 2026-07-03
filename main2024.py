from machine import Pin, PWM
from time import sleep
import _thread

#Global vars
status = 0
triggerBtnPush = False
cueDelayTime = 1.25

##setup pwm for the servo
pwm = PWM(Pin(15))
pwm.freq(50)

#build an empty object of ins and outs
class CueObj:
    # constructor of CueObj class
    def __init__(self):
        self.RelayOutput = None  
        
#instantiation
Cue1 = CueObj() 
Cue2 = CueObj()
Cue3 = CueObj()

#populate the objects
Cue1.RelayOutput = Pin(5, Pin.OUT) #blue wire - Jack gets shot
Cue2.RelayOutput = Pin(6, Pin.OUT) #white wire - Roxie gets shot
Cue3.RelayOutput = Pin(7, Pin.OUT) #yellow wire - Boone shoots and misses

#empty array
CueArray = [] 
#populate the array
CueArray.insert(1,[Cue1,1,0,0.25,"Jack gets shot"])
CueArray.insert(2,[Cue2,1,0,0.25,"Roxie gets shot"])
CueArray.insert(3,[Cue3,1,0,0.25,"Boone shoots and misses"])

print("There are " + str(len(CueArray)) + " cues in the show")

def input_thread_core0():
    global status
    global triggerBtnPush
    global cueDelayTime
    
    triggerBtn = Pin(0, Pin.IN, Pin.PULL_DOWN)
    stopBtn = Pin(1, Pin.IN, Pin.PULL_DOWN)
    triggerRemote = Pin(4, Pin.IN, Pin.PULL_DOWN)
    gunIsCocked = False

    while True:
        if triggerBtn.value() or triggerRemote.value():
            #Start preformance
            #Must push the green trigger btn to start the show
            if status == 0:
                print("Start the show in 5 seconds")               
                triggerBtnPush = True
                sleep(5)
                status = 1  
                print("Cue 1 Is Next")
                continue
        #The Show has started
        if status > 0:
            #print(triggerBtn.value())
            #print(triggerRemote.value())
            #print(gunIsCocked)
            if ((triggerBtn.value() == 1) or (triggerRemote.value() == 1)) and gunIsCocked == False:
                print("Button Down")
                gunIsCocked = True
                #sleep(cueDelayTime)
                continue
            if ((triggerBtn.value() == 0) or (triggerRemote.value() == 0)) and gunIsCocked == True:
                #print("triggerWireles.value()=" + str(triggerWireless.value()) + "   gunIsCocked=" + str(gunIsCocked))
                gunIsCocked = False
                print("Fire Cue " + str(status) + " " + CueArray[status - 1][4])                
                if CueArray[status - 1][0] is not None:
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
    
    triggerLed = PWM(Pin(2))
    triggerLed.freq(50)
    triggerLedValueMax = 4000
    triggerLedValue = 2000
    triggerLed.duty_u16(triggerLedValue) 
   
    stopLed = PWM(Pin(3))
    stopLed.freq(50)
    stopBtnValueMax = 4000
    stopBtnValue = 2000
    stopLed.duty_u16(stopBtnValue)
    
    yellowBtnLed = PWM(Pin(10))
    yellowBtnLed.freq(50)
    yellowBtnLedValueMax = 640000
    yellowBtnLedValue = 2000
    yellowBtnLed.duty_u16(yellowBtnLedValue)
     
    blinkCount = 0
    while True:
        if triggerBtnPush:
            triggerBtnPush = False
            triggerLed.duty_u16(triggerLedValueMax)
            sleep(cueDelayTime)
            triggerLed.duty_u16(0)
            continue
        else:            
            if status == -1:
                #Blink the stop button fast the           
                triggerLed.duty_u16(0)
                stopLed.duty_u16(stopBtnValue)
                if stopBtnValue == stopBtnValueMax :
                    stopBtnValue = 0
                else :
                    stopBtnValue = stopBtnValueMax             
                sleep(0.1)
                continue
            if status == 0:
                #Blink the red button then green 
                #Indicats that the green btn must be pushed to start the show
                stopLed.duty_u16(0)          
                triggerLed.duty_u16(triggerLedValue)
                yellowBtnLed.duty_u16(yellowBtnLedValueMax)
                sleep(0.06)
                stopLed.duty_u16(stopBtnValueMax)                 
                triggerLed.duty_u16(0)
                yellowBtnLed.duty_u16(0)
                sleep(0.06)
                stopLed.duty_u16(0)                 
                triggerLed.duty_u16(0)
                yellowBtnLed.duty_u16(yellowBtnLedValueMax)
                continue
            else:             
                stopLed.duty_u16(stopBtnValueMax)             
                #Blink the trigger button the status number of times
                #Indicats that the we are going to play cue# (green btn) or stop (red btn)
                i = 0
                while i < status:                
                    triggerLed.duty_u16(triggerLedValueMax)
                    yellowBtnLed.duty_u16(yellowBtnLedValueMax)
                    sleep(0.15)
                    triggerLed.duty_u16(0)
                    yellowBtnLed.duty_u16(0)
                    sleep(0.15)
                    i = i + 1
                sleep(0.80)
                continue

        #This should never run
            
        triggerLed(0)
        stopLed.duty_u16(0)   
   
            
  
#Start the threads
second_thread = _thread.start_new_thread(status_thread_core1, ())
input_thread_core0()