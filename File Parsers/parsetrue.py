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
		output.write(content + '\n')
		output.write(lines[counter] + '\n')
		print counter

print truecount	
