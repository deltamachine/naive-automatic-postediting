import re
import sys
import pipes
from streamparser import parse


def distance(a, b):
    """Calculates the Levenshtein distance between a and b."""

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


def divide_entries(entries):
	source = []
	mt = []
	target = []
	freqs = []

	for elem in entries:
		elem = elem.split('\t')

		source.append(elem[0])
		mt.append(elem[1])
		target.append(elem[2])
		freqs.append(elem[3])

	with open('source_entries.txt', 'w', encoding='utf-8') as file:
		for elem in source:
			file.write('%s\n' % (elem))

	with open('mt_entries.txt', 'w', encoding='utf-8') as file:
		for elem in mt:
			file.write('%s\n' % (elem))

	with open('target_entries.txt', 'w', encoding='utf-8') as file:
		for elem in target:
			file.write('%s\n' % (elem))

	return source, mt, target, freqs


def tag_entries(input_file, output_file, s_lang, t_lang, path, data_type):
    pipe = pipes.Template()

    if data_type == 'source':
    	command = 'apertium -d ' + path + ' ' + s_lang + '-' + t_lang + '-morph'
    else:
    	command = 'apertium -d ' + path + ' ' + t_lang + '-' + s_lang + '-morph'
    
    pipe.append(command, '--')
    pipe.append('apertium-pretransfer', '--')
    pipe.copy(input_file, output_file) 


def bla(word):
	if len(re.findall('\/\*', word)) > 1:
		word = re.search('\/\*(.*?)\/\*', word).group(1)
		word = re.sub('\$', '', word)
		word = re.sub('\^', '', word)
		word = '^' + word + '/*' + word + '$'
	
	return word


def clean_trash(orig_source, orig_mt, orig_target, freqs, s_lang, t_lang, input_file):
	with open('tagged_source_entries.txt', 'r', encoding='utf-8') as file:
		source = file.read().strip('\n').split('\n')

	with open('tagged_mt_entries.txt', 'r', encoding='utf-8') as file:
		mt = file.read().strip('\n').split('\n')

	with open('tagged_target_entries.txt', 'r', encoding='utf-8') as file:
		target = file.read().strip('\n').split('\n')	

	for i in range(len(source)):
		source[i] = bla(source[i])

	for i in range(len(mt)):
		mt[i] = bla(mt[i])

	for i in range(len(target)):
		target[i] = bla(target[i])

	counter = 0

	with open(s_lang + '-' + t_lang + '-cleaned_' + input_file, 'w', encoding='utf-8') as file:	
		for s, m, t in zip(source, mt, target):
			s_units = parse(c for c in s)
			m_units = parse(c for c in m)
			t_units = parse(c for c in t)

			for su, mu, tu in zip(s_units, m_units, t_units):
				for sr, mr, tr in  zip(su.readings, mu.readings, tu.readings):
					s_lemma = sr[0][0]
					m_lemma = mr[0][0]
					t_lemma = tr[0][0]

					s_tags = sr[0][1]
					m_tags = mr[0][1]
					t_tags = tr[0][1]

					if 'lquot' in t_tags or 'sent' in t_tags or 'rquot' in t_tags or 'cm' in t_tags or 'guio' in t_tags: 
						pass
					elif 'lquot' in s_tags or 'sent' in s_tags or 'rquot' in s_tags or 'cm' in s_tags or 'guio' in s_tags: 
						pass
					else:
						st_dis = distance(s_lemma, t_lemma)
						st_letters = len(t_lemma)
						st_percent = (st_letters - st_dis) / st_letters * 100

						sm_dis = distance(s_lemma, m_lemma)
						sm_letters = len(m_lemma)
						sm_percent = (sm_letters - sm_dis) / sm_letters * 100

						mt_dis = distance(m_lemma, t_lemma)
						mt_letters = len(t_lemma)
						mt_percent = (mt_letters - mt_dis) / mt_letters * 100

						if st_percent >= 30 and sm_percent >= 30 and mt_percent >= 30 and 'other' not in input_file:
							file.write('%s\t%s\t%s\t%s\n' % (orig_source[counter], orig_mt[counter], orig_target[counter], freqs[counter]))
						elif 'other' in input_file:
							file.write('%s\t%s\t%s\t%s\n' % (orig_source[counter], orig_mt[counter], orig_target[counter], freqs[counter]))
						else:
							pass

			
			counter += 1

def main():
	input_file = sys.argv[1]
	s_lang = sys.argv[2]
	t_lang = sys.argv[3]
	path = sys.argv[4]

	with open(input_file, 'r', encoding='utf-8') as file:
		entries = file.read().strip('\n').split('\n')

	orig_source, orig_mt, orig_target, freqs = divide_entries(entries)

	tag_entries('source_entries.txt', 'tagged_source_entries.txt', s_lang, t_lang, path, 'source')
	tag_entries('mt_entries.txt', 'tagged_mt_entries.txt', s_lang, t_lang, path, 'mt')
	tag_entries('target_entries.txt', 'tagged_target_entries.txt', s_lang, t_lang, path, 'target')

	clean_trash(orig_source, orig_mt, orig_target, freqs, s_lang, t_lang, input_file)	



if __name__ == '__main__':
	main()