import copy
from random import shuffle

import abjad

# generate a random tone row

BASE_ROW = list(range(12))
randomized_row = copy.deepcopy(BASE_ROW)
shuffle(randomized_row)
tone_row = abjad.TwelveToneRow(items=randomized_row)
reformatted = [tone.pitch_class_label().lower() for tone in tone_row.items]
print(reformatted)
# abjad.show(abjad.illustrate(tone_row))
