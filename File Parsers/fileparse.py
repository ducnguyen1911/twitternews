import os

inputfile = open('dataset3.txt', 'r')

lines = []

for line in inputfile:
	lines.append(line.strip())

inputfile.close()

output = open("output.txt", "w")

for counter in range(len(lines)):
	print counter
	content = lines[counter]
	content.strip()
	content2 = content.replace("'", "")
	content2 = content2.replace('"', '')
	if lines[counter] == '':
		counter = counter + 2
		print "line skipped"
	else:
		output.write(content2 + '\n')
