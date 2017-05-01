import argparse
import random

import numpy as np
import tensorflow as tf

from gtd.io import save_stdout
from gtd.log import set_log_level
from gtd.utils import Config
from strongsup.experiment import Experiments
from strongsup.results.tracker import TopLevelTracker
from strongsup.results.entry import ExperimentType

set_log_level('DEBUG')


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('exp_id', nargs='+')
arg_parser.add_argument('-m', '--mode', default='train', choices=['train', 'eval'])
arg_parser.add_argument('-v', '--eval-visualize', action='store_true',
        help='(eval mode) whether to log things to visualizers (WARNING: big file size!)')
arg_parser.add_argument('-s', '--eval_samples', default=float('inf'), type=float,
        help='(eval mode) number of examples to evaluate on (default: entire dataset)')
arg_parser.add_argument('-c', '--check_commit', default='strict')
arg_parser.add_argument('-t', '--tracker')
arg_parser.add_argument('-r', '--random-seed', default=0, type=int)
args = arg_parser.parse_args()


# set random seeds
seed = args.random_seed
random.seed(seed)
np.random.seed(seed)
tf.set_random_seed(seed)

# import keras AFTER random seeds are set
from keras import backend as K

sess_config = tf.ConfigProto()
sess_config.gpu_options.allow_growth = True
sess = tf.InteractiveSession(config=sess_config)
K.set_session(sess)


exp_id = args.exp_id
exp_mode = args.mode
eval_samples = args.eval_samples

# create experiment
experiments = Experiments(check_commit=args.check_commit=='strict')

if exp_id == ['default']:
    # new default experiment
    exp = experiments.new()
elif len(exp_id) == 1 and exp_id[0].isdigit():
    # reload old experiment
    exp = experiments[int(exp_id[0])]
else:
    # new experiment according to configs
    config = Config.from_file(exp_id[0])
    for filename in exp_id[1:]:
        config = Config.merge(config, Config.from_file(filename))
    exp = experiments.new(config)  # new experiment from config

# add experiment to tracker
if args.tracker:
    exp_type, dataset, seed = ExperimentType.parse_configs(exp_id)
    with TopLevelTracker(args.tracker) as tracker:
        tracker.register_result(
                dataset, exp_type, seed, exp.workspace.root)

################################
# Profiling
# from gtd.chrono import Profiling, Profiler
# profiler = Profiler.default()
# import gtd.ml.seq_batch; profiler.add_module(gtd.ml.seq_batch)
# import strongsup.decoder; profiler.add_module(strongsup.decoder)
# import strongsup.parse_model; profiler.add_module(strongsup.parse_model)
# import strongsup.parse_case; profiler.add_module(strongsup.parse_case)
# import strongsup.tables.predicates_computer; profiler.add_module(strongsup.tables.predicates_computer)
# import strongsup.tables.executor; profiler.add_module(strongsup.tables.executor); strongsup.tables.executor.add_decorated_methods(profiler)
# import strongsup.exploration_policy; profiler.add_module(strongsup.exploration_policy)
# Profiling.start()
################################

# start training
exp.workspace.add_file('stdout', 'stdout.txt')
exp.workspace.add_file('stderr', 'stderr.txt')

with save_stdout(exp.workspace.root):
    try:
        config = exp.config
        if exp_mode == 'train':
            print '\n===== TRAIN MODE ====='
            if config.train_mode == 'semi-supervised':
                exp.train()
            elif config.train_mode == 'supervised':
                exp.supervised_train()
            else:
                raise ValueError('Invalid train mode: {}'.format(config.train_mode))

        elif exp_mode == 'eval':
            print '\n===== EVALUATION MODE ====='
            exp.big_evaluate(eval_samples)
        else:
            raise ValueError('Invalid experiment mode: {}'.format(exp_mode))

    finally:
        pass
        ################################
        # Profiling.report()
        ################################
