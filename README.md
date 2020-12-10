## PaSh: Light-touch Data-Parallel Shell Processing

Mailing lists: [Commits](mailto:pash-commits@googlegroups.com) | [Discussion](mailto:pash-discuss@googlegroups.com)

PaSh is  a system for  parallelizing POSIX shell  scripts. Key elements include:

* [compiler](./compiler): Shell-to-Dataflow translations and associated parallelization transformations.
* [annotations](./annotations/): DSL characterizing commands, parallelizability study, and associated annotations.
* [evaluation](./evaluation): shell pipelines and example [scripts](./evaluation/scripts) used for the evaluation.
* [runtime](./runtime): PaSh's runtime components, including `eager`, `split`, and assocaited combiners.
* [docs](./docs): Design documents, tutorials, installation instructions, etc.
* [papers](./papers): Academic papers related to PaSh ([EuroSys 2021](https://arxiv.org/abs/2007.09436)).

## Running PaSh

To parallelize, say, `./evaluation/hello-world.sh` with parallelization width of `2`, from the top-level directory of the repository run:

```sh
./pa.sh -w 2 ./evaluation/hello-world.sh
``` 

## Installation

To install, run:

```sh
./install.sh -p
```

The `-p` requires `sudo` (i.e., "root") access to install packages such as `opam`, `python3.8`, etc.

## Tests

To execute the current tests, one-liner shell scripts, simply run:

```sh
cd compiler
./test_evaluation_scripts.sh
```

