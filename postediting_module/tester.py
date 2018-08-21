import re
import json
import argparse
from nltk.tokenize import word_tokenize as tokenizer


"""
===================== Global arguments section =================================
"""

parser = argparse.ArgumentParser(description='Tester for postediting module for Apertium pipeline')
parser.add_argument('lang_pair', help='For example, bel-rus')

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
	pe_context = json.load(open(postedits, 'r'))

	return pe_context


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
	string = re.sub('\.\.', '.', string)

	return string


def compare_bd(word, postedits):
	for operation in postedits:
		if word == operation[1]:
			word = operation[2]

	return word


def compare_other(word, prev_word, next_word, postedits):
	for key, value in postedits.items():
		mt = key.split('\t')[1]
		pe = key.split('\t')[2]

		if word == mt:
			context = value[1]

			for c in context:
				if prev_word == c[0] and next_word == c[1]:
					word = pe

	return word


def apply_postedits(mt_string, bd_postedits, grammar_postedits, other_postedits):
	mt_string = re.sub('\.\.', '.', mt_string)
	tokens = tokenizer(mt_string)

	for i in range(len(tokens)):
		try:
			prev_word = tokens[i-1]
		except:
			prev_word = 'None'

		try:
			next_word = tokens[i+1]
		except:
			next_word = 'None'

		tokens[i] = compare_bd(tokens[i], bd_postedits)
		tokens[i] = compare_other(tokens[i], prev_word, next_word, grammar_postedits)
		tokens[i] = compare_other(tokens[i], prev_word, next_word, other_postedits)

	pe_string = ' '.join(tokens)
	pe_string = clean_edited_string(pe_string)

	print(pe_string)


def main():
	lang_pair = args.lang_pair
	mt_string = input()

	bidix_postedits = process_bd_postedits('%s_bidix-entries.txt' % (lang_pair))
	grammar_postedits = process_other_postedits('%s_grammar-context.json' % (lang_pair))
	other_postedits = process_other_postedits('%s_other-context.json' % (lang_pair))

	apply_postedits(mt_string, bidix_postedits, grammar_postedits, other_postedits)


if __name__ == '__main__':
	main()