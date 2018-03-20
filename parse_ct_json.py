import re
import sys
import json
from sklearn.model_selection import train_test_split


def fix_mistakes(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        corpus = file.read()

    corpus = re.sub(',\n,\n,', ',', corpus)
    corpus = re.sub(',\n,', ',', corpus)
    corpus = re.sub('\n\n', '\n', corpus)

    return corpus
      

def write_content(content, file):
    with open(file, 'w', encoding='utf-8') as file:
        for elem in content:
            file.write('%s\n' % (elem))


def parse_corpora(corpus, train_size, test_size):
    full_corpus = json.loads(corpus)

    source, mt, target = [], [], []

    for elem in full_corpus:
        if elem['mt'] and elem['mt']['engine'] == 'Apertium':
            source.append(elem['source']['content'])
            mt.append(elem['mt']['content'])
            target.append(elem['target']['content'])

    s_train, s_test, m_train, m_test, t_train, t_test = train_test_split(
        source, mt, target, test_size=0.2, random_state=42)

    s_train = s_train[:train_size]
    m_train = m_train[:train_size]
    t_train = t_train[:train_size]
    s_test = s_test[:test_size]
    m_test = m_test[:test_size]
    t_test = t_test[:test_size]

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
    train_size = int(sys.argv[2])
    test_size = int(sys.argv[3])
    corpus = fix_mistakes(input_file)
    parse_corpora(corpus, train_size, test_size)


if __name__ == '__main__':
    main()