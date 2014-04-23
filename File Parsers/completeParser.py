import os

inputfile = open('output.txt', 'r')

lines = []

for line in inputfile:
	lines.append(line.strip())

inputfile.close()

output = open("output2.txt", "w")

for counter in range(len(lines)):

	if lines[counter] == 'false' and lines[counter+1] == 'false' and lines[counter+2] != 'false':
		content = lines[counter+2]
		content.strip()
		content2 = content.replace("'", "")
		content2 = content2.replace('"', '')
		output.write(lines[counter])
		output.write(content2 + '\n')
		output.write(lines[counter+1])
		counter+=2




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
