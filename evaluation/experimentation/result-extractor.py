import math
import numpy as np
import pandas as pd
import glob
import multiprocessing
import os
from widthselector import time_to_sec

# FILE_NAME = "/home/daniel/Research/fromRemote/lin02/smalltimes.txt"
# FILE_NAME = os.environ['PASH_TOP']+"/../common-commands-time.out"
FILE_NAME = "/home/daniel/Research/pash/evaluation/experimentation/Results/evaluate-methods-time.out"
with open(FILE_NAME) as f:
    allLines = f.readlines()


def view_methods(input_sizes=(1, 10, 100, 1000), methods=("m1", "m2", "m3")):
    num_cores = int(allLines[1])
    test_scripts = allLines[0].split()
    script_names = [name.split('/')[-1] for name in test_scripts]
    script_names = [name[:name.find('.')] for name in script_names]
    real_times = [_ for _ in allLines if 'real' in _]
    real_times = np.asarray([time_to_sec(time.split()[-1]) for time in real_times])
    assert(len(test_scripts)*len(methods)*len(input_sizes) == len(real_times))
    ism_times = np.reshape(real_times, (len(input_sizes), len(test_scripts), len(methods)))  # InputScriptMethod shape
    sim_times = np.swapaxes(ism_times, 0, 1)
    script_times = [pd.DataFrame(im_times, columns=methods, index=input_sizes) for im_times in sim_times]
    widths = [int(line[line.find("=")+1:].strip()) for line in allLines if 'w=' in line]
    ism_widths = np.reshape(widths, (len(input_sizes), len(test_scripts), len(methods)))  # InputScriptMethod shape
    sim_widths = np.swapaxes(ism_widths, 0, 1)
    scripts_widths = [pd.DataFrame(im_widths, columns=methods, index=input_sizes) for im_widths in sim_widths]
    for i in range(len(scripts_widths)):
        scripts_widths[i].to_csv("Results/"+script_names[i]+"_im_widths_df")
    return 0


# view_methods()


def custom_sort(s):
    s = s[s.find('SIZE')+4:]
    return(int(s[:s.find('_')]))


def concat_models(script, Mw):
    """
    Combines all performance model files for given script into single performance matrix
    Args:
        script: name of the script
        Mw: maximum width; experiment identifier

    Returns: None
    """
    model_files = glob.glob("performance-models/"+script+"/*"+str(Mw))
    model_files.sort(key=custom_sort)
    time_matrix = []
    for file_path in model_files:
        temp = np.loadtxt(file_path)
        time_matrix.append(temp)
    time_matrix = np.asarray(time_matrix)
    SIZES = [1, 10, 100, 1000]
    WIDTHS = [i for i in range(1, Mw+2, round(Mw / len(time_matrix[0])))]
    time_df = pd.DataFrame(time_matrix, columns=WIDTHS, index=SIZES)

    seq_times = time_df[1]
    speedup_matrix = np.zeros((len(time_matrix), len(time_matrix[0])))
    for j in range(len(time_df)):
        SIZE_times = time_df.iloc[j]
        for k in range(len(SIZE_times)):
            speedup_matrix[j, k] = seq_times.iloc[j] / SIZE_times.iloc[k]
    speedup_df = pd.DataFrame(speedup_matrix, index=SIZES, columns=WIDTHS)
    path_to_figure = "/home/daniel/Research/pash_figures/"+script
    if not os.path.exists(path_to_figure):
        os.mkdir(path_to_figure)
    time_df.to_csv(path_to_figure+"/time_df.csv")
    speedup_df.to_csv(path_to_figure+"/speedup_df.csv")
    return None


#script_names = ["minimal_sort", "no_grep", "sort-sort", "top-n", "wf"]
script_names = ["shortest-scripts"]
[concat_models(s_name, 40) for s_name in script_names]
view_methods()


def compare_methods(script, data_path="/home/daniel/Research/pash_figures", widths_suffix="_im_widths_df"):
    # Performance times
    speedups = pd.read_csv(data_path+"/"+script+"/speedup_df.csv", index_col=0)
    times = pd.read_csv(data_path + "/" + script + "/time_df.csv", index_col=0)
    widths = pd.read_csv("Results/"+script+widths_suffix, index_col=0)
    time_comparison = np.zeros((len(widths), len(widths.iloc[0])))
    for i in range(len(widths)):
        for w in range(len(widths.iloc[0])):
            width = widths.iloc[i][w]
            times_row = times.iloc[i]
            if str(width) not in times.columns:
                time = (times_row.loc[str(width+1)]+times_row.loc[str(width-1)])/2
            else:
                time = times_row.loc[str(width)]
            time_comparison[i, w] = time
    time_comparison = pd.DataFrame(time_comparison, index=widths.index, columns=widths.columns)

    # Overheads
    
    pass


#compare_methods("shortest-scripts")


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

# fill()
print()