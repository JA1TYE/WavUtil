import wave
import argparse
import os.path
import struct

#prepare an argument parser
parser = argparse.ArgumentParser(description='Convert .wav to .bin or C-style Array.')
parser.add_argument('input')
parser.add_argument('-o',metavar = '<output>')
parser.add_argument('-b',action='store_true',help='Generate .bin file.',default=True)
parser.add_argument('-a',action='store_true',help='Generate .txt(C-Style Array Source) file.')
parser.add_argument('-r',action='store_true',help='Reduce bit resorution from 16-bit to 8-bit')

pres = parser.parse_args()

#Set output filename
if pres.o is None:
    fwname = pres.input
else:
    fwname = pres.o

#Set output file's extension and open file
if pres.b:
    fbin = open(fwname + '.bin','wb')

if pres.a:
    farr = open(fwname + '.txt','w')

#open the wave file
if os.path.exists(pres.input):
    wav = wave.open(pres.input,'r')
    wInfo = wav.getparams()
    print('Filename: ' + pres.input)
    print('Number of channels: ' + str(wInfo[0])+ ' [Ch]')
    print('Number of frame: ' + str(wInfo[3])+ ' [Frames]')
    print('Size of audio data: ' + str(wInfo[3] * wInfo[1] * wInfo[0])+ ' [Bytes]')
    print('Sampling rate: ' + str(wInfo[2])+' [Hz]')
    print('Sample size: ' + str(wInfo[1])+ ' [Bytes/sample]')
    print('Compression: ' + str(wInfo[5]))
else:
    print('Error:No such file ' + '\'' + pres.input + '\'')
    quit()

#Prepare the header for C-Style option
if pres.a:
    farr.write('/*\n')
    farr.write('Filename: ' + pres.input)
    farr.write('File Format: ' + str(wInfo[0]) +'-Ch,' + str(wInfo[1] * 8) + '-Bit,' + str(wInfo[2]) + 'Hz\n')
    if pres.r:
        farr.write('Bit resolution is reduced to 8-Bit.\n')
    farr.write('*/\n')

    #Calc number of element
    NoE = wInfo[3] * wInfo[0]

    if wInfo[1] == 2 and pres.r is not True:#for 16bit wav without -r option
        farr.write('int16_t wave[' + str(NoE) + ']={\n')
    else:
        farr.write('uint8_t wave[' + str(NoE) + ']={\n')


#Write the file
for i in range(wInfo[3]):
#for i in range(1):
    t = wav.readframes(1)

    if wInfo[1] == 2:# if Bytes/sample are 2 bytes (16-bit)
        if pres.r:# bit reduce option
            dL = struct.unpack('h',t[0:2])[0]
            dL = int(dL / 256.0) + 128
            if wInfo[0] == 2:# if file has two channel
                dR = struct.unpack('h',t[2:4])[0]
                dR = int(dR / 256.0) + 128
        else: #treated as unsigned 16bit int
            dL = struct.unpack('H',t[0:2])[0]
            if wInfo[0] == 2:# if file has two channel
                dR = struct.unpack('H',t[2:4])[0]
    else:# if Bytes/sample is 1 byte (8-bit)
        dL = t[0]
        if wInfo[0] == 2:# if file has two channel
            dR = t[1]

    if pres.b:#Binary output
        if pres.r:
            if wInfo[0] == 2:# if file has two channel
                fbin.write(struct.pack('BB',dL,dR))
            else:
                fbin.write(struct.pack('B',dL))
        else:
            fbin.write(t)

    if pres.a:#C-Style Array output
        if wInfo[1] == 2 and pres.r is not True:#for 16bit wav without -r option
            if wInfo[0] == 2:
                farr.write('0x{0:0>4x},0x{1:0>4x}'.format(dL,dR))
            else:
                farr.write('0x{0:0>4x}'.format(dL))
        else:
            if wInfo[0] == 2:
                farr.write('0x{0:0>2x},0x{1:0>2x}'.format(dL,dR))
            else:
                farr.write('0x{0:0>2x}'.format(dL))
        #print comma
        if i != (wInfo[3] - 1):
            farr.write(',')

        #Print New Line
        if wInfo[0] == 2 and (i % 4) == 3:
            farr.write('\n')
        elif wInfo[0] == 1 and (i % 8) == 7:
            farr.write('\n')

if pres.a: #Close the array
    farr.write('};\n')
