import sys
import json
from sklearn.model_selection import train_test_split


def write_content(content, file):
    with open(file, 'w', encoding='utf-8') as file:
        for elem in content:
            file.write(elem)
            file.write('\n')


def parse_corpora(input_file):
    full_corpus = json.load(open(input_file))
    source, mt, target = [], [], []

    for elem in full_corpus:
        if elem['mt'] and elem['mt']['engine'] == 'Apertium':
            source.append(elem['source']['content'])
            mt.append(elem['mt']['content'])
            target.append(elem['target']['content'])

    s_train, s_test, m_train, m_test, t_train, t_test = train_test_split(
        source, mt, target, test_size=0.2, random_state=42)

    print('Size of train set: %s sentences' % (len(s_train)))
    print('Size of test set: %s sentences' % (len(s_test)))

    write_content(s_train, 'en_train.txt')
    write_content(m_train, 'es_mt_train.txt')
    write_content(t_train, 'es_train.txt')
    write_content(s_test, 'en_test.txt')
    write_content(m_test, 'es_mt_test.txt')
    write_content(t_test, 'es_test.txt')


def main():
    input_file = sys.argv[1]

    parse_corpora(input_file)


if __name__ == '__main__':
    main()
