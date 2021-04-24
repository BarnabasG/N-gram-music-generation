from mido import MidiFile, Message, MidiTrack
from datetime import datetime
from time import perf_counter

import nltk
import random

import glob
from os import path, walk, remove

import pickle

notes_to_estimate = 1000

def read_notes(filename):
    
    mid = MidiFile(filename)

    all_notes, velocities, times = '','',''     

    print(max(mid.tracks, key=len))
    for msg in max(mid.tracks, key=len):

        if msg.type == 'note_on':
            all_notes += (str(msg.note)) + ' '
            velocities += (str(msg.velocity)) + ' '
            times += (str(msg.time)) + ' '

    return (all_notes, velocities, times)

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
        if seq in song_notes and not seq in found:
            same += 1
            #found.append(seq)
        else:
            diff += 1

    if same > 0 and diff > 0:
        similar = same/(same+diff)
    else:
        similar = 0
    return similar, filename#max(mid.tracks, key=len)


def ngram(notes, velocities, times, N, ngrams={}):


    note_tokens = nltk.word_tokenize(notes)
    velocity_tokens = nltk.word_tokenize(velocities)
    time_tokens = nltk.word_tokenize(times)

    if ngrams == {}:
        start = perf_counter()
        ngrams = create_key(note_tokens, N, {})
        stop = perf_counter()
        print(f"ngram find time: {stop-start:0.3f} seconds")


    index = random.randrange(len(note_tokens)-N)

    curr_sequence = ' '.join(note_tokens[index:index+N])
    output_velocities = ' '.join(velocity_tokens[index:index+N])
    output_times = ' '.join(time_tokens[index:index+N])

    output_notes = curr_sequence

    diverge = 0
    continuous = [0]

    next_in_seq = index+N
    next_vel_seq = index+N
    next_time_seq = index+N

    for i in range(notes_to_estimate):
        if curr_sequence not in ngrams.keys():
            index = random.randrange(len(note_tokens)-N)
            print("MISSING", curr_sequence, i)
            curr_sequence = ' '.join(note_tokens[index:index+N])


        if continuous[-1] > 7:
            next = random.choice(ngrams[curr_sequence])
            
            next_note = note_tokens[next]

            if next_note != note_tokens[next_in_seq]:

                diverge += 1
                continuous.append(1)

            else:
                continuous[-1] += 1

            next_in_seq = next+1
            next_vel_seq = next+1
            next_time_seq = next+1
            next_velocity = velocity_tokens[next]
            next_time = time_tokens[next]
        else:
            next_note = note_tokens[next_in_seq]
            next_velocity = velocity_tokens[next_vel_seq]
            next_time = time_tokens[next_time_seq]
            next_in_seq += 1
            next_vel_seq += 1
            next_time_seq += 1

            continuous[-1] += 1            

        output_notes += ' ' + next_note
        
        output_velocities += ' ' + next_velocity

        output_times += ' ' + next_time

        seq_notes = nltk.word_tokenize(output_notes)
        seq = seq_notes[len(seq_notes)-N:len(seq_notes)]

        curr_sequence = ' '.join(seq)

    note_out = output_notes.split()
    vel_out = output_velocities.split()
    time_out = output_times.split()

    length, unique = 0, 0
    for n in ngrams.values():
        note_x = []
        for x in n:
            note_x.append(note_tokens[x])
        length += len(note_x)
        unique += len(set(note_x))

    ngram_avr = length/len(ngrams.keys())
    unique_avr = unique/len(ngrams.keys())
    print(f"Average continuation per {N} note sequence: {ngram_avr:0.3f}" )
    print(f"Average unique continuation per {N} note sequence: {unique_avr:0.3f}" )
    print("Divergences from previous sequence:", diverge)
    

    return (note_out, vel_out, time_out, ngrams, continuous)

def create_key(note_tokens, N, ngrams):

    for i in range(len(note_tokens)-N):
        seq = ' '.join(note_tokens[i:i+N])
        if seq not in ngrams.keys():
            ngrams[seq] = []
        ngrams[seq].append(i+N)

    return ngrams


def create_track(details, composer):

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('program_change', program=1, time=0))
    for n in details:
        v = int(n[1])
        t = int(n[2])
        if 0 < v < 35:
            v = 35
        elif v > 105:
            v = 105
        track.append(Message('note_on', note=int(n[0]), velocity=v, time=t))

    now = datetime.now()

    current_time = now.strftime("%H-%M-%S")
    filename = 'compositions/' + composer + "_"  + current_time +'.mid'

    mid.save(filename)

    return mid, filename

def get_setup(composer, count):

    f=open(composer + "_training.txt", "r")
    lines = f.readlines()
    clean = [ line.strip() for line in lines ]

    if clean[0]==str(count):
        return (clean[1],clean[2],clean[3])
    else:
        return 0
            

def main():

    N = 8
    
    composer = 'all'
    if composer == 'all':
        files = []
        folders = [x[0] for x in walk("training")]
        for folder in folders:
            files += (glob.glob(folder+"/*.mid"))
    else:
        files = glob.glob("training/"+composer+"/*.mid")
    count = len(files)
    print(composer + "_training.txt")
    if path.isfile(composer + "_training.txt"):
        search = get_setup(composer, count)
    else:
        search = 0
    start = perf_counter()
    if search == 0:
 
        all_notes,all_velocities,all_times = '','',''
        for piece in files:
            data = read_notes(piece)
            all_notes += data[0]
            all_velocities += data[1]
            all_times += data[2]

        f=open(composer + "_training.txt", "w")
        f.write(str(count) + '\n')
        f.write(str(all_notes) + '\n')
        f.write(str(all_velocities) + '\n')
        f.write(str(all_times) + '\n')

        ngrams_pickles = (glob.glob("*.p"))
        for f in ngrams_pickles:
            remove(f)
        
    else:
        all_notes = search[0]
        all_velocities = search[1]
        all_times = search[2]


        if path.isfile("ngram_"+composer+"_"+str(N)+".p"):
            ngrams = pickle.load(open("ngram_"+composer+"_"+str(N)+".p", "rb"))
        else:
            search = 0


    stop = perf_counter()
    print(f"Load time: {stop-start:0.3f} seconds")  

    for _ in range(1):

        show_simalarities = False
        start = perf_counter()
        if search == 0:
            res = ngram(all_notes, all_velocities, all_times, N)
            pickle.dump(res[3], open("ngram_"+composer+"_"+str(N)+".p", "wb"))

        else:
            res = ngram(all_notes, all_velocities, all_times, N, ngrams)

        notes = res[0]
        velocities = res[1]
        times = res[2]
        continuous = res[4]
        print(continuous)
        continuous = sorted(continuous, reverse=True)
        print(continuous)
        details = list(zip(notes, velocities, times))

        fin = create_track(details, composer)
        mid, name = fin[0], fin[1]

        print("notes: ", len(details))
        stop = perf_counter()
        print(f"Composition Complete: length - {mid.length:0.2f} seconds")
        print(f"Song {name} creation time: {stop-start:0.3f} seconds")

        
        if show_simalarities:
            start = perf_counter()
            sim = []
            for piece in files:
                sim.append(similarity(piece, mid))

            srt = sorted(sim, key=lambda x: x[0], reverse=True)[:5]
            for piece in srt:
                print(f"Similarity for {piece[1]}: {piece[0]*100:0.3f} %")
            stop = perf_counter()
            print(f"Simalarity calculation time: {stop-start:0.3f} seconds")
        print()

        



if __name__ == "__main__":
    main()
