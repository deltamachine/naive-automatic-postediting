import sys
from collections import Counter


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

#приведи это говно в порядок, смотреть больно
def find_bidix(postedits, prefix):
	bidix_entries = []
	grammar_entries = []
	other_entries = {}

	for elem in postedits:
		elem = elem.split('\',')

		for i in range(len(elem)):
			elem[i] = elem[i].strip('(')
			elem[i] = elem[i].strip(')')
			elem[i] = elem[i].strip(' ')
			elem[i] = elem[i].strip('\'')

		try:
			source = elem[0].split(' ')
			mt = elem[1].split(' ')
			target = elem[2].split(' ')
		except:
			pass
			#хуйня с апострофами

		if len(source) == len(mt) and len(mt) == len(target):
			for i in range(len(mt)):
				if '*' in mt[i]:
					bidix_entrie = '%s\t%s\t%s\t' % (source[i], mt[i], target[i])
					bidix_entries.append(bidix_entrie) 

					continue

				dis = distance(mt[i], target[i])
				letters = len(target[i])

				if letters != 0:
					edits_percent = ((letters - dis) / letters) * 100
				else:
					edits_percent = 0

				if edits_percent >= 50 and edits_percent < 100:
					grammar_entrie = '%s\t%s\t%s\t' % (source[i], mt[i], target[i])
					grammar_entries.append(grammar_entrie)
					#print(source)
				elif mt[i] != target[i]: 
					other_entrie = '%s\t%s\t%s\t' % (source[i], mt[i], target[i])
					
					if source[i] not in other_entries.keys():
						other_entries[source[i]] = {}
						other_entries[source[i]][mt[i]] = Counter()
						other_entries[source[i]][mt[i]][target[i]] = 1
					else:
						if mt[i] not in other_entries[source[i]].keys():
							other_entries[source[i]][mt[i]] = Counter()
							other_entries[source[i]][mt[i]][target[i]] = 1
						else:
							if target[i] not in other_entries[source[i]][mt[i]].keys():
								other_entries[source[i]][mt[i]][target[i]] = 1
							else:
								other_entries[source[i]][mt[i]][target[i]] += 1	
				else:
					continue	

	bidix_counter = Counter()
	grammar_counter = Counter()

	for entrie in bidix_entries:
		bidix_counter[entrie] += 1

	for entrie in grammar_entries:
		grammar_counter[entrie] += 1

	with open(prefix + '-bidix_entries.txt', 'w', encoding='utf-8') as file:
		for elem in bidix_counter.most_common():
			file.write('%s%s\n' % (elem[0], str(elem[1])))

	with open(prefix + '-grammar_entries.txt', 'w', encoding='utf-8') as file:
		for elem in grammar_counter.most_common():
			file.write('%s%s\n' % (elem[0], str(elem[1])))

	for key, value in other_entries.items():
		if len(value.keys()) > 1:
			for sec_key, sec_value in value.items():
				if len(sec_value.keys()) > 1:
					v = sum(sec_value.values())
					mc = sec_value.most_common(1)

					if mc[0][1] * 100 / v > 50 and v > 7:
						print(key, sec_key, mc[0][0], mc[0][1], v, mc[0][1] * 100 / v)


def main():
	postedits = sys.argv[1]
	prefix = sys.argv[2]

	with open(postedits, 'r', encoding='utf-8') as file:
		postedits = file.read().strip('\n').split('\n')

	find_bidix(postedits, prefix)


if __name__ == '__main__':
	main()