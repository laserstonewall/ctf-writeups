SBOX = [0xb9, 0xb3, 0x49, 0x94, 0xf9, 0x3, 0xd0, 0xfc, 0x67, 0xa3, 0x72, 0xb5,
	 0x45, 0x82, 0x54, 0x93, 0x5b, 0x88, 0x5c, 0xe0, 0x96, 0x41, 0xc7, 0xa,
	 0xdb, 0x7f, 0x77, 0x29, 0x9, 0xb, 0x8d, 0x80, 0x2d, 0xaf, 0xe1, 0x4a,
	 0x38, 0x73, 0x3a, 0x6a, 0xf2, 0xb6, 0xdc, 0xbd, 0x79, 0x2a, 0xcb, 0x55,
	 0x10, 0x61, 0x63, 0x68, 0x13, 0x95, 0x9f, 0x1c, 0x4f, 0x35, 0x5f, 0xae,
	 0x37, 0xb8, 0xfe, 0xea, 0x7a, 0x4b, 0xc3, 0xe8, 0xc6, 0x44, 0x60, 0xb2,
	 0x5a, 0x2e, 0xeb, 0x47, 0x1e, 0x4d, 0x9a, 0x98, 0x36, 0xe7, 0x48, 0x3e,
	 0x42, 0x6b, 0xa1, 0x65, 0xb1, 0x57, 0x6c, 0x4, 0xff, 0xfd, 0x34, 0x40,
	 0x31, 0x8c, 0xbe, 0xda, 0x2c, 0x1b, 0x7c, 0x64, 0x3f, 0xd1, 0xc9, 0x9b,
	 0x25, 0x87, 0xaa, 0xd, 0x15, 0x1f, 0xce, 0x30, 0xfb, 0xd5, 0xef, 0xbb,
	 0x24, 0x28, 0x90, 0x2f, 0x85, 0xc5, 0x4c, 0x97, 0xa8, 0x16, 0x43, 0xac,
	 0x74, 0xc0, 0x8b, 0xc4, 0xe9, 0x7e, 0xf5, 0xd2, 0xab, 0x12, 0xd8, 0xdd,
	 0xa9, 0xad, 0x21, 0xd7, 0xed, 0x1, 0x32, 0xbf, 0xa6, 0x8a, 0xe3, 0x6f,
	 0xde, 0x84, 0xc8, 0x6d, 0x92, 0x99, 0x51, 0x39, 0xe5, 0x46, 0x9c, 0xf0,
	 0x0, 0x8e, 0xbc, 0xa2, 0x22, 0x9d, 0xc2, 0xfa, 0xb0, 0x33, 0x56, 0xec,
	 0xdf, 0x89, 0x52, 0x8, 0x62, 0x7, 0x59, 0xb7, 0xe4, 0x14, 0x9e, 0x70,
	 0xd9, 0xe, 0x3d, 0x26, 0x1d, 0x66, 0x71, 0xe2, 0x5, 0x6e, 0x5d, 0xf6,
	 0x18, 0xf, 0xcf, 0xd6, 0xe6, 0xba, 0x1a, 0x78, 0xf8, 0x76, 0xd3, 0x50,
	 0xf7, 0x58, 0x17, 0x91, 0x11, 0x86, 0xf1, 0xa4, 0x19, 0x4e, 0x6, 0xa0,
	 0xca, 0xa5, 0xf3, 0xee, 0xcd, 0x53, 0x5e, 0xa7, 0xc, 0xb4, 0x2, 0xc1,
	 0x3b, 0x27, 0x69, 0x7d, 0x8f, 0xcc, 0x20, 0x7b, 0x81, 0x2b, 0x83, 0x23,
	 0xd4, 0x3c, 0xf4, 0x75]

def pad(data):
	if len(data) == 0:
		return b"\x00" * 8
	while len(data) % 8 != 0:
		data += b"\x00"
	return data

def sub(state):
	return [SBOX[x] for x in state]

def mix(block, state):
	for i in range(8):
		state[i] ^= block[7 - i] & 0x1f
		state[i] ^= block[i] & 0xe0
	return state

def shift(state):
	t = 0
	for s in state:
		t ^= s
	u = state[0]
	for i in range(7):
		state[i] ^= t ^ state[i] ^ state[i+1]
	state[7] ^= t ^ state[7] ^ u
	return state

def hash(data):
	assert len(data) % 8 == 0

	state = [2**i-1 for i in range(1, 9)]
	for i in range(0, len(data), 8):
		block = data[i: i+8]
		state = sub(state)
		state = mix(block, state)
		state = shift(state)

	state = sub(state)
	return bytes(state).hex()

Banner = """
 ____  __  __ ____        _   _    _    ____  _   _
/ ___||  \/  / ___|      | | | |  / \  / ___|| | | |
\___ \| |\/| \___ \ _____| |_| | / _ \ \___ \| |_| |
 ___) | |  | |___) |_____|  _  |/ ___ \ ___) |  _  |
|____/|_|  |_|____/      |_| |_/_/   \_\____/|_| |_|
"""

print(Banner, end= "\n\n")
print("Can you even Collide?")

MSG1 = bytes.fromhex(input("First message : ").strip())
MSG2 = bytes.fromhex(input("Second message : ").strip())

MSG1 = pad(MSG1)
MSG2 = pad(MSG2)

H1 = hash(MSG1)
H2 = hash(MSG2)

print("H(MSG1) = {}".format(H1))
print("H(MSG2) = {}".format(H2))

if MSG1 == MSG2:
	print("Really ?")
elif H1 == H2 : 
	if H1 == "0000000000000000":
		print("Good job, Here's your reward: ")
		print(open("flag.txt","r").read())
	else:
		print("So close, yet so far :(")
else:
	print("Not even close :(")