# Squib-Box
Micro Python project for Pi Pico that fires off gun shot squibs  

boot up the pi so you can see it as a folder in windows push the bootsel button and plug it into usb

add the the .utf file to the drive

Set COM port press the Bootselect button on the Pico and plung into usb to computer
In Thony > Run > Configure Interpreter > Port or WebREPL (To find it go to the device manager)

Save the program in Thonny on to the pi pico as main.py hit the play button


In MicroPython is to use a $2 hardware module called a MAX485 TTL-to-RS485 Breakout Board.This small board does all the heavy electrical translation for you. It allows you to plug standard DMX wires into one side and read clean MicroPython data directly out of the other side using the Pico's built-in UART port.

Step 1: Get the Hardware ModuleSearch online for a "MAX485 TTL to RS485 module". They cost around $1 to $3 and feature a green screw-terminal block on one end for your DMX signal.

Step 2: Wire It for ReceivingConnect the module to your Raspberry Pi Pico like this:

MAX485 Module Pin
Pi Pico PinWhy?VCCVBUS (Pin 40)Powers the chip with 5 Volts.GNDGND (Any Ground Pin)Common circuit ground.RO (Receiver Out)GPIO 1 (Pin 2 / UART0 RX)Sends incoming DMX data straight into the Pico.RE (Receiver Enable)GND (Any Ground Pin)Tying this to ground keeps the chip in Listen Mode.DE (Driver Enable)GND (Any Ground Pin)Disables transmitting so it doesn't conflict with incoming data.DI (Driver In)Leave DisconnectedNot needed for receiving.On the green terminal side: Connect terminal A to DMX Pin 3 (Data+) and terminal B to DMX Pin 2 (Data-).