import sys
import re


input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as file:
	f = file.read()

sentences = re.findall('<tuv xml:lang=".*?"><seg>(.*?)</seg></tuv>', f)

with open(output_file, 'w', encoding='utf-8') as file:
	for i in range(0, len(sentences), 2):
		file.write('%s\t%s\n' % (sentences[i], sentences[i + 1]))
