from widthselector import width_selector_M1, width_selector_M2, width_selector_M3
import subprocess
import time
import os

#script_location = "no-grep-scripts"
script_location = "grep-scripts"
#script_list = ["no-grep-scripts/no_grep.sh", "no-grep-scripts/testscript1.sh"]
script_list = os.listdir(script_location)
#script_names = ["no_grep", "testscript1"]
data_location = os.environ['PASH_TOP']+"/evaluation/benchmarks/oneliners/input/"
# data_files = ['1M.txt', '10M.txt', '100M.txt', '1G.txt']
data_files = ['1M.txt']
maxM3_width = 4
# benchmark = ""


def modifyScript(script, data_file):
    with open(script, 'r') as f:
        allLines = f.readlines()
        assert(len(allLines) > 1)
        line = allLines[0]
        allLines[0] = line[:line.find('=')+1]+data_file+'\n'
    with open(script, 'w') as f:
        f.writelines(allLines)


def get_script_performances():
    for data in data_files:
        data_name = data[:data.find(".")]
        datapath = data_location + data
        M3_times = []
        M3_widths = []
        for script in script_list:
            scriptpath = script_location + "/" + script
            modifyScript(scriptpath, datapath)
            start = time.time()
            [width_selector_M3(scriptpath, maxM3_width, datapath) for _ in range(5)]
            t3 = time.time() - start
            M3_times.append(t3)
            w3 = width_selector_M3(scriptpath, maxM3_width, datapath)
            M3_widths.append(w3)

        if not os.path.exists("overhead"):
            os.mkdir("overhead")
        if not os.path.exists("overhead/" + script_location):
            os.mkdir("overhead/" + script_location)
        with open("overhead/M3_times" + data_name, 'w') as f:
            for i in range(len(script_list)):
                # f.write(script_names[i]+'\n')
                f.write(str(M3_times[i]) + '\n')
        with open("overhead/M3_widths" + data_name, 'w') as f:
            for i in range(len(script_list)):
                # f.write(script_names[i]+'\n')
                f.write(str(M3_widths[i]) + '\n')


# Clear file for new times
log = open("Results/evaluate-methods-time.out", 'w')
log.close()

"""
for data in data_files:
    log = open("Results/evaluate-methods-time.out", 'a')
    subprocess.run(["./evaluate-methods.sh", script_location], stdout=subprocess.DEVNULL, stderr=log)
    log.close()
"""

def get_default_performance():
    for data in data_files:
        data_name = data[:data.find(".")]
        datapath = data_location + data
        log = open("Results/evaluate-methods-time.out", 'a')
        log.write(data_name + '\n')
        for script in script_list:
            scriptpath = script_location + "/" + script
            modifyScript(scriptpath, datapath)
        subprocess.run(["./evaluate-default.sh", script_location], stdout=subprocess.DEVNULL, stderr=log)
        log.close()


get_default_performance()


def get_main_results():
    for data in data_files:
        data_name = data[:data.find(".")]
        datapath = data_location+data
        M1_times = []
        M2_times = []
        M3_times = []
        M1_widths = []
        M2_widths = []
        M3_widths = []
        for script in script_list:
            scriptpath = script_location+"/"+script
            modifyScript(scriptpath, datapath)

            start = time.time()
            [width_selector_M3(scriptpath, maxM3_width, datapath) for _ in range(5)]
            t3 = time.time() - start
            M3_times.append(t3)
            w3 = width_selector_M3(scriptpath, maxM3_width, datapath)
            M3_widths.append(w3)

            start = time.time()
            [width_selector_M1(scriptpath, datapath) for _ in range(5)]
            t1 = time.time()-start
            M1_times.append(t1)
            w1 = width_selector_M1(scriptpath, datapath)
            M1_widths.append(w1)

            start = time.time()
            [width_selector_M2(scriptpath, datapath) for _ in range(5)]
            t2 = time.time() - start
            M2_times.append(t2)
            w2 = width_selector_M2(scriptpath, datapath)
            M2_widths.append(w2)

        if not os.path.exists("overhead"):
            os.mkdir("overhead")
        if not os.path.exists("overhead/"+script_location):
            os.mkdir("overhead/"+script_location)

        with open("overhead/"+script_location+"/M1_times"+data_name, 'w') as f:
            for i in range(len(script_list)):
                #f.write(script_names[i]+'\n')
                f.write(str(M1_times[i])+'\n')

        with open("overhead/"+script_location+"/M2_times"+data_name, 'w') as f:
            for i in range(len(script_list)):
                #f.write(script_names[i]+'\n')
                f.write(str(M2_times[i])+'\n')

        with open("overhead/"+script_location+"/M1_widths"+data_name, 'w') as f:
            for i in range(len(script_list)):
                #f.write(script_names[i]+'\n')
                f.write(str(M1_widths[i])+'\n')

        with open("overhead/"+script_location+"/M2_widths"+data_name, 'w') as f:
            for i in range(len(script_list)):
                #f.write(script_names[i]+'\n')
                f.write(str(M2_widths[i])+'\n')

        with open("overhead/M3_times"+data_name, 'w') as f:
            for i in range(len(script_list)):
                #f.write(script_names[i]+'\n')
                f.write(str(M3_times[i])+'\n')

        with open("overhead/M3_widths"+data_name, 'w') as f:
            for i in range(len(script_list)):
                #f.write(script_names[i]+'\n')
                f.write(str(M3_widths[i])+'\n')

        #log = open("Results/evaluate-methods-time.out", 'a')
        #subprocess.run(["./evaluate-methods.sh", script_location], stdout=subprocess.DEVNULL, stderr=log)
        #log.close()