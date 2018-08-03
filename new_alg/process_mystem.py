import sys
from pymystem3 import Mystem


input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as file:
	words = file.read().strip('\n')

m = Mystem()
analysis = m.analyze(words)

with open(output_file, 'w', encoding='utf-8') as file:
	for elem in analysis:
		if elem['text'] != ' ' and elem['text'] != '\n':
			try:
				token = elem['text']
				lemma = elem['analysis'][0]['lex']
				pos_tag = elem['analysis'][0]['gr'].split(',')[0].split('=')[0]
				info = '%s\t%s\t%s\n' % (token, lemma, pos_tag)
				file.write(info)
			except:
				pass