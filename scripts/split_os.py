import sys


corpus = sys.argv[1]
output1 = sys.argv[2]
output2 = sys.argv[3]

with open(corpus, 'r', encoding='utf-8') as file:
	corpus = file.read().strip('\n').split('\n')

with open(output1, 'w', encoding='utf-8') as file1, open(output2, 'w', encoding='utf-8') as file2:
	for line in corpus:
		line = line.split('\t')

		file1.write('%s\n' % (line[0]))
		file2.write('%s\n' % (line[1]))
