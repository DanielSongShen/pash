import sys
import subprocess
from subprocess import PIPE, run
import os
GIT_TOP_CMD = ['git', 'rev-parse', '--show-toplevel', '--show-superproject-working-tree']
if 'PASH_TOP' in os.environ:
    PASH_TOP = os.environ['PASH_TOP']
else:
    PASH_TOP = run(GIT_TOP_CMD, stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout.rstrip()
sys.path.append(PASH_TOP)

TEST_FILE_DIR = f"{PASH_TOP}/evaluation/benchmarks/oneliners/input"
TESTFILES = [f"{TEST_FILE_DIR}/1M.txt", f"{TEST_FILE_DIR}/10M.txt"]
commands = ["sort", "tr", "wc", "uniq", "grep"]


def eval_width(commands):
    """
    Evaluate frequently used parallizable-pure commands
    TODO evaluate using C aggregators
    Args:
        commands: list of commands to evaluate

    Returns:

    """
    subprocess.call(f"{PASH_TOP}/pa.sh ")

