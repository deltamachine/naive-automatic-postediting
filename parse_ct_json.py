import re
import sys
import json
from sklearn.model_selection import train_test_split
from nltk import sent_tokenize


def fix_mistakes(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        corpus = file.read()

    corpus = re.sub(',\n,\n,', ',', corpus)
    corpus = re.sub(',\n,', ',', corpus)
    corpus = re.sub('\n\n', '\n', corpus)
    corpus = re.sub('\[[0-9]+\]', '', corpus)

    return corpus
      

def write_content(content, file):
    with open(file, 'w', encoding='utf-8') as file:
        for elem in content:
            file.write('%s\n' % (elem.strip(' ')))


def parse_corpus(corpus):
    full_corpus = json.loads(corpus)

    source, mt, target = [], [], []

    for elem in full_corpus:
        if elem['mt'] and elem['mt']['engine'] == 'Apertium':
            s = sent_tokenize(elem['source']['content'])
            m = sent_tokenize(elem['mt']['content'])
            t = sent_tokenize(elem['target']['content'])

            if len(s) == len(m) and len(s) == len(t):
                source += s
                mt += m
                target += t

    print('Size of the whole sentence-aligned corpus: %s sentences' % (len(source)))

    return source, mt, target


def prepare_sets(source, mt, target, source_lang, target_lang, train_size, test_size):
    s_train, s_test, m_train, m_test, t_train, t_test = train_test_split(
        source, mt, target, test_size=0.2, random_state=12345)

    if train_size != 'default' and test_size != 'default':
        train_size, test_size = int(train_size), int(test_size)
        s_train = s_train[:train_size]
        m_train = m_train[:train_size]
        t_train = t_train[:train_size]
        s_test = s_test[:test_size]
        m_test = m_test[:test_size]
        t_test = t_test[:test_size]

    write_content(s_train, source_lang + '_train.txt')
    write_content(m_train, target_lang + '_mt_train.txt')
    write_content(t_train, target_lang + '_train.txt')
    write_content(s_test, source_lang + '_test.txt')
    write_content(m_test, target_lang + '_mt_test.txt')
    write_content(t_test, target_lang + '_test.txt')


def main():
    input_file = sys.argv[1]
    source_lang = sys.argv[2]
    target_lang = sys.argv[3]
    train_size = sys.argv[4]
    test_size = sys.argv[5]

    corpus = fix_mistakes(input_file)
    source, mt, target = parse_corpus(corpus)
    prepare_sets(source, mt, target, source_lang, target_lang, train_size, test_size)


if __name__ == '__main__':
    main()
