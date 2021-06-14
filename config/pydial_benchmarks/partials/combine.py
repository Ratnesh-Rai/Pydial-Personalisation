import os, subprocess
from itertools import product
from pprint import pprint
import argparse

parser = argparse.ArgumentParser(description='Make all possible combinations of partial config files in subdirectories')
parser.add_argument('targetdir', metavar='target', nargs='?', default='./dest')
parser.add_argument('--stdout', nargs='?', type=bool, default=False)


args = parser.parse_args()
targetdir = args.targetdir
stdout = args.stdout

if targetdir == './dest' and not os.path.isdir(targetdir):
    os.makedirs(targetdir)


if not os.path.isdir(targetdir):
    raise Exception("{} is not a directory".format(targetdir))
elif targetdir[0] != '.' and targetdir[0] != '/':
    targetdir = './' + targetdir

dir_tree = [d for d in os.walk('./src/')]

paths = {}

for path, dirs, files in dir_tree:
    if path == './src/':
        pass
    elif len(files) != 0:
        paths[path] = list(map(lambda f: path + '/' + f, files))

all_tasks = product(*paths.values())

for parts in all_tasks:
    basenames = list(map(lambda path: os.path.splitext(os.path.basename(path))[0], parts))
    full_cfg_name = os.path.join(targetdir, '-'.join(basenames) + '.cfg')
    command = 'cat ' + ' '.join(parts) + ' > ' + full_cfg_name
    with open(full_cfg_name, 'w') as wf:
        subprocess.call(['cat',] + list(parts), stdout=wf)
    if stdout:
        for i in range(0,10):
            print(' '.join(basenames + [str(i)]))
