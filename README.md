## Introduction

**Authors**: Kelvin Guu, Panupong (Ice) Pasupat, Evan Zheran Liu, Percy Liang

Source code accompanying our ACL 2017 paper,
[From Language to Programs: Bridging Reinforcement Learning and Maximum Marginal
Likelihood](https://arxiv.org/abs/1704.07926).

Also see:
- [An introduction to SCONE](https://nlp.stanford.edu/projects/scone/),
the context-dependent semantic parsing dataset that we evaluate on.
- Reproducible experiments on
[our worksheet at CodaLab.org](https://worksheets.codalab.org/worksheets/0x88c914ee1d4b4a4587a07f36f090f3e5/).

## Setup

First, download the repository and necessary data.

```bash
$ git clone https://github.com/kelvinguu/lang2program.git
$ mkdir -p lang2program/data
$ cd lang2program/data
$ wget http://nlp.stanford.edu/data/glove.6B.zip  # GloVe vectors
$ unzip glove.6B.zip -d glove.6B
$ wget https://nlp.stanford.edu/projects/scone/scone.zip  # SCONE dataset
$ unzip scone.zip
```

The resulting data directory should look like this:

- data/
    - glove.6B/
    - rlong/

Now, start the project's Docker container (you will need to install [Docker](https://www.docker.com/what-docker)).
The container has all the required software dependencies installed.

```bash
$ cd ..
$ ./launch_docker
```

This script will download the appropriate Docker image if it is not already
on your machine. Downloading the image may take a while.

Inside the container, your Git repository will be mounted at `/lang2program`.
All subsequent instructions in this README should be performed inside
the container. To exit the container, type `exit`, just as you would
exit `bash`.


## Training a model

To launch a new training run:

```bash
$ cd /lang2program
$ python scripts/main.py configs/rlong/best-scene.txt
```

To run a different configuration, replace `configs/rlong/best-scene.txt`
with your own config file. See `configs/rlong/default-base.txt`
and `configs/rlong/dataset-mixins/scene.txt` for reasonable starting
points. These files are in [HOCON](https://github.com/typesafehub/config/blob/master/HOCON.md)
syntax.

On stdout, the script will print out the experiment's ID number.

Data for this experiment will be saved to the directory
`/lang2program/data/experiments/<experiment_id>`, containing the following
files:

- config.txt
    - The config file for this training run
- checkpoints/
    - TensorFlow checkpoints, saved during training
- tensorboard/
    - TensorBoard log files
- codalab.json
    - The results of periodic evaluation are saved here.
