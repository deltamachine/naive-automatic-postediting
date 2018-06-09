import re
import sys
from sklearn.model_selection import train_test_split


def write_content(content, file):
    with open(file, 'w', encoding='utf-8') as file:
        for elem in content:
            file.write('%s\n' % (elem.strip(' ')))


def prepare_sets(source, mt, target, source_lang, target_lang):
    with open(source, 'r', encoding='utf-8') as file:
        source = file.read().strip('\n').split('\n')

    with open(mt, 'r', encoding='utf-8') as file:
        mt = file.read().strip('\n').split('\n')

    with open(target, 'r', encoding='utf-8') as file:
        target = file.read().strip('\n').split('\n')

    s_train, s_test, m_train, m_test, t_train, t_test = train_test_split(
        source, mt, target, test_size=0.2, random_state=42)

    write_content(s_train, 'train.' + source_lang)
    write_content(m_train, 'train.mt.' + target_lang)
    write_content(t_train, 'train.' + target_lang)
    write_content(s_test, 'test.' + source_lang)
    write_content(m_test, 'test.mt.' + target_lang)
    write_content(t_test, 'test.' + target_lang)

    print('Size of a train set: %s sentences' % (len(s_train)))
    print('Size of a test set: %s sentences' % (len(s_test)))


def main():
    source = sys.argv[1]
    mt = sys.argv[2]
    target = sys.argv[3]
    source_lang = sys.argv[4]
    target_lang = sys.argv[5]

    prepare_sets(source, mt, target, source_lang, target_lang)


if __name__ == '__main__':
    main()