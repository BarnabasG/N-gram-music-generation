# N-gram-music-generation
## A simple AI music generation program based on N-gram techniques

This program uses data from over 300 classical midi files from a range of composers to generate new compositions using the N-grams technique.
The program used this technique to look at the previous N notes and find instances in the training data where this sequence also appeared.
By selecting the note which followed one of those sequences, the music should sound reasonable.

I used the mido python library to read and write midi files, which contain the information on each note played along with its velocity (how hard the note is hit) as well as the time since the previous note was played.

While some outputs can sound very natural and music-like, others can sound quite random. Several tests are advised (using n_grams_music_gen.py).
Additionally, the program can sometimes end up sampling more of a particular piece than intended. This occurs if a piece has a lot of unique note sequences where the only instance of the sequence is in the same song. This issue will be reduced as more training data is added, however I implemted a similarity funtion to test how similar the generated piece is to each of the training pieces to check uniquness. This function does take significantly longer than the actual music generation and so is off by default. Set the 'show_similarities' boolean to True to enable this, or run the 'similarity calc.py' script.

Finally, the slowest part of the generation is reading and parsing the training data, so the program will only read the data if there has been as change in the number of training pieces since the last time. Otherwise, the data will be written to text file in the correct format then read back in in significantly less time for future runs. The n-grams dictionary is also saved and read using pickle.
