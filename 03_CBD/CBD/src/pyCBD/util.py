import sys

PYCBD_VERSION = '1.6'
"""The version of the CBD simulator."""

PYTHON_VERSION = sys.version_info[0]
"""The python version of the simulation."""

def enum(**enums):
	"""
	Helper function to construct simple enums.
	"""
	return type('Enum', (), enums)


def hash64(number):
	"""
	Simple hashing function to convert the :func:`id` of an object to a short string.
	This hash is case-sensitive!

	Args:
		number (int):   The number to convert.
	"""
	seq = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$_"
	v1 = number
	B = len(seq)
	rems = []
	while v1 > B:
		v2 = v1 // B
		rems.append(v1 - (v2 * B))
		v1 = v2
	rems.append(v1)
	rems = reversed(rems)
	H = ""
	for r in rems:
		H += seq[int(r)]
	return H

def unhash64(H):
	"""
	Reverse operation of the :func:`hash64` method.

	Args:
		H (str):    The hash to convert back to a number.
	"""
	seq = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$_"
	B = len(seq)
	rems = []
	for c in H:
		rems.append(seq.index(c))
	value = 0
	for r in rems:
		value *= B
		value += r
	return value

if __name__ == '__main__':
	print(hash64(13697856412599))
	print(unhash64("dhvh3zU3"))
