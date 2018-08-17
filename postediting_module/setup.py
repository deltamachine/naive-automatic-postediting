import os
import re
import sys
from shutil import copyfile
from subprocess import check_output


def find_path(dir_name):
    path = check_output('locate ' + dir_name, shell=True)
    path = str(path).split('\\n')
    path = path[0][2:]

    return path


def copy_files(lang_path, apertium_path):
    list_of_files = os.listdir(lang_path)

    for file in list_of_files:
        copyfile(lang_path + '/' + file, apertium_path + '/' + file)


def change_main_modes(apertium_path, main_changes, lang_pair, work_mode):
    main_modes = apertium_path + '/modes.xml'

    with open(main_modes, 'r', encoding='utf-8') as file:
        f = file.read()

    rev_lang_pair = lang_pair.split('-')[1] + '-' + lang_pair.split('-')[0]
    

    if work_mode == 'pe':
        f_splitted = f.split('\n')
        ind = None

        for i in range(len(f_splitted)):
            if '<!--' in f_splitted[i]:
                ind = i
            if rev_lang_pair in f_splitted[i]:
                break

        f = ['\n'.join(f_splitted[:ind]), main_changes, '\n'.join(f_splitted[ind:])]
        f = '\n'.join(f)

    else:
        f = re.sub(main_changes, '', f) 

    with open(main_modes, 'w', encoding='utf-8') as file:
        file.write(f)


def change_other_modes(apertium_path, other_changes, lang_pair, work_mode):
    main_mode = apertium_path + '/modes/%s.mode' % (lang_pair)
    pe_mode = apertium_path + '/modes/%s-posteditor.mode' % (lang_pair)

    with open(main_mode, 'r', encoding='utf-8') as file:
        f = file.read().strip(' \n')

    if work_mode == 'pe':
        f = f + other_changes
    else:
        f = '|'.join(f.split('|')[:-1])

    with open(main_mode, 'w', encoding='utf-8') as file:
        file.write(f)

    with open(pe_mode, 'w', encoding='utf-8') as file:
        file.write(f)


def main():
    work_mode = sys.argv[1]
    lang_pair = sys.argv[2]

    apertium_path = find_path('apertium-%s' % (lang_pair))
    python_path = sys.executable

    main_changes = '  <mode name="%s-posteditor" install="no">\n    <pipeline>\n        <program name="%s">\n            <file name="posteditor.py"/>\n        </program>\n    </pipeline>\n  </mode>\n\n' % (lang_pair, python_path)
    other_changes = ' | %s \'%s/posteditor.py\'' % (python_path, apertium_path)

    copyfile('posteditor.py', apertium_path + '/posteditor.py')
    copy_files(lang_pair, apertium_path)

    change_main_modes(apertium_path, main_changes, lang_pair, work_mode)
    change_other_modes(apertium_path, other_changes, lang_pair, work_mode)


if __name__ == '__main__':
    main()