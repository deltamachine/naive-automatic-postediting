import sys
from collections import Counter


def find_bidix(postedits):
	entries = []

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
					entrie = '%s\t%s\t%s\t' % (source[i], mt[i], target[i])
					entries.append(entrie)

	counter = Counter()

	for entrie in entries:
		counter[entrie] += 1

	print(counter.most_common(10))


def main():
	postedits = sys.argv[1]

	with open(postedits, 'r', encoding='utf-8') as file:
		postedits = file.read().strip('\n').split('\n')

	find_bidix(postedits)


if __name__ == '__main__':
	main()