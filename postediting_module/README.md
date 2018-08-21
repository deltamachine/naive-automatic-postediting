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
* _path_to_language_pair_: for example, **/home/apertium/apertium-bel-rus**.

This script will install the posteditor and add it to the bel-rus pipeline:

```cmd
$ python3 setup.py pe bel-rus /home/.../apertium-bel-rus
```

And this script will backward changes.

```cmd
$ python3 setup.py raw bel-rus /home/.../apertium-bel-rus
```
#### How it works (examples for Belarusian - Russian)

Example 1:

* Source sentence: _Xуткая шэрая лісіца **пераскаквае** проста праз лянівага сабаку._
* Translation without postediting module: _Быстрая серая лисичка ***пераскаквае** просто через ленивой собаку._
* Translation with postediting module: _Быстрая серая лисичка **перепрыгивает** просто через ленивой собаку._

Example 2:

* Source sentence: _Дом ля **возера** мой._
* Translation without postediting module: _Дом у **озеро** мой._
* Translation with postediting module: _Дом у **озера** мой._

Example 3:

* Source sentence: _Учора вечарам я напісаў **ліст**._
* Translation without postediting module: _Вчера вечером я написал **лист**._
* Translation with postediting module: _Вчера вечером я написал **письмо**._

### Testing

If you want to test posteditor on bel-rus without installing it in the pipeline, you can just run _tester.py_: 

```cmd
$ python3 tester.py bel-rus
```

It will require an input string which should be an output of the raw Apertium pipeline.

Example 1

* Input: _Быстрая серая лисичка ***пераскаквае** просто через ленивой собаку._
* Output: _Быстрая серая лисичка **перепрыгивает** просто через ленивой собаку._

Example 2:

* Input: _Дом у **озеро** мой._
* Output: _Дом у **озера** мой._

Example 3:

* Input: _Вчера вечером я написал **лист**._
* Output: _Вчера вечером я написал **письмо**._
