# Pydial-Personalisation
 This repo contains the extension of Pydial for using personal context of specific user across whole user domain, It introduces new financial product loan recommendation domain into inthe Pydial user simulator.
## Steps to setup Pydial
If you are reading this you have probably already downloaded the PyDial repo but if
you havent, do it now:
 ```
 git clone https://github.com/Ratnesh-Rai/Pydial-Personalisation.git
 cd Pydial-Personalisation
 ```

PyDial uses Python 2.7 and has not been tested with other versions. Ensure 
that you use the requirements.txt file to install the appropriate dependencies
via pip. If you do not have pip installed yet first do

> sudo easy_install pip

otherwise exectued directly

> pip install -r requirements.txt

To check that you have a fully functioning system, run the PyDial functional tests

> sh testPyDial

You should see output similar to the following:

Running PyDial Tests
  1 tests/test_DialogueServer.py   time 0m3.908s
  2 tests/test_Simulate.py         time 0m18.990s
  3 tests/test_Tasks.py            time 0m0.492s
3 tests: 980 warnings,   0 errors
See test logs in _testlogs for details


Finally, install the documentation

> sh createDocs.sh

Then point your browser at documentation/Docs/index.html.  If PyDial is new to you,
read the Tutorial "Introduction to PyDial".


The PyDial Team

August 2018
PyDial is distributed under Apache 2.0 Licensed. See LICENSE
## Run some examples:
**1. Run benchmark using pydial :
  * Following URL https://pydial.cs.hhu.de/benchmarks/ , run the followind commands to reproduce the benchmark output for "env1-dqn-np-CR.cfg",
  * You can select any config file just replace the config filename or path
  ```
  (pydial27)$ python pydial.py train config/pydial_benchmarks/partials/dest/env1-dqn-np-CR.cfg
  (pydial27)$ python pydial.py plot --noplot _benchmarklogs/<name of log file thats generated>
  env1-CamRestaurants: Performance vs Num Dialogs
  Reward                       1000         2000         3000         4000
  env1-dqn-CR-00     :  12.9 +- 0.5  12.0 +- 0.6  12.0 +- 0.6  13.7 +- 0.3
  Success                      1000         2000         3000         4000
  env1-dqn-CR-00     :  94.6 +- 2.0  90.6 +- 2.6  90.6 +- 2.6  98.4 +- 1.1
  Turns                        1000         2000         3000         4000
  env1-dqn-CR-00     :   6.0 +- 0.2   6.1 +- 0.2   6.1 +- 0.2   6.0 +- 0.2
  ```
  * We can easily see and compare the output with corresponding reults in the paper: https://arxiv.org/pdf/1711.11023.pdf
  
  **2. Similarly to run with other hyperparameters and algorithms modify configuration files present at config/pydial_benchmarks/
  * To run training, use following command:
   >python pydial.py train config/pydial_benchmarks/<configuration file name>.
  
  * To run test, type:
  >testPydial
  It will run all the test present under tests directory
  * To plot the resultant 
  >pydial.py plot  _benchmarklogs/<log name>
