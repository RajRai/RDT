'''
Created on Oct 22, 2020

@author: rajat
'''

import checksum
import sys
import socket
from threading import Timer
import datetime

seq = 0
sock = None
timer = None
timeout = 0
chunks = []
received = 0
sent = 0
corr_count = 0
timeouts = 0
acks = 0

def print_results():
    string = ""
    #if (acks < 10):
    #    sock.close()
    #    startup()
    for i in range(0,acks):
        chunk = chunks[i]
        print(chunk)
        string += chunk
    print(checksum.checksum(string))
    t = datetime.datetime.now()
    print("Raj Rai, " + t.strftime("%b %d %Y, %H:%M:%S"))
    print("Total Received: " + str(received))
    print("Total Sent: " + str(sent))
    print("Total Corrupted: " + str(corr_count))
    print("Total Timeouts: " + str(timeouts))
    sys.exit(0)

# called when a timeout occurs
def resend_chunk(acks_when_defined):
    global timeouts, sent, timer
    if (acks_when_defined < acks):
        return
    timer = Timer(timeout, resend_chunk, [acks_when_defined])
    timer.start()
    message = str(seq) + " " + str(seq) + " " + chunks[acks] + " "
    message += checksum.checksum(message)
    message = message.encode('utf-8')
    try:
        sock.send(message)
        #print("SENT (TIMEOUT): " + message.decode())
        timeouts += 1
        sent += 1
    except:
        print_results()

def send_next_chunk():
    global seq, sent, received, corr_count, acks, timer
    while acks < 10:
        timer = Timer(timeout, resend_chunk, [acks])
        message = str(seq) + " " + str(seq) + " " + chunks[acks] + " "
        message += checksum.checksum(message)
        #print("SENT: " + message)
        message = message.encode('utf-8')
        timer.start()
        try:
            sock.send(message)
            sent += 1
            response = sock.recv(30)
            received += 1
        except:
            timer.cancel()
            print_results()
        
        timer.cancel()
        response = response.decode('utf-8')
        #print("RECEIVED: " + response)
        if (response == ""):
            break
        if checksum.checksum_verifier(response):
            splits = response.split()
            if int(splits[0]) == seq:
                seq = -seq+1
                acks += 1
        else:
            corr_count += 1
        if response == "":
            break
    print_results()
    

def read_file():
    try:
        file = open('declaration.txt')
    except:
        sys.exit(1)
    
    for i in range(0,10):
        chunk = file.read(20)
        if not chunk:
            break
        chunks.append(chunk)
    

def startup():
    global ip, port, cid, los, corrupt, delay, timeout, sock
    # get inputs
    ip = "128.119.245.12" # gaia
    port = 20000
    cid = int(sys.argv[1])
    loss = float(sys.argv[2])
    corrupt = float(sys.argv[3])
    delay = int(sys.argv[4])
    timeout = float(sys.argv[5])
    
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(60)
    try:
        sock.connect((ip, port))
    except:
        sock = None
    
    
    
    nmessage = "HELLO S " + str(loss) + " " + str(corrupt) + " " + str(delay) + " " + str(cid)
    
    try:
        sock.send(nmessage.encode('utf-8'))
    except:
        pass
    
    while True:
        try:
            response = sock.recv(64)
            response = response.decode()
        except:
            break
        if response.startswith("OK"):
            print("Connection established %s %d %d" % (ip, port, cid))
            t = datetime.datetime.now()
            print(t.strftime("%b %d %Y, %H:%M:%S"))
            read_file()
            send_next_chunk()
            break
        elif response.startswith("WAITING"):
            if acks >= 9:
                print_results()
            print(response)
            continue
        elif response.startswith("ERROR"):
            print(response)
            break
        
    try:
        sock.close()
    except:
        pass
    sys.exit()

if __name__ == '__main__':    
    t = datetime.datetime.now()
    print("Raj Rai, " + t.strftime("%b %d %Y, %H:%M:%S"))
    startup()