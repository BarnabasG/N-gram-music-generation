from mido import MidiFile

import glob
from os import walk

def similarity(filename, my_mid):

    mid = MidiFile(filename)
    mine = my_mid.tracks[0]
    my_notes, song_notes = [], ''
    i, same, diff = 1, 0, 0
    for msg in max(mid.tracks, key=len):
        if msg.type == 'note_on':
            song_notes += str(msg.note) + " "

    for i in range(1, len(mine)-5):
        my_notes.append(' '.join(str(x.note) for x in mine[i:i+5]))

    found = []
    for seq in my_notes:
        if seq in song_notes and seq not in found:
            same += 1
            found.append(seq)
        else:
            diff += 1

    if same > 0 and diff > 0:
        similar = same/(same+diff)
    else:
        similar = 0
    return similar, filename

def main():

    files = []
    folders = [x[0] for x in walk("ngrams_music/training")]

    for folder in folders:
        files += (glob.glob(folder+"/*.mid"))

    file = "successes/successful_sequence_1 (slow)"
    filename = "ngrams_music/compositions/"+file+'.mid'

    print(f"Calculating similarity for {file}")

    mid = MidiFile(filename)

    sim = []
    for piece in files:
        sim.append(similarity(piece, mid))
    srt = sorted(sim, key=lambda x: x[0], reverse=True)[:5]
    for piece in srt:
        print(f"Similarity to {piece[1]}: {piece[0]*100:0.3f} %")

if __name__ == "__main__":
    main()