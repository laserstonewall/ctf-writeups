import socket
import time
import pandas as pd

# phrasedict = dict()
# phrasecount = 1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '172.17.0.2'  # The server's hostname or IP address
PORT = 5000          # The port used by the server

s.connect((HOST, PORT))

time.sleep(1)

i = 0

# Listen to the initial banner
conv = s.recv(1024)

# These correspond to the competitor_bet1 and competitor_bet2 in game.py in the Game class
compbids1 = []
compbids2 = []
pbet1 = []
winloss = []

for i in range(128):
    if i==0:
        compbet1 = conv.split(b'\n')[3].split()[-1]
    else:
        compbet1 = conv.split(b'\n')[2].split()[-1]
    compbids1.append(compbet1)
    
    print(conv.split(b'\n'))
    print(compbet1)
    
    # We want to use our magic qoin
    choice = b'2'
    s.send(choice + b'\n')
    time.sleep(0.1)
    conv = s.recv(16000)

    # this was a guess as to how to tweak it by adding the rotations
    # it could be reversed if an overall win didn't occur after a few tries (it's still probabilistic)
    if compbet1 == b'0':
        choice = b'1'
    else:
        choice = b'2'

    s.send(choice + b'\n')
    if i==127:
        time.sleep(5)
        conv = s.recv(16000)
        conv += s.recv(16000)
    else:
        time.sleep(0.1)
        conv = s.recv(16000)   

    # We can tell which part of the printout corresponds to compbids
    compbids2.append(conv.split(b'\n')[0].split(b'bets on ')[1][0:1])
    pbet1.append(conv.split(b'\n')[0].split(b'you bet on ')[-1])
    winloss.append(conv.split(b'\n')[1][0:1])
    
print(conv.split(b'\n'))