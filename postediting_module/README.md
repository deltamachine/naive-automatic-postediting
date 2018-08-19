Postediting module for Apertium
===================================

### Installation

#### Prerequisites
1. NLTK package for Python
2. Precompiled language pairs which support the posteditor (bel-rus, rus-ukr, spa-cat)

#### How to install a testpack
NB: currently this testpack contains needed data only for bel-rus.

```cmd
$ git clone https://github.com/deltamachine/naive-automatic-postediting.git
$ cd naive-automatic-postediting/postediting_module
```

Script _setup.py_ adds all the needed files in language pair directory and changes some files with modes.

###### Arguments:

* _work_mode_: **pe** for installing the posteditor and changing modes, **raw** for backwarding changes.
* _language_pair_: for example, **bel-rus**.

This script will install the posteditor and add it to the bel-rus pipeline:

```cmd
$ python3 setup.py pe bel-rus
```

And this script will backward changes.

```cmd
$ python3 setup.py raw bel-rus
```
#### How it works (examples for Belarusian - Russian)

Example 1:

* Source sentence: **Xуткая шэрая лісіца пераскаквае проста праз лянівага сабаку**
* Translation without postediting module: **Быстрая серая лисичка *пераскаквае просто через ленивой собаку**
* Translation with postediting module: **Быстрая серая лисичка перепрыгивает просто через ленивой собаку**

Example 2:

* Source sentence: **У гэтым класе 40 вучняў**
* Translation without postediting module: **В этим классе 40 учеников**
* Translation with postediting module: **В этом классе 40 учеников**

Example 3:

* Source sentence: **Учора вечарам я напісаў ліст**
* Translation without postediting module: **Вчера вечером я написал лист**
* Translation with postediting module: **Вчера вечером я написал письмо**
