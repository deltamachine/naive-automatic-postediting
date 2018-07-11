
# New algorithm: RATIONALE 

This rationale describes new algorithm for learning postediting operations. It is based on the custom alignment algorithm 
which is also described below.

### Definitions:
 * S : source sentence
 * MT: machine translation system
 * MT(S): machine translation of S
 * PE(MT(S)): post-editing of the machine translation of S, assumed available
 
### Process:
1. Tag S, MT(S) and PE(MT(S)) using Apertium tagger (for example, bel-rus-morph).
2. For S, MT(S) and PE(MT(S)) collect a dictionary, which contains positions of words as keys and tokens + tags as items. 
For example, for a sentence "Цмоки" the dictionary will look like {0: [цмоки, (<n>, <m>, <aa>, <sg>, <nom>)]}.
3. Then align S and MT(S) and S and PE(MT(S)) using these dictionaries:
