
# New algorithm: RATIONALE 

This rationale describes new algorithm for learning postediting operations. It is based on the custom alignment algorithm 
which is also described below.

Disclaimer: seems that this algorithm will work okay on close-related languages, but I'm not sure about others.

### Definitions:
 * S : source sentence
 * MT: machine translation system
 * MT(S): machine translation of S
 * PE(MT(S)): post-editing of the machine translation of S, assumed available
 * (s, t): pair of words, where s belongs to S and t belongs to MT(S) or to PE(MT(S))
 * pos(x): position of a word x in a sentence.
 
### Process:
1. Tag S, MT(S) and PE(MT(S)) using Apertium tagger (for example, bel-rus-morph).
2. For S, MT(S) and PE(MT(S)) collect a dictionary, which contains positions of words as keys and tokens + tags as items. 
For example, for a sentence "Цмоки" the dictionary will look like {0: [цмоки, (n, m, aa, sg, nom)]}.
3. Then align S and MT(S) and S and PE(MT(S)) using these dictionaries. 

For every pair of words (s, t), the algorithm calculates two parameters: |pos(s) - pos(t)| and tags_percent. Tags_percent is calculated the following way:
 - if both s and t have no tags, then tags_percent = 100
 - if s or t has no tags, then tags_percent = (l - d) / l * 100, where l = number of letters in t and d = Levenshtein distance betweeen s and t
 - otherwise tags_percent = length(tags_intersection) / length(t) * 100
 
Then  for every s the algorithm checks, if there s = t (for example, Russian and Belarusian both have word "не"), wherein |pos(s) - pos(t)| < 3 and also finds t with max(tags_percent) and min(|pos(s) - pos(t)|). 

If there are s = t, wherein |pos(s) - pos(t)| < 3, the algorithm aligns s and t.

If not, algorithm aligns s and that t, which has max(tags_percent) and min(|pos(s) - pos(t)|).

4. After aligning, find aligned triplets where word in MT(S) != PE(MT(S)). This is our potential operation.

### Usage

```
new_learn_postedits_algorithm.py train.source train.mt train.target source_lang target_lang path_to_language_pair context_window
```

context_window parameter - number of words around the word which should be postedited.


### Example

```
python3 new_learn_postedits_algorithm.py train.be train.mt.ru train.ru bel rus /home/anna/apertium-bel-rus 2
```
