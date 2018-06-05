# Naïve automatic postediting

Discontinued code that learns some naïve postediting operators from existing postediting runs.
The code may work but is not completely documented. The code was generated in connection with the PhD thesis of Assem Abeustanova (née Shormakova), which is now stalled.

There may be some undocumented files and options: some cleanup is needed. The project may be recovered if someone resumes development. 

## cleaned_learn_postedits.py

```
usage: cleaned_learn_postedits.py [-h] [-v] [-m MAXSOURCELENGTH]
                          [-M MAXTRANSLATIONLENGTH] [-d DIRECTORY] [-t] [-i]
                          [-o OUTPUT]
                          sourceLanguage targetLanguage text_in_fn hyp_in_fn
                          ref_in_fn hyp_out_fn ref_out_fn fmt
```
This programme the name of two languages, a source file (one sentence per line), a machine-translated file (one sentence per line), a postedited version of that file (one sentence per line), and a fuzzy match threshold (e.g. 0.8) below which postedits are not considered. Then one specifies a maximum source segment length (-m), a maximum target segment length (-M), the directory where an Apertium machine translation system is found (-d) and an output file (-o).

Example:
```
python3 cleaned_learn_postedits.py eng kaz 1withtatoe.en 1withtatoe.mt.kk 1withtatoe.kk 0.8 -m 3 -M 3 -o operations.txt -d ~/apertium-sources/apertium-eng-kaz
```

The programme contains some code written by Pankaj Sharma [https://github.com/pankajksharma/py-apertium] back in 2014.

The program translates all segments of 1, 2... MAXSOURCELENGTH words using an Apertium system, and tries to find them in the machine-translated sentence. For those found, it aligns the resulting segments with those in the postedited/reference sentence to build postediting operators (*s*,*m*,*t*) where *s* is the source segment, *m* is the Apertium translation and *t* the postedited/reference segment, which could then be applied to a machine-translated sentence to postedited. There is a better explanation in document rationale.md  in this repository.

## apply_postedits.py

This would read the output of cleaned_learn_postedits.py  and apply the result to a series of source texts.

```
usage: apply_postedits.py [-h] [-m MAXSOURCELENGTH] [-M MAXTRANSLATIONLENGTH]
                          [-d DIRECTORY] [-t] [-i] [-o OPERATORS] [-v] [--go]
                          [-f SOURCE_TEXTS]
                          sourceLanguage targetLanguage```
```

## parse_ct_json.py

```
usage: parse_ct_json.py json_input train_size test_size
```
This script parses Mediawiki JSON file with source, Apertium translated and postedited artiles and prepares train and test sets of a given size for cleaned_learn_postedits.py and apply_postedits.py.

Example:
```
python3 parse_ct_json.py en2es.json 1000 200
```

## estimate_changes.py

```
usage: estimate_changes.py file_with_sentences language_model
```
This script takes file with output from apply_postedits.py, scores original Apertium translated sentence and sentences which were processed with postediting operations on a language model and stores scores in scores.txt

Example:
```
python3 estimate_changes.py sentences.txt esp-europarl.arpa
```
