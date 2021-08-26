import math
import numpy as np
import pandas as pd
import multiprocessing
import os

FILE_NAME = "/home/daniel/Research/fromRemote/lin02/smalltimes.txt"
# FILE_NAME = os.environ['PASH_TOP']+"/../common-commands-time.out"
with open(FILE_NAME) as f:
    allLines = f.readlines()

# sanity check
# NUM_CORES = multiprocessing.cpu_count()
# assert NUM_CORES==int(allLines[2])
NUM_CORES = int(allLines[2])

COMMANDS = allLines[1].split()
real_times = [_ for _ in allLines if 'real' in _ or '']
real_times = np.asarray(real_times)

# populate time array
WIDTHS = [int(_[_.find('=')+1:]) for _ in allLines if 'w=' in _]
NUM_WIDTHS = math.floor(math.log(NUM_CORES, 2))+1
WIDTHS = WIDTHS[:NUM_WIDTHS]
assert len(real_times)/NUM_WIDTHS/len(COMMANDS) == int(len(real_times)/NUM_WIDTHS/len(COMMANDS))
SIZES = [_[:_.find('.')] for _ in allLines if '.txt' in _ and 'cat' not in _]
NUM_SIZES = int(len(real_times)/NUM_WIDTHS/len(COMMANDS))
SIZES = SIZES[:NUM_SIZES]
real_times_temp = []
for i in range(len(COMMANDS)):
    size_times = []
    for j in range(NUM_SIZES):
        width_times = []
        for k in range(NUM_WIDTHS):
            width_times.append(real_times[i*(NUM_SIZES*NUM_WIDTHS)+j*(NUM_WIDTHS)+k])
            #real_times_temp[i,j,k] = real_times[i*(NUM_SIZES*NUM_WIDTHS)+j*(NUM_WIDTHS)+k]
        size_times.append(width_times)
    real_times_temp.append(size_times)
real_times = real_times_temp


def time_to_sec(time):
    return float(time[:time.find('m')])*60+float(time[time.find('m')+1:-1])


def populate():
    # populate performance matricies
    tempsum = 0
    for i, CMD in enumerate(COMMANDS):
        time_matrix = np.zeros((NUM_SIZES, NUM_WIDTHS))
        CMD_times = real_times[i]
        for j, SIZE_times in enumerate(CMD_times):
            for k, time in enumerate(SIZE_times):
                time_matrix[j,k] = time_to_sec(time.split()[-1])
                tempsum+=time_to_sec(time.split()[-1])
        time_matrix = pd.DataFrame(time_matrix, index=SIZES, columns=WIDTHS)
        seq_times = time_matrix[1]
        speedup_matrix = np.zeros((NUM_SIZES, NUM_WIDTHS))
        for j in range(len(time_matrix)):
            SIZE_times = time_matrix.iloc[j]
            for k in range(len(SIZE_times)):
                speedup_matrix[j,k] = seq_times[j]/SIZE_times.iloc[k]
        speedup_matrix = pd.DataFrame(speedup_matrix, index=SIZES, columns=WIDTHS)
        time_matrix.to_csv("performance-models/"+CMD+"_time_matrix.csv")
        speedup_matrix.to_csv("performance-models/"+CMD+"_speedup_matrix.csv")


def fill():
    # Fill performance models
    for CMD in COMMANDS:
        time_matrix = pd.read_csv("performance-models/"+CMD+"_time_matrix.csv", index_col=0)
        speedup_matrix = pd.read_csv("performance-models/" + CMD + "_speedup_matrix.csv", index_col=0)
        full_time_matrix = np.zeros((len(time_matrix), NUM_CORES+1))
        for i in range(len(time_matrix)):
            SIZE_times = time_matrix.iloc[i]
            endtime = SIZE_times.iloc[0]
            endpoint = int(SIZE_times.index[0])
            assert(endpoint==len(full_time_matrix[0])-1)
            full_time_matrix[i, endpoint] = endtime
            for startpoint, starttime in SIZE_times.iloc[1:].iteritems():
                startpoint = int(startpoint)
                slope = (endtime-starttime)/(endpoint-startpoint)
                full_time_matrix[i, startpoint:endpoint] = [starttime+slope*t for t in range(endpoint-startpoint)]
                endpoint = startpoint
                endtime = starttime
        full_time_matrix = pd.DataFrame(full_time_matrix, index=SIZES)
        full_time_matrix = full_time_matrix.drop(columns=[0])

        full_speedup_matrix = np.zeros((len(speedup_matrix), NUM_CORES))
        seq_times = full_time_matrix[1]
        for j in range(len(full_time_matrix)):
            SIZE_times = full_time_matrix.iloc[j]
            for k in range(len(SIZE_times)):
                full_speedup_matrix[j, k] = seq_times[j] / SIZE_times.iloc[k]
        full_speedup_matrix = pd.DataFrame(full_speedup_matrix, index=SIZES, columns=[i for i in range(1,NUM_CORES+1)])
        full_time_matrix.to_csv("performance-models/" + CMD + "_full_time_matrix.csv")
        full_speedup_matrix.to_csv("performance-models/" + CMD + "_full_speedup_matrix.csv")
        print()

fill()
print()