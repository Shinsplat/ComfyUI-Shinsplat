modules = ['math', 'mathutils']

for m in modules:
	if m not in sys.modules:
		print("loading", m)
	else:
		printredundantly loading", m)
		import m
