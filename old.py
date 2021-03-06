#/usr/bin/env python

def Normal(message):
   #Normal Flight
   return str(message)


def Front(message):
   #Object to the front
   temp = list(str(message))
   temp[2] = binascii.unhexlify('64')
   temp[3] = binascii.unhexlify('0b')
   return "".join(temp)


def Left(message):
   #Object to the left
   temp = list(str(message))
   temp[1] = binascii.unhexlify('94')
   temp[2] = binascii.unhexlify('06')
   return "".join(temp)


def Rear(message):
   #Object to the rear
   temp = list(str(message))
   temp[2] = binascii.unhexlify('a4')
   temp[3] = binascii.unhexlify('34')
   return "".join(temp)


def Right(message):
   #Object to the right
   temp = list(message)
   temp[2] = binascii.unhexlify('bc')
   temp[3] = binascii.unhexlify('01')
   return "".join(temp)


directionFlags = {0:Normal,
			1:Front,
			2:Left,
			4:Rear,
			8:Right,
}

if __name__ == "__main__":
   import serial
   import time
   import pigpio
   import srte
   import binascii

   #SBUS Definition (1 startbit, 8 databits, 1 odd parity, 2 stopbits)
   port = serial.Serial('/dev/ttyAMA0')
   port.baudrate = 100000
   port.bytesize = 8
   port.parity = serial.PARITY_ODD
   port.stopbits = 2
   port.timeout = 6

   pi = pigpio.pi()

   if not pi.connected:
       exit()

   S=[] #this will hold sensor objects
   Readings = [0,0,0,0,0,0,0,0] #the most recent reading values from the sensor
   S.append(srte.sonar(pi, 16 , 20)) #sensor trigger pin 04/ echo pin 04
   S.append(srte.sonar(pi, 13, 19)) #sensor trigger pin 14/ echo pin 15
   S.append(srte.sonar(pi, 23, 24)) #sensor trigger pin 23/ echo pin 24
   S.append(srte.sonar(pi, 17, 27)) #sensor trigger pin 17/ echo pin 27

   end = time.time() + 60.0

   r = 1

   #test code
   #first = bytearray.fromhex("0f 00 04 20 00 01 38 3f 00 fe 27 00 01 08 40 00 02 10 80 00 04 20 00 00 00")

   try:
        while time.time() < end:
	    #test code
	    #message = first

            #get sbus message

            #directional flag to determine which direction to avoid
	    #bits are defined as right,rear,left,front where a 1 in that bit
	    # means an object is present that direction
            direction = 0
            message = port.read(25)            	

            for s in range(len(S)): #iterate through each sensor
                S[s].trigger()
	    time.sleep(.005)	
            for s in range(len(S)):#read each sensor and store in readings array
                Readings[s] = S[s].read()
                if (Readings[s] <= 20):
                    if (s == 0):#front sensors
                        direction = direction | 1
                    if (s == 1):#left sensors
                        direction = direction | 2
                    if (s == 2):#rear sensors
                        direction = direction | 4
                    if (s == 3):#right sensors
                        direction = direction | 8
                print("{} {:.1f}".format(r, Readings[s]))
	        #port.write(directionFlags[direction](message))
                #message = directionFlags.setdefault(direction,message)(message)
            	#print (' ' .join(x.encode('hex') for x in message))
            	port.write(message)

            r += 1
            time.sleep(.0025)

   except KeyboardInterrupt:
      pass

   print("\ntidying up")

   for s in S:
      s.cancel()
   print Readings #print recent readings
   print r
   pi.stop()
