import os

inputfile = open('output2.txt', 'r')
falsecount = 0
lines = []

for line in inputfile:
	lines.append(line.strip())

inputfile.close()

output = open("outputfalse.txt", "w")

for counter in range(len(lines)):
	
	if lines[counter] == 'false':
		falsecount+=1
		content = lines[counter-1]
		tag = lines[counter]
		output.write(content + '\n')
		output.write(tag + '\n')
		print counter

	if falsecount == 10100:
		break

print falsecount	
