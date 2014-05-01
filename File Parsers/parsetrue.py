import os

inputfile = open('output2.txt', 'r')
truecount = 0
lines = []

for line in inputfile:
	lines.append(line.strip())

inputfile.close()

output = open("outputtrue.txt", "w")

for counter in range(len(lines)):
	
	if lines[counter] == 'true':
		truecount+=1
		content = lines[counter-1]
		tag = lines[counter]
		output.write(content + '\n')
		output.write(tag + '\n')
		print counter

print truecount	
