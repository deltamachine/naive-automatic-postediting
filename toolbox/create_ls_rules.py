import re
import pipes
import json
import argparse
import string
from streamparser import parse
from nltk.tokenize import word_tokenize as tokenizer


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='Algorithm for extracting and writing lexical selection rules') 
parser.add_argument('postedits', help='File with postedits')
parser.add_argument('s_lang', help='Source language')
parser.add_argument('t_lang', help='Target language')
parser.add_argument('path', help='Path to Apertium language pair')


args = parser.parse_args()


"""
===================== Main code section =================================
"""


def tag_corpus(input_file, output_file, s_lang, t_lang, path, data_type):
	pipe = pipes.Template()

	if data_type == 'source':
		command = 'apertium -d ' + path + ' ' + s_lang + '-' + t_lang + '-morph'
	else:
		command = 'apertium -d ' + path + ' ' + t_lang + '-' + s_lang + '-morph'
	
	pipe.append(command, '--')
	pipe.append('apertium-pretransfer', '--')
	pipe.copy(input_file, output_file)


def process_postedits(postedits):
	with open(postedits, 'r', encoding='utf-8') as file:
		pe_context = json.load(file)

	return pe_context


def distance(a, b):
	"""Calculates the Levenshtein distance between string a and string b."""

	n, m = len(a), len(b)

	if n > m:
		a, b = b, a
		n, m = m, n

	current_row = range(n + 1)

	for i in range(1, m + 1):
		previous_row, current_row = current_row, [i] + [0] * n

		for j in range(1, n + 1):
			add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
			
			if a[j - 1] != b[i - 1]:
				change += 1

			current_row[j] = min(add, delete, change)

	return current_row[n]


def calculate_metric(source, target):
	dis = distance(source, target)
	letters1 = len(source)
	letters2 = len(target)
	metric1 = (letters1 - dis) / letters1 * 100
	metric2 = (letters2 - dis) / letters2 * 100	

	return metric1, metric2


def find_rules(postedits, s_lang, t_lang, input1, input2):
	with open(input1, 'w', encoding='utf-8') as file1, open(input2, 'w', encoding='utf-8') as file2:
		for key, value in postedits.items():
			s = key.split('\t')[0]
			mt = key.split('\t')[1]
			pe = key.split('\t')[2]

			s_context = value[0]
			metric1, metric2 = calculate_metric(mt, pe)

			#print(s, mt, pe, metric1, metric2)

			if 0 <= metric1 <= 50 and 0 <= metric2 <= 50:
				for cont in s_context:
					file1.write('%s\t%s\n' % (cont[0], cont[1]))

				file1.write('\n')
				file2.write('%s\t%s\n' % (s, pe))


def clean_parsed_word(word):
	if len(re.findall('\/\*', word)) > 1:
		word = re.search('\/\*(.*?)\/\*', word).group(1)
		word = re.sub('\$', '', word)
		word = re.sub('\^', '', word)
		word = '^' + word + '/*' + word + '$'

	return word


def parse_string(string):
	units = parse(c for c in string)

	for unit in units:
		lemma = unit.readings[0][0][0]
		pos = unit.readings[0][0][1]
	
	try:
		if pos == []:
			pos = '*'
		else:
			pos = pos[0] + '.*'
	except:
		lemma = string.split('/')[0]
		pos = '*'

	return lemma.strip('*'), pos


def process_tagged_words(output1, output2):
	with open(output1, 'r', encoding='utf-8') as file1:
		output1 = file1.read().strip('\n').split('\n\n')

	with open(output2, 'r', encoding='utf-8') as file2:
		output2 = file2.read().strip('\n').split('\n')

	draft_rules = {}

	for context, words in zip(output1, output2):
		#print(context, words)
		if words == '^./.<sent>$':
			continue

		context = context.split('\n')
		words = re.sub('\^\./\.\<sent\>\$', '', words)
		words = words.split('\t')

		#print(words)

		s = clean_parsed_word(words[0])	
		pe = clean_parsed_word(words[1])

		s_lemma, s_pos = parse_string(s)
		pe_lemma, pe_pos = parse_string(pe)

		key = tuple([s_lemma, s_pos, pe_lemma, pe_pos])
		draft_rules[key] = [[], []]

		for c in context:
			c = c.split('\t')	
			l_context = clean_parsed_word(c[0])
			r_context = clean_parsed_word(c[1])

			l_lemma, l_pos = parse_string(l_context)
			r_lemma, r_pos = parse_string(r_context)	

			if l_lemma not in draft_rules[key][0]:
				draft_rules[key][0] += [l_lemma, l_pos]

			if r_lemma not in draft_rules[key][1]:
				draft_rules[key][1] += [r_lemma, r_pos]	

	return draft_rules


def clean_context(context):
	cleaned = []

	for c in context:
		if c not in string.punctuation and c != 'sent.*' and c != 'cm.*' and c != '..':
			cleaned.append(c)

	return cleaned


def write_rules(draft_rules, s_lang, t_lang):
	with open('%s-%s_lex-sel-rules.txt' % (s_lang, t_lang), 'w', encoding='utf-8') as file:
		for key, value in draft_rules.items():
			lc = clean_context(value[0])
			rc = clean_context(value[1])

			#print(key, lc, rc)

			if lc != []:
				file.write('<rule>\n')
				
				if len(lc) > 2:
					file.write('  <or>\n')

					for i in range(0, len(lc)-1, 2):
						file.write('    <match lemma="%s" tags="%s"/>\n' % (lc[i], lc[i+1]))
					
					file.write('  </or>\n')
				if len(lc) == 2:
					file.write('  <match lemma="%s" tags="%s"/>\n' % (lc[0], lc[1]))

				file.write('  <match lemma="%s" tags="%s">\n' % (key[0], key[1]))
				file.write('    <select lemma="%s" tags="%s"/>\n' % (key[2], key[3]))
				file.write('  </match>\n</rule>\n\n')

			if rc != []:
				#print(rc)
				file.write('<rule>\n')
				file.write('  <match lemma="%s" tags="%s">\n' % (key[0], key[1]))
				file.write('    <select lemma="%s" tags="%s"/>\n' % (key[2], key[3]))
				file.write('  </match>\n')

				if len(rc) > 2:
					file.write('  <or>\n')

					for i in range(0, len(rc)-1, 2):
						file.write('    <match lemma="%s" tags="%s"/>\n' % (rc[i], rc[i+1]))
					
					file.write('  </or>\n')
				if len(rc) == 2:
					file.write('  <match lemma="%s" tags="%s"/>\n' % (rc[0], rc[1]))

				file.write('</rule>\n\n')


def create_lr_rules(postedits, s_lang, t_lang, path):
	input1 = '%s-%s_left_context.txt' % (s_lang, t_lang)
	input2 = '%s-%s_potential_rules.txt' % (s_lang, t_lang)

	output1 = '%s-%s_left_context_tagged.txt' % (s_lang, t_lang)
	output2 = '%s-%s_potential_rules_tagged.txt' % (s_lang, t_lang)

	find_rules(postedits, s_lang, t_lang, input1, input2)

	tag_corpus(input1, output1, s_lang, t_lang, path, 'source')
	tag_corpus(input2, output2, s_lang, t_lang, path, 'target')

	draft_rules = process_tagged_words(output1, output2)
	#print(draft_rules)
	write_rules(draft_rules, s_lang, t_lang)


def main():
	postedits = args.postedits
	s_lang = args.s_lang
	t_lang = args.t_lang
	path = args.path

	postedits = process_postedits(postedits)
	#print(postedits)
	create_lr_rules(postedits, s_lang, t_lang, path)


if __name__ == '__main__':
	main()