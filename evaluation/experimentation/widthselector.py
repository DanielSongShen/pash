import subprocess
import pandas as pd
import numpy as np
import os
import math
from sklearn.preprocessing import normalize


def time_to_sec(time):
    return float(time[:time.find('m')])*60+float(time[time.find('m')+1:-1])


# Classifies grep into grep-complex and grep-simple
def arg_parser(CMD, grep_th=10):
    CMD_NAME = CMD[0]
    if len(CMD) < 1:
        return CMD_NAME
    ARGS = CMD[1:]
    if CMD_NAME == "grep":
        assert(len(ARGS) >= 1)
        regex = ARGS[-1]
        if len(regex) > grep_th:
            CMD_NAME = "grep-complex"
        else:
            CMD_NAME = "grep-simple"
    return CMD_NAME


def script_parser(script_file, CMD_LIST, dataFile):
    """
    parses bash script for pash width selector
    Args:
        script_file:  [str] name of file with script to optimize
        CND_LIST: list of commands with performance matricies

    Returns: hyper-parameters for width selector algorithm including: command frequency map, input file size
    """
    # single line script
    # TODO: multiline scripts
    with open(script_file) as f:
        lines = f.readlines()
    for line in lines:
        if 'cat' in line:
            pipeline = line
    pipeline = pipeline.split('|')
    cat_in = pipeline[0]
    assert 'cat' in cat_in
    IN_SIZE = os.path.getsize(dataFile)

    # TODO: parse command flags and args
    # For now, assume no flags
    pipeline = [_.split() for _ in pipeline]
    CMD_NAMES = [arg_parser(_) for _ in pipeline]
    CMD_FREQ = np.zeros(len(CMD_LIST))
    CMD_FREQ = pd.DataFrame(CMD_FREQ, index=CMD_LIST)
    for CMD_NAME in CMD_NAMES:
        if CMD_NAME in CMD_LIST:
            CMD_FREQ.loc[CMD_NAME]+=1
    return CMD_FREQ, IN_SIZE


def weighted_matrix_addition(a, b, w):
    # 2 dimensional matrix
    c = np.zeros(a.shape)
    for i in range(len(a)):
        for j in range(len(a[0])):
            c[i,j] = a[i,j]+w*b[i,j]
    return c


def get_normalize(array):
    return array/np.linalg.norm(array)


def width_selector_M1(script, dataFile):
    """
    predicts an optimal width for performance of pash based on performance models
    Args:
        script: script file name and path
        dataFile: path to input file. Used to get file size, not for running the script

    Returns: predicted optimal width for pash
    """
    CMD_FREQ, INPUT_FILE_SIZE = script_parser(script,
                                              ["grep-complex", "grep-simple", "sort", "tr", "wc", "uniq"], dataFile)
    # Method one: directly sum time matricies across commands
    template_full_time_matrix = pd.read_csv('performance-models/sort_full_time_matrix.csv', index_col=0)
    cumulative_time_matrix = np.zeros(template_full_time_matrix.to_numpy().shape)
    for CMD, FREQ in CMD_FREQ[0].items():
        if FREQ!=0:
            full_time_matrix = pd.read_csv('performance-models/'+CMD+'_full_time_matrix.csv', index_col=0).to_numpy()
            cumulative_time_matrix = weighted_matrix_addition(cumulative_time_matrix, full_time_matrix, FREQ)
    # pd.DataFrame(cumulative_time_matrix, columns=template_full_time_matrix.columns, index=template_full_time_matrix.index).to_csv('/home/daniel/Research/pash_figures/cumulative_time_matrix.csv')
    quantized_size = int(math.floor(math.log(INPUT_FILE_SIZE, 10)))
    OPT_WIDTH = np.argmin(cumulative_time_matrix[quantized_size-6])+1
    return OPT_WIDTH


def width_selector_M2(script, dataFile):
    """
    predicts an optimal width for performance of pash based on performance models
    Args:
        script: script file name and path
        dataFile: path to input file. Used to get file size, not for running the script

    Returns: predicted optimal width for pash
    """
    CMD_FREQ, INPUT_FILE_SIZE = script_parser(script,
                                              ["grep-complex", "grep-simple", "sort", "tr", "wc", "uniq"], dataFile)
    # Method two: weighted average of speedup matricies
    template_full_time_matrix = pd.read_csv('performance-models/sort_full_time_matrix.csv', index_col=0)
    # cumulative_time_matrix = np.zeros(template_full_time_matrix.to_numpy().shape)
    quantized_size = int(math.floor(math.log(INPUT_FILE_SIZE, 10)))
    SIZE_INDEX = quantized_size-6
    opt_speedup_widths = []
    weighted_times = []
    for CMD, FREQ in CMD_FREQ[0].items():
        if FREQ!=0:
            full_speedup_matrix = pd.read_csv('performance-models/' + CMD + '_full_speedup_matrix.csv',
                                           index_col=0).to_numpy()
            full_time_matrix = pd.read_csv('performance-models/'+CMD+'_full_time_matrix.csv', index_col=0).to_numpy()
            maxI = np.argmax(full_speedup_matrix[SIZE_INDEX])
            weighted_times.append(full_time_matrix[SIZE_INDEX][maxI]*FREQ)
            opt_speedup_widths.append((maxI+1)*FREQ)

    norm_weighted_times = get_normalize(np.asarray(weighted_times))
    weighted_sum = 0
    for CMDi in range(len(norm_weighted_times)):
        weighted_sum += opt_speedup_widths[CMDi]*norm_weighted_times[CMDi]
    OPT_WIDTH = round(weighted_sum/(sum(CMD_FREQ[0])))
    return OPT_WIDTH


def width_selector_M3(script, maxW, dataFile, step=2):
    """
    predicts an optimal width for performance of pash based on performance models
    Args:
        script: script file name and path
        maxW: maximum width to be tested
        dataFile: path to input file. Used to get file size, not for running the script
        step: step increment of width

    Returns: optimal width for pash
    """
    # Method three: experimental to get ground truth (optimal width)
    IN_SIZE = os.path.getsize(dataFile)
    quantized_size = int(math.floor(math.log(IN_SIZE, 10)))
    log = "Results/M3times.txt"
    times = []
    for i in range(1, maxW+step, step):
        subprocess.run(["./m3-time.sh", script, log, str(i)], stdout=subprocess.DEVNULL)
        with open(log, 'r') as f:
            cur_time = f.readlines()
        times.append(time_to_sec(cur_time[1].split()[1]))
    script_time_model_path = "performance-models/"+script.split('/')[-1][:-3]
    if not os.path.exists(script_time_model_path):
        os.mkdir(script_time_model_path)
    np.savetxt(script_time_model_path+"/M3_SIZE"+str(quantized_size)+"_s"+str(step)+"_Mw"+str(maxW), np.asarray(times))
    OPT_WIDTH=np.argmin(times)*step+1
    return OPT_WIDTH