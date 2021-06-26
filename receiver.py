'''
Created on Oct 22, 2020

@author: rajat

Just a note that these for some reason run in my Windows CMD
but not on an Anaconda prompt. Both use Python 3, but thought
it was worth mentioning.
'''

import checksum
import sys
import socket
import datetime

ack = 0
sock = None
chunks = []
received = 0
sent = 0
corr_count = 0

def print_results():
    string = ""
    #if (len(chunks)<10):
    #    sock.close()
    #    startup()
    for chunk in chunks:
        print(chunk)
        string += chunk
    print(checksum.checksum(string))
    t = datetime.datetime.now()
    print("Raj Rai, " + t.strftime("%b %d %Y, %H:%M:%S"))
    print("Total Received: " + str(received))
    print("Total Sent: " + str(sent))
    print("Total Corrupted: " + str(corr_count))
    sys.exit(0)
        
def receive_next_chunk():
    global ack, sent, received, corr_count
    acks = 0
    while len(chunks)<10:
        try:
            response = sock.recv(30)
            received += 1
        except:
            #print("quit with reason: failed receive")
            break
        response = response.decode('utf-8')
        #print("RECEIVED: " + response)
        if response == "":
            #print("quit with reason: empty response")
            break
        # I actually set this up at first so that it would use numbered
        # ACKs (failed to acknowledge RDT ACKs are only 1 or 0). That's
        # why the implementation is a bit odd, figured it was worth keeping
        # some pieces of it in case it comes up in a future assignment
        msg = ack
        if checksum.checksum_verifier(response):
            #splits = response.split()
            idx = response.find(" ")
            if int(response[0]) == ack:
                chunks.append(response[idx+3:idx+23])
                ack = -ack+1
                acks += 1
            else:
                msg = -ack+1
        else:
            msg = -ack+1
            corr_count += 1
        message = " " + " " + str(msg) + " " + "                    " + " "
        message += checksum.checksum(message)
        #print("SENT: " + message)
        message = message.encode('utf-8')
        try:
            sock.send(message)
            sent += 1
        except:
            #print("quit with reason: failed send")
            break
    print_results()
    

def startup():
    global ip, port, cid, loss, corrupt, delay, sock
    # get inputs
    ip = "128.119.245.12" # gaia
    port = 20000
    cid = int(sys.argv[1])
    loss = float(sys.argv[2])
    corrupt = float(sys.argv[3])
    delay = int(sys.argv[4])
    
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(60)
    try:
        sock.connect((ip, port))
    except:
        sock = None
    
    # startup printing
    
    
    nmessage = "HELLO R " + str(loss) + " " + str(corrupt) + " " + str(delay) + " " + str(cid)
    
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
            receive_next_chunk()
            break
        elif response.startswith("WAITING"):
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