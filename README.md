# Pydial-Personalisation
 This repo contains the extension of Pydial for using personal context of specific user across whole user domain, It introduces new financial product recommendation domain
## Run some examples:
**1. Run benchmark using pydial :** https://bitbucket.org/dialoguesystems/pydial/src/master/
  * Ran a benchmark after resolving few python errors in DQNPolicy.py file in line no--198, 770.
  * Following URL https://pydial.cs.hhu.de/benchmarks/ , run the followind commands to reproduce the benchmark output for "env1-dqn-CR.cfg"
  ```
  $ conda activate pydial27
  (pydial27)$ python pydial.py train config/pydial_benchmarks/env1-dqn-CR.cfg
  (pydial27)$ python pydial.py plot --noplot _benchmarklogs/env1-dqn-CR-seed7051991-00.1-4.train.log
  env1-CamRestaurants: Performance vs Num Dialogs
  Reward                       1000         2000         3000         4000
  env1-dqn-CR-00     :  12.9 +- 0.5  12.0 +- 0.6  12.0 +- 0.6  13.7 +- 0.3
  Success                      1000         2000         3000         4000
  env1-dqn-CR-00     :  94.6 +- 2.0  90.6 +- 2.6  90.6 +- 2.6  98.4 +- 1.1
  Turns                        1000         2000         3000         4000
  env1-dqn-CR-00     :   6.0 +- 0.2   6.1 +- 0.2   6.1 +- 0.2   6.0 +- 0.2
  ```
  * We can easily see and compare the output with corresponding reults in the paper: https://arxiv.org/pdf/1711.11023.pdf

**2. Run the shielded benchmark presented by “florisdenhengst”:**
  * There are many *.cfg. Run example on one cfg:
  ```  
  $ conda activate pydial27
  (pydial27)$ python pydial.py train config/pydial_benchmarks/shielded/dest/True_20_0_online_0_0.3_0.05_60000_0.0001_50_300_100_0_dec_prof_vp.cfg
  (pydial27)$ vim _benchmarklogs/True_20_0_online_0_0.3_0.05_60000_0.0001_50_300_100_0_dec_prof_vp-seed0-00.1-30.train.log
  ```
