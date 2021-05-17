# sms

**Category:** Crypto

## Challenge

Challenge text:

```
Doesn't every hash follow the sms protocol (substitute-mix-shift) ? Well, I think so! Therefore, I created my own hash function.

nc sms.2021.3k.ctf.to 1337
```

**Attachment:** [sms-d502d22d55f1cde3d8d078876eea4c3f.py](sms-d502d22d55f1cde3d8d078876eea4c3f.py)

We are given the Python file that runs the remote service we can interact with via `netcat`, using the above IP/port pair.

When we connect, we see an intro message and are asked to enter two of our own messages:

```
 ____  __  __ ____        _   _    _    ____  _   _
/ ___||  \/  / ___|      | | | |  / \  / ___|| | | |
\___ \| |\/| \___ \ _____| |_| | / _ \ \___ \| |_| |
 ___) | |  | |___) |_____|  _  |/ ___ \ ___) |  _  |
|____/|_|  |_|____/      |_| |_/_/   \_\____/|_| |_|


Can you even Collide?
First message : abcd
Second message : efgh
```

where here I've entered `abcd` and `efgh` as two test messages.

Let's dig into the provided Python file.

We can see an array of integers, defined by their hex values, stored in `SBOX`, functions that manipulate the data, then the interaction code. First we see:

```python
MSG1 = bytes.fromhex(input("First message : ").strip())
MSG2 = bytes.fromhex(input("Second message : ").strip())
```

The `bytes.fromhex` tells us that the input messages need to be hex format. Then the messages are run through the `pad` and `hash` functions, which perform manipulations on the input strings, storing the answers in `H1` and `H2`.

```python
MSG1 = pad(MSG1)
MSG2 = pad(MSG2)

H1 = hash(MSG1)
H2 = hash(MSG2)
```

Finally, a set of `if/else` statements checks to make sure the initial messages were not the same.

```python
if MSG1 == MSG2:
	print("Really ?")
```

If they are not the same, but the resulting hashes are _also_ not the same, we again fail, producing the message `Not even close :(`.

If the resulting hashes `H1` and `H2` are the same, **and** if they are both `0000000000000000`, the function reads in the flag file, and prints it to screen for us.

This means our primary task is to make sure that the output of the `hash` function for our messages is `0000000000000000`. So let's get into the `hash` function and work backwards.

```python
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
```

`state` is cast to a list of type `bytes`, and then converted to hex. Each byte is represented by two hex characters, so if the hash function returns `0000000000000000`, `state = [0, 0, 0, 0, 0, 0, 0, 0]`:

```python
In [5]: bytes([0, 0, 0, 0, 0, 0, 0, 0]).hex()
Out[5]: '0000000000000000'
```

The last function that is run is `sub(state)`, so we need the output of this function to give us our array of `0`: `[0, 0, 0, 0, 0, 0, 0, 0]`. What does `sub` look like?

```python
def sub(state):
	return [SBOX[x] for x in state]
```

So `sub` grabs elements from the `SBOX` list. Since we need our output to have all `0`'s, which elements in `SBOX` are `0`?

```python
In [3]: import numpy as np

In [4]: np.argwhere(np.array(SBOX)==0x0)
Out[4]: array([[168]])
```

Only one element has `0`, element `168`. So we need to send an array into `sub` that looks like `[168, 168, 168, 168, 168, 168, 168, 168]`:

```python
In [7]: sub([168, 168, 168, 168, 168, 168, 168, 168])
Out[7]: [0, 0, 0, 0, 0, 0, 0, 0]
```

Looking back to the start of the `hash` function, we see first that the `assert` statement means we must have an input data array in blocks of length 8. The `state` array is then initialized with the powers of 2 (minus 1): `[1, 3, 7, 15, 31, 63, 127, 255]`.  

Next we iterate through the data in blocks of length 8. For now, since we know at the _end_ of `hash` we need an array of length 8, let's assume there is a single block. We'll come back to this assumption towards the end. This allows us to ignore the loop for the moment, and assume each function is run once successively on the `state` array. 

Picking up where we left off towards the end of the function, we see that the `[168, 168, 168, 168, 168, 168, 168, 168]` must come out of the `shift` function. This function is a bit complicated, so let's put in a few test arrays and see what happens:

```python
In [10]: shift([1, 2, 3, 4, 5, 6, 7, 8])
Out[10]: [10, 11, 12, 13, 14, 15, 0, 9]

In [11]: shift([0, 1, 2, 3, 4, 5, 6, 7])
Out[11]: [1, 2, 3, 4, 5, 6, 7, 0]

In [12]: shift([2, 3, 4, 5, 6, 7, 8, 9])
Out[12]: [3, 4, 5, 6, 7, 8, 9, 2]

In [13]: shift([3, 4, 5, 6, 7, 8, 9, 10])
Out[13]: [12, 13, 14, 15, 0, 1, 2, 11]

In [14]: shift([4, 5, 6, 7, 8, 9, 10, 11])
Out[14]: [5, 6, 7, 8, 9, 10, 11, 4]

In [15]: shift([1, 1, 1, 1, 1, 1, 1, 1])
Out[15]: [1, 1, 1, 1, 1, 1, 1, 1]

In [16]: shift([2, 2, 2, 2, 2, 2, 2, 2])
Out[16]: [2, 2, 2, 2, 2, 2, 2, 2]
```

For arrays starting with an even number, it seems to rotate the array by 1, for odd the behavior is a bit more complicated, and when numbers are repeated, the output is the same as the input. Since we need `[168, 168, 168, 168, 168, 168, 168, 168]` as the output, if we have that as the input to the `shift` function, we should have the same output:

```python
In [18]: shift([168, 168, 168, 168, 168, 168, 168, 168])
Out[18]: [168, 168, 168, 168, 168, 168, 168, 168]
```

Continuing up the `hash` function, this means that the output of `mix(block, state)` must be `[168, 168, 168, 168, 168, 168, 168, 168]`. Looking at `mix`, we can see that it generates its output array by iterating through each element of `state`, and `XOR`ing it a few times. 

The first `XOR` uses the `[7-i]` byte from block, first `AND`s it with `0x1f` with is `00011111` in binary, so it's grabbing the last 5 bits of that block, then `XOR`ing with the current `state` value.

The second `XOR` takes the `[i]` byte from block, `AND`s with `0xe0` which is `11100000` in binary, so it takes the first 3 bits of that block, then `XOR`s with the value of `state` from the previous line.

So `mix` takes the `block` data input, and uses pairs to compute the new `state` value, i.e. `state[0]` depends on `block[7]` and `block[0]`, `state[1]` depends on `block[6]` and `block[1]`, etc.

We could probably logic out what these need to be by thinking about the bits, but it's easier just to brute force the calculation. We know the input `state` to `mix` is determined by calling `sub` on the initial state array of `[1, 3, 7, 15, 31, 63, 127, 255]`, so `sub` transforms it to `[179, 148, 252, 147, 128, 234, 151, 117]` (using the integer representation of the hex numbers returned). 

So for `state[0] = 179`, after its new state is computed using `block[7]` and `block[0]`, we want `state[0] = 168`. Each block is a single byte, so it can take values ranging from `0` to `255`. So we can just check all possible combinations of `block[7]` and `block[0]` to see which give `168` as the output for `state[0]`. However, the calculation for `state[7]` _also_ uses `block[7]` and `block[0]`, so whatever pair we find for these two block elements, we'll need to make sure also works for the calculation for converting `state[7] = 117` to `state[7] = 168`.

The code I wrote to do this brute force is:

```python
# custom version of the function to make my brute force easier
def mixtest(block1, block2, state):
    state ^= block2 & 0x1f
    state ^= block1 & 0xe0
    return state

# the initial state array
state = [2**i-1 for i in range(1, 9)]

# sub in the SBOX values
substate = sub(state)

# an empty array to hold the integer values for the first block
block1 = [0 for i in range(8)]

# we only need to iterate through 4 indexes, since we'll determine the proper values
# for block[i] and block[7-i] at the same time
for ind in range(4):
    
    # brute force of all possible block pairs for the current block[ind] block[7-ind] pair
    for i in range(255):
        for j in range(255):
            
            # we need to satisfy for both state[ind] and state[7-ind]
            currstate1 = mixtest(i, j, substate[ind])
            currstate2 = mixtest(j, i, substate[7-ind])
            if (currstate1 == 168) and (currstate2 == 168):

                block1[ind] = i
                block1[7-ind] = j
                
print(block1)

[29, 63, 66, 40, 59, 84, 60, 219]
```

So this is the value for the first data block we need. Translating back to a hex string:

```python
''.join([hex(x)[2:] for x in block1])

'1d3f42283b543cdb'
```
So this is the 8 byte (16 hex characters) string we need as input to `hash`. The last thing is to look at `pad`. We can see that it really just makes sure that our `MSG1` and `MSG2` are 8 bytes long, and zero pads the end if not. Our calculated data string is already 8 bytes long, so pad won't modify it.

We can test:

```python
MSG = '1d3f42283b543cdb'
MSG = bytes.fromhex(MSG.strip())

MSG = pad(MSG)

H = hash(MSG)

print(H)

'0000000000000000'
```

Awesome, so we have a unique `MSG` that gives us the correct value. However, recall that the two messages must be unique. We've already found the one data combination that does it for a single 8 byte data block (you can check that each block pair is unique, there are not multiple solutions for each block pair). So we'll need a longer data input for `MSG2`. We know the output after the first data block, so let's start there and add another data block to `MSG2`, i.e. if `MSG1 = '1d3f42283b543cdb'`, then `MSG2 = '1d3f42283b543cdb????????????????'` and figure out the values of `?`s. 

So for this longer `MSG`, the `hash` function will iterate a second time. After the first iteration, `state = [168, 168, 168, 168, 168, 168, 168, 168]`. Run through `sub`, it will pick out the same element from `SBOX` at each position, so we get `state = [0, 0, 0, 0, 0, 0, 0, 0]`. This will be the `state` input to `mix`. Again, we know the output of `mix` must be `[168, 168, 168, 168, 168, 168, 168, 168]`, so we are trying to find the data block that will do this, to fill in the `?`.

We can run the same brute force with our new state vector:

```python
#state array after subbing in SBOX values from position 168
substate2 = [0, 0, 0, 0, 0, 0, 0, 0]

# second block we are trying to figure out
block2 = [0 for i in range(8)]

# same brute force algorithm, with the new substate2
for ind in range(4):
    for i in range(255):
        for j in range(255):
            currstate1 = mixtest(i, j, substate2[ind])
            currstate2 = mixtest(j, i, substate2[7-ind])
            if (currstate1 == 168) and (currstate2 == 168):

                block2[ind] = i
                block2[7-ind] = j
                
print(block2)

[168, 168, 168, 168, 168, 168, 168, 168]
```

Translating to a hex string:
```python
''.join([hex(x)[2:] for x in block2])

'a8a8a8a8a8a8a8a8'
```

So `MSG2 = '1d3f42283b543cdba8a8a8a8a8a8a8a8'`. We can check this produces the correct hash:

```python
MSG = '1d3f42283b543cdba8a8a8a8a8a8a8a8'
MSG = bytes.fromhex(MSG.strip())

MSG = pad(MSG)

H = hash(MSG)

print(H)

'0000000000000000'
```

We use the provided `netcat` command to connect to the server, enter these two hex numbers, finally getting the flag:

```
 ____  __  __ ____        _   _    _    ____  _   _
/ ___||  \/  / ___|      | | | |  / \  / ___|| | | |
\___ \| |\/| \___ \ _____| |_| | / _ \ \___ \| |_| |
 ___) | |  | |___) |_____|  _  |/ ___ \ ___) |  _  |
|____/|_|  |_|____/      |_| |_/_/   \_\____/|_| |_|


Can you even Collide?
First message : 1d3f42283b543cdb
Second message : 1d3f42283b543cdba8a8a8a8a8a8a8a8
H(MSG1) = 0000000000000000
H(MSG2) = 0000000000000000
Good job, Here's your reward:
3k{1s_this_even_4_ha$h?_6b3c1686f7bf87}
```

**Flag:** `3k{1s_this_even_4_ha$h?_6b3c1686f7bf87}`