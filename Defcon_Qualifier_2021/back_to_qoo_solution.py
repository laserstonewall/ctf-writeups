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
    time.sleep(0.01)
    conv = s.recv(16000)

    # this was a guess as to how to tweak it by adding the rotations
    # it could be reversed if an overall win didn't occur after a few tries (it's still probabilistic)
    if compbet1 == b'0':
        choice = b'1'
    else:
        choice = b'2'

    # # This causes you to lose, win about 50%
    # if compbet1 == b'0':
    #     choice = b'2'
    # else:
    #     choice = b'1'

    # # This causes you to lose, but not as badly, win about 75%
    # if compbet1 == b'0':
    #     choice = b'0'
    # else:
    #     choice = b'0'

    s.send(choice + b'\n')
    if i==127:
        time.sleep(1)
        conv = s.recv(16000)
        conv += s.recv(16000)
    else:
        time.sleep(0.01)
        conv = s.recv(16000)   

    # We can tell which part of the printout corresponds to compbids
    compbids2.append(conv.split(b'\n')[0].split(b'bets on ')[1][0:1])
    pbet1.append(conv.split(b'\n')[0].split(b'you bet on ')[-1])
    winloss.append(conv.split(b'\n')[1][0:1])

for line in conv.split(b'\n'):
    print(line)

nonce = conv.split(b'\n')[-3].split(b':')[-1].decode('ascii')
data  = conv.split(b'\n')[-2].split(b':')[-1].decode('ascii')

# print(nonce.decode(''))
# print(data)

# bases come from the randomly generated competitor_bid2 for each game (Zardus competitor)
# this is the referee in the zardus bet function
bases = compbids2

# adam sends his bases in the message
adam = conv.split(b'\n')

# let's figure out where they used the same bases as part of the protocol
adam_msg = [x.split(b':')[-1] for x in adam[6:6+128]]
same_indices = []
for i, base in enumerate(bases):
    print(i, base, adam_msg[i], base==adam_msg[i])
    if base==adam_msg[i]:
        same_indices.append(i)
        
print(same_indices)

print(b''.join([bases[i] for i in same_indices]))

pbet1new = ''.join([x.decode('ascii') for x in pbet1])

winlossnew = ''.join([x.decode('ascii').lower() for x in winloss])

# you can back out player2_bet, which is actually the state zardus is sending
# the value of pbet2 necessarily had to be different if won or lost, hence two cases
pbet2 = []
for i in range(128):
    if winlossnew[i]=='w':
        print(winlossnew[i],
              int(pbet1new[i]), 
              int(compbids1[i]) * int(compbids2[i]), 
              int(pbet1new[i])^(int(compbids1[i]) * int(compbids2[i]))
             )
        pbet2.append(int(pbet1new[i])^(int(compbids1[i]) * int(compbids2[i])))
    else:
        print(winlossnew[i],
              int(pbet1new[i]), 
              int(compbids1[i]) * int(compbids2[i]), 
              1 - (int(pbet1new[i])^(int(compbids1[i]) * int(compbids2[i])))
             )
        pbet2.append(1 - (int(pbet1new[i])^(int(compbids1[i]) * int(compbids2[i]))))

import hashlib
from Crypto.Cipher import AES

def key_array_to_key_string(key_list):
    key_string_binary = b''.join([bytes([x]) for x in key_list])
    return hashlib.md5(key_string_binary).digest()

key = [int(x) for x in ''.join([str(pbet2[i]) for i in same_indices])]
key = key_array_to_key_string(key)

# nonce = bytes.fromhex('2bfcd1f6cd2e5f285d8f480a0db0bc44')
# data = bytes.fromhex('48490dfe52dc6d6cfcbd7b92fbc3d7ab978de76cabf72d576a4b7bdd6aade800dc0d9c1ecd15008182dbc552a339662cd054fd')

nonce = bytes.fromhex(nonce)
data = bytes.fromhex(data)

cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
print(cipher.decrypt(data))