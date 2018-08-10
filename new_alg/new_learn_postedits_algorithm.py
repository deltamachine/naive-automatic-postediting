import re
import sys
import pipes
from streamparser import parse
from nltk.tokenize import word_tokenize as tokenizer


def tag_corpus(input_file, output_file, s_lang, t_lang, path, data_type):
	"""
	Tag given corpus using apertium-tagger
	"""

	pipe = pipes.Template()

	if data_type == 'source':
		command = 'apertium -d ' + path + ' ' + s_lang + '-' + t_lang + '-morph'
	else:
		command = 'apertium -d ' + path + ' ' + t_lang + '-' + s_lang + '-morph'
	
	pipe.append(command, '--')
	pipe.append('apertium-pretransfer', '--')
	pipe.copy(input_file, output_file)


def open_files(source_file, mt_file, target_file):
	"""
	Open and read all the needed files.
	"""

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
	"""
	Collect a dictionary, which contains positions of sentence words as keys
	and tokens + tags as items. 
	"""

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

	for unit in units:
		sentence_words[counter] = [tokens[counter], set(unit.readings[0][0][1])]
		counter += 1

	return sentence_words


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


def fill_options(source, target, t_pos):
	"""
	Go through every word in source sentence and compares it
	with a given word in a target sentence. It calculates two numbers:
		- ta
	"""

	options = {}

	for s_pos in sorted(source.keys()):
		intersection = source[s_pos][1] & target[t_pos][1]

		if len(target[t_pos][1]) == 0 and len(source[s_pos][1]) == 0:
			tags_percent = 100

		elif len(target[t_pos][1]) == 0 or len(source[s_pos][1]) == 0:
			dis = distance(source[s_pos][0], target[t_pos][0])
			letters = len(target[t_pos][0])
			tags_percent = (letters - dis) / letters * 100

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
	"""
	Align source and target sentences.
	"""

	pos_alignment = []
	word_alignment = []

	for t_pos in sorted(target.keys()):
		options = fill_options(source, target, t_pos)
		sim_pos, position, difference = fill_positions(source, target, t_pos, options)

		if sim_pos != -1:
			pos_alignment.append((sim_pos, t_pos))
			word_alignment.append((source[sim_pos][0], target[t_pos][0]))	

		elif difference > 3:
			continue

		else:
			pos_alignment.append((position, t_pos))
			word_alignment.append((source[position][0], target[t_pos][0]))		
	
	return word_alignment


def find_postedits(source, mt, target, source_tagged, mt_tagged, target_tagged, cont_wind):
	"""
	Collect a list of potential postedits.
	"""

	postedits = []

	for i in range(len(source)):
		try:
			source_words = collect(source[i], source_tagged[i])
			mt_words = collect(mt[i], mt_tagged[i])
			target_words = collect(target[i], target_tagged[i])

			mt_align = align(source_words, mt_words)
			target_align = align(source_words, target_words)

			len_mt = len(mt_align)
			len_tar = len(target_align)

			for j in range(len(mt_align)):
				a = j - cont_wind
				b = len_mt - j - 1

				for k in range(len(target_align)):
					c = k - cont_wind
					d = len_tar - k - 1

					if mt_align[j][0] == target_align[k][0] and mt_align[j][1] != target_align[k][1]:
						if a <= 0 and c <= 0 and b > cont_wind and d > cont_wind:
							elem1 = ' '.join([elem[0] for elem in mt_align[0:j+cont_wind+1]])
							elem2 = ' '.join([elem[1] for elem in mt_align[0:j+cont_wind+1]])
							elem3 = ' '.join([elem[1] for elem in target_align[0:k+cont_wind+1]])

						elif a <= 0 and c <= 0 and b <= cont_wind and d <= cont_wind:
							elem1 = ' '.join([elem[0] for elem in mt_align])
							elem2 = ' '.join([elem[1] for elem in mt_align])
							elem3 = ' '.join([elem[1] for elem in target_align])

						elif a > 0 and c > 0 and b <= cont_wind and d <= cont_wind:
							elem1 = ' '.join([elem[0] for elem in mt_align[a:j]]) + ' ' + ' '.join([elem[0] for elem in mt_align[j:]])
							elem2 = ' '.join([elem[1] for elem in mt_align[a:j]]) + ' ' + ' '.join([elem[1] for elem in mt_align[j:]])
							elem3 = ' '.join([elem[1] for elem in target_align[c:k]]) + ' ' + ' '.join([elem[1] for elem in target_align[k:]])

						else:
							elem1 = ' '.join([elem[0] for elem in mt_align[a:j]]) + ' ' + ' '.join([elem[0] for elem in mt_align[j:j+cont_wind+1]])
							elem2 = ' '.join([elem[1] for elem in mt_align[a:j]]) + ' ' + ' '.join([elem[1] for elem in mt_align[j:j+cont_wind+1]])
							elem3 = ' '.join([elem[1] for elem in target_align[c:k]]) + ' ' + ' '.join([elem[1] for elem in target_align[k:k+cont_wind+1]])

						postedits.append((elem1, elem2, elem3))
		except:
			pass

	return postedits


def main():
	source_file = sys.argv[1]
	mt_file = sys.argv[2]
	target_file = sys.argv[3]
	s_lang = sys.argv[4]
	t_lang = sys.argv[5]
	path = sys.argv[6]
	cont_wind = int(sys.argv[7])

	tag_corpus(source_file, source_file + '.tagged', s_lang, t_lang, path, 'source')
	tag_corpus(mt_file, mt_file + '.tagged', s_lang, t_lang, path, 'mt')
	tag_corpus(target_file, target_file + '.tagged', s_lang, t_lang, path, 'target')

	source, mt, target, source_tagged, mt_tagged, target_tagged = open_files(source_file, mt_file, target_file)
	postedits = find_postedits(source, mt, target, source_tagged, mt_tagged, target_tagged, cont_wind)
	
	with open(s_lang + '-' + t_lang + '-postedits.txt', 'w', encoding='utf-8') as file:
		for elem in postedits:
			file.write('%s\n' % (str(elem)))


if __name__ == '__main__':
	main()