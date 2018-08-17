import re
import argparse
import pipes
import json
from itertools import product
from streamparser import parse
from nltk.tokenize import word_tokenize as tokenizer


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='Algorithm for applying extracted postedits to a test file')
parser.add_argument('source_file', help='Source test data')
parser.add_argument('mt_file', help='Machine-translated test data')
parser.add_argument('target_file', help='Target (postedited) test data') 
parser.add_argument('bidix_postedits', help='File with bidix postedits')
parser.add_argument('grammar_postedits', help='File with grammar postedits')
parser.add_argument('other_postedits', help='File with other postedits')
parser.add_argument('s_lang', help='Source language')
parser.add_argument('t_lang', help='Target language')
parser.add_argument('path', help='Path to Apertium language pair')

args = parser.parse_args()


"""
===================== Main code section =================================
"""


def process_bd_postedits(postedits):
	with open(postedits, 'r', encoding='utf-8') as file:
		file = file.read().strip('\n').split('\n')

	postedits = []

	for line in file:
		line = line.split('\t')[:3]

		if line not in postedits:
			postedits.append(line)

	return postedits


def process_other_postedits(postedits):
	with open(postedits, 'r', encoding='utf-8') as file:
		pe_context = json.load(file)

	return pe_context


def tag_corpus(input_file, output_file, s_lang, t_lang, path, data_type):
	pipe = pipes.Template()

	if data_type == 'source':
		command = 'apertium -d ' + path + ' ' + s_lang + '-' + t_lang + '-morph'
	else:
		command = 'apertium -d ' + path + ' ' + t_lang + '-' + s_lang + '-morph'
	
	pipe.append(command, '--')
	pipe.append('apertium-pretransfer', '--')
	pipe.copy(input_file, output_file)


def open_files(source_file, mt_file, target_file):
	with open(source_file, 'r', encoding='utf-8') as file:
		source = file.read().strip('\n').split('\n')

	with open(mt_file, 'r', encoding='utf-8') as file:
		mt = file.read().strip('\n').split('\n')

	with open(target_file, 'r', encoding='utf-8') as file:
		target = file.read().strip('\n').split('\n')

	with open(source_file + '.tagged', 'r', encoding='utf-8') as file:
		source_tagged = file.read().strip('\n').split('\n')

	with open(mt_file + '.tagged', 'r', encoding='utf-8') as file:
		mt_tagged = file.read().strip('\n').split('\n')

	with open(target_file + '.tagged', 'r', encoding='utf-8') as file:
		target_tagged = file.read().strip('\n').split('\n')	

	return source, mt, target, source_tagged, mt_tagged, target_tagged


def collect(sentence, sentence_tagged):
	sentence_words = {}
	tokens = tokenizer(sentence.lower())

	sentence_tagged = sentence_tagged.split(' ')

	for i in range(len(sentence_tagged)):
		if len(re.findall('\/\*', sentence_tagged[i])) > 1:
			word = re.search('\/\*(.*?)\/\*', sentence_tagged[i]).group(1)
			word = re.sub('\$', '', word)
			word = re.sub('\^', '', word)
			word = '^' + word + '/*' + word + '$'
			sentence_tagged[i] = word

	sentence_tagged = ' '.join(sentence_tagged)

	units = parse(c for c in sentence_tagged)
	counter = 0

	try:
		for unit in units:
			sentence_words[counter] = [tokens[counter], set(unit.readings[0][0][1])]
			counter += 1
	except:
		pass

	return sentence_words


def distance(a, b):
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
	letters = len(target)
	tags_percent =(letters - dis) / letters * 100

	return tags_percent


def fill_options(source, target, t_pos):
	options = {}

	for s_pos in sorted(source.keys()):
		intersection = source[s_pos][1] & target[t_pos][1]

		if len(target[t_pos][1]) == 0 and len(source[s_pos][1]) == 0:
			tags_percent = calculate_metric(source[s_pos][0], target[t_pos][0])

			if tags_percent >= 60:
				tags_percent = 100

		elif len(target[t_pos][1]) == 0 or len(source[s_pos][1]) == 0:
			tags_percent = calculate_metric(source[s_pos][0], target[t_pos][0])

		else:
			tags_percent = len(intersection) / len(target[t_pos][1]) * 100

		options[s_pos] = [tags_percent, abs(s_pos - t_pos)]

	return options


def fill_positions(source, target, t_pos, options):
	position = -1
	percent = -1
	difference = -1
	sim_pos = -1
	sim_dif = 1000

	for o_pos, value in options.items():
		if source[o_pos][0] == target[t_pos][0]:
			if value[1] < sim_dif:
				sim_pos = o_pos
				sim_dif = value[1]

		elif value[0] > percent:
			percent = value[0]
			difference = value[1]
			position = o_pos

		elif value[0] == percent and value[1] < difference:
			difference = value[1]
			position = o_pos

		else:
			continue

	return sim_pos, position, difference


def align(source, target):
	word_alignment = []

	for t_pos in sorted(target.keys()):
		options = fill_options(source, target, t_pos)
		sim_pos, position, difference = fill_positions(source, target, t_pos, options)

		if sim_pos != -1:
			word_alignment.append((source[sim_pos][0], target[t_pos][0]))	
		elif difference > 3:
			continue
		else:
			word_alignment.append((source[position][0], target[t_pos][0]))		
	
	return word_alignment


def prepare_data(source, mt, target, source_tagged, mt_tagged):
	source = source.lower()
	mt = mt.lower()
	target = target.lower()

	source_words = collect(source, source_tagged)
	mt_words = collect(mt, mt_tagged)
	mt_align = align(source_words, mt_words)
	mt_tokens = tokenizer(mt)

	return source, mt, target, mt_align, mt_tokens


def check_bd_postedits(elem, edits, postedits):
	for operation in postedits:
		if elem[0] == operation[0] and elem[1] == operation[1]:
			if elem in edits.keys():
				edits[elem].append(operation)
			else:
				edits[elem] = [operation]

	return edits


def check_other_postedits(elem, edits, other_postedits, mt_tokens):
	for key, value in other_postedits.items():
		pe = key.split('\t')

		if elem[0] == pe[0] and elem[1] == pe[1]:
			ind = mt_tokens.index(pe[1])
			left = mt_tokens[ind - 1]
			right = mt_tokens[ind + 1]

			for item in value[1]:
				if item[0] == left and item[1] == right:

					if elem in edits.keys():
						edits[elem].append(key.split('\t'))
					else:
						edits[elem] = [key.split('\t')]

	return edits


def prepare_variants(edits, mt_tokens):
	combinations = product(*list(edits.values()))
	
	variants, checked = [], []

	for comb in combinations:
		var = []

		for j in range(len(mt_tokens)):
			for elem in comb:
				if mt_tokens[j] == elem[1]:							
					var.append(elem[2])
					checked.append(mt_tokens[j])
				else:
					c = 0

					for elem in edits.keys():
						if mt_tokens[j] in elem:
							c += 1

					if c == 0 and (len(var) == 0 or len(var) > 0 and var[-1] != mt_tokens[j]) and mt_tokens[j] not in checked:
						var.append(mt_tokens[j])
		
		if var not in variants:
			variants.append(var)

	return variants


def clean_edited_string(string):
	string = re.sub(' \.', '.', string)
	string = re.sub(' ,', ',', string)
	string = re.sub(' \?', '?', string)
	string = re.sub(' !', '!', string)
	string = re.sub(' :', ':', string)
	string = re.sub(' ;', ';', string)
	string = re.sub('" ', '"', string)
	string = re.sub(' "', '"', string)
	string = re.sub('« ', '«', string)
	string = re.sub(' »', '»', string)
	string = re.sub('#', '', string)

	return string


def apply_postedits(source, mt, target, source_tagged, mt_tagged, target_tagged, s_lang, t_lang, bd_postedits, gram_postedits, other_postedits):
	with open('%s-%s_corrected.txt' % (s_lang, t_lang), 'w', encoding='utf-8') as file:
		for i in range(len(source)):
			source[i], mt[i], target[i], mt_align, mt_tokens = prepare_data(source[i], mt[i], target[i], source_tagged[i], mt_tagged[i])

			edits = {}

			for elem in mt_align:
				elem = tuple(elem)
				edits = check_bd_postedits(elem, edits, bd_postedits)
				edits = check_other_postedits(elem, edits, gram_postedits, mt_tokens)
				edits = check_other_postedits(elem, edits, other_postedits, mt_tokens)

			variants = prepare_variants(edits, mt_tokens)

			file.write('S\t%s\nMT\t%s\n' % (source[i], mt[i]))

			for var in variants:
				var = ' '.join(var)
				var = clean_edited_string(var)
				file.write('ED\t%s\n' % (var))

			file.write('T\t%s\n\n' % (target[i]))


def main():
	source_file = args.source_file
	mt_file = args.mt_file
	target_file = args.target_file
	bidix_postedits = args.bidix_postedits
	grammar_postedits = args.grammar_postedits
	other_postedits = args.other_postedits
	s_lang = args.s_lang
	t_lang = args.t_lang
	path = args.path

	bidix_postedits = process_bd_postedits(bidix_postedits)
	grammar_postedits = process_other_postedits(grammar_postedits)
	other_postedits = process_other_postedits(other_postedits)

	#print(grammar_postedits)

	tag_corpus(source_file, source_file + '.tagged', s_lang, t_lang, path, 'source')
	tag_corpus(mt_file, mt_file + '.tagged', s_lang, t_lang, path, 'mt')
	tag_corpus(target_file, target_file + '.tagged', s_lang, t_lang, path, 'target')

	source, mt, target, source_tagged, mt_tagged, target_tagged = open_files(source_file, mt_file, target_file)
	
	apply_postedits(source, mt, target, source_tagged, mt_tagged, target_tagged, s_lang, t_lang, bidix_postedits, grammar_postedits, other_postedits)


if __name__ == '__main__':
	main()