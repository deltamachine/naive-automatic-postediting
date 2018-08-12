import re
import os
import sys


input_file = sys.argv[1]
eval_path = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as file:
	input_file = file.read().strip('\n')

input_file = re.sub(' \.', '.', input_file)
input_file = re.sub(' ,', ',', input_file)
input_file = re.sub(' \?', '?', input_file)
input_file = re.sub(' !', '!', input_file)
input_file = re.sub(' :', ':', input_file)
input_file = re.sub(' ;', ';', input_file)
input_file = re.sub('" ', '"', input_file)
input_file = re.sub(' "', '"', input_file)
input_file = re.sub('« ', '«', input_file)
input_file = re.sub(' »', '»', input_file)
input_file = re.sub('#', '', input_file)
#input_file = re.sub('MT\t', ' ', input_file)
#input_file = re.sub('T\t', ' ', input_file)
#input_file = re.sub('ED\t', ' ', input_file)

cases = input_file.split('\n\n')
sentences = {}

for elem in cases:
	elem = elem.split('\n')
	pe = elem[-1].strip('T\t')
	sentences[pe] = []

	for line in elem:
		if (line[0] == 'M' or line[0] == 'E') and line != 'ED\t':
			line = line.strip('MT\t')
			line = line.strip('ED\t')
			sentences[pe].append(line)

train_data = {}

for key, value in sentences.items():
	for v in value:
		with open('hyp.txt', 'w', encoding='utf-8') as file1, open('ref.txt', 'w', encoding='utf-8') as file2:
			file1.write('%s\n' % (v))
			file2.write('%s\n' % (key))	

		os.system('perl %s -test hyp.txt -ref ref.txt > eval.txt' % (eval_path))

		with open('eval.txt', 'r', encoding='utf-8') as file:
			file = file.read()

		wer = re.search('\(WER\): (.*?) %\n', file).group(1)
		train_data[v] = wer

with open('output.txt', 'w', encoding='utf-8') as file:
	for key, value in train_data.items():
		file.write('%s\t%s\n' % (key, value))