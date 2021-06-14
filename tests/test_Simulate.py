###############################################################################
# PyDial: Multi-domain Statistical Spoken Dialogue System Software
###############################################################################
#
# Copyright 2015 - 2018
# Cambridge University Engineering Department Dialogue Systems Group
#
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

'''
************************

**test_Simulate.py** - test simulation system
==========================================================================

'''

#from nose.tools import with_setup
import os,sys
curdir = os.path.dirname(os.path.realpath(__file__))
curdir = curdir.split('/')
curdir = '/'.join(curdir[:-1]) +'/'
os.chdir(curdir)
sys.path.insert(0,curdir)

from ontology import Ontology
from utils import Settings
from utils import ContextLogger
import Simulate
import TestingUtils
import time

class TEntropyMinimizationPolicy():
    """Entropy Minimization policy tests
    """
    def test_simulate_multidomain(self):
        '''Run EntropyMinimization policy for domains in 2 multi domain dialogues
        '''
        Settings.init(config_file='./tests/test_configs/simulate_multiDomains_EntropyMinimizationPolicy.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        logger.info("Starting Entropy Minimization Policy Multidomain Simulation")
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        simulator = Simulate.SimulationSystem(error_rate=0.1)
        simulator.run_dialogs(2)    # run 2 dialogues

    def test_simulate_singledomain_for_all_domains(self):
        '''Loop over all domains and run 2 dialogues via EntropyMinimizationPolicy in each
        '''
        Settings.init(config_file='./tests/test_configs/simulate_singledomain_for_all_domains.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        domains = TestingUtils.get_loop_over_domains()
        for dstring in domains:
            Settings.config.set("GENERAL", 'domains', dstring)
            Settings.config.add_section('policy_'+dstring)
            Settings.config.set('policy_'+dstring, 'policytype','entropy_minimization')
            logger.info("Starting Entropy Minimization Single Domain Simulation for "+dstring)
            reload(Ontology.FlatOntologyManager)        # since this has a singleton class
            Ontology.init_global_ontology()
            simulator = Simulate.SimulationSystem(error_rate=0.1)
            simulator.run_dialogs(2)    # run 2 dialogues


class TRandomQuestionPolicy():
    """Random Question policy tests
    """
    def test_simulate_multidomain(self):
        '''Run RandomQuestion policy for domains in 2 multi domain dialogues
        '''
        Settings.init(config_file='./tests/test_configs/simulate_multiDomains_RandomQuestion.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        logger.info("Starting Random Question Multidomain Simulation")
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        simulator = Simulate.SimulationSystem(error_rate=0.1)
        simulator.run_dialogs(2)    # run 2 dialogues

    def test_simulate_singledomain_for_all_domains(self):
        '''Loop over all domains and run 2 dialogues via RandomQuestion policy in each
        '''
        Settings.init(config_file='./tests/test_configs/simulate_singledomain_for_all_domains.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        domains = TestingUtils.get_loop_over_domains()
        for dstring in domains:
            Settings.config.set("GENERAL", 'domains', dstring)
            Settings.config.add_section('policy_'+dstring)
            Settings.config.set('policy_'+dstring, 'policytype','random')
            Settings.config.set('policy_'+dstring, 'summary_belief_threshold','.8')
            logger.info("Starting RandomQuestion Single Domain Simulation for "+dstring)
            reload(Ontology.FlatOntologyManager)        # since this has a singleton class
            Ontology.init_global_ontology()
            simulator = Simulate.SimulationSystem(error_rate=0.1)
            simulator.run_dialogs(2)    # run 2 dialogues


class TNaiveDatabaseEntropyPolicy():
    """Naive Database Entropy policy tests
    """
    def test_simulate_multidomain(self):
        '''Run RandomQuestion policy for domains in 2 multi domain dialogues
        '''
        Settings.init(config_file='./tests/test_configs/simulate_multiDomains_NaiveDatabaseEntropy.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        logger.info("Starting NaiveDatabaseEntropyPolicy Multidomain Simulation")
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        simulator = Simulate.SimulationSystem(error_rate=0.1)
        simulator.run_dialogs(2)    # run 2 dialogues

    def test_simulate_singledomain_for_all_domains(self):
        '''Loop over all domains and run 2 dialogues via RandomQuestion policy in each
        '''
        Settings.init(config_file='./tests/test_configs/simulate_singledomain_for_all_domains.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        domains = TestingUtils.get_loop_over_domains()
        for dstring in domains:
            Settings.config.set("GENERAL", 'domains', dstring)
            Settings.config.add_section('policy_'+dstring)
            Settings.config.set('policy_'+dstring, 'policytype','naive_database_entropy')
            Settings.config.set('policy_'+dstring, 'summary_belief_threshold','.8')
            # no policy settings given --> defaults to HDC
            logger.info("Starting NaiveDatabaseEntropyPolicy Single Domain Simulation for "+dstring)
            reload(Ontology.FlatOntologyManager)        # since this has a singleton class
            Ontology.init_global_ontology()
            simulator = Simulate.SimulationSystem(error_rate=0.1)
            simulator.run_dialogs(2)    # run 2 dialogues


class THDCPolicy():
    """HDC (handcrafted) policy tests
    """
    def test_simulate_multidomain(self):
        '''Run HDC policy for domains in 2 multi domain dialogues
        '''
        Settings.init(config_file='./tests/test_configs/simulate_multiDomains_HDC.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        logger.info("Starting HDC Multidomain Simulation")
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        simulator = Simulate.SimulationSystem(error_rate=0.1)
        simulator.run_dialogs(2)    # run 2 dialogues

    def test_simulate_singledomain_for_all_domains(self):
        '''Loop over all domains and run 2 dialogues via HDC policy in each
        '''
        Settings.init(config_file='./tests/test_configs/simulate_singledomain_for_all_domains.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        domains = TestingUtils.get_loop_over_domains()
        for dstring in domains:
            Settings.config.set("GENERAL", 'domains', dstring)
            Settings.config.add_section('policy_'+dstring)
            Settings.config.set('policy_'+dstring, 'policytype','hdc')
            # no policy settings given --> defaults to HDC
            logger.info("Starting HDC Single Domain Simulation for "+dstring)
            reload(Ontology.FlatOntologyManager)        # since this has a singleton class
            Ontology.init_global_ontology()
            simulator = Simulate.SimulationSystem(error_rate=0.1)
            simulator.run_dialogs(2)    # run 2 dialogues


class TGPPolicy():
    """GP (Gaussian Process) policy tests
    """
    def test_simulate_multidomain(self):
        '''Run 2 dialogues with the multidomain system and GP policies
        (NB: config needs to explicitly set each domain to use gp actually...)
        '''
        Settings.init(config_file='./tests/test_configs/simulate_multiDomains_GP.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        logger.info("Starting GP Multidomain Simulation")
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        simulator = Simulate.SimulationSystem(error_rate=0.1)
        simulator.run_dialogs(2)    # run 2 dialogues

    def test_simulate_singledomain_for_all_domains(self):
        '''Loop over all domains and runs 2 dialogues with GP policy in each
        '''
        import numpy.random as nprand
        # not seeding this - so will be based on system clock--> meaning TESTING here will be somewhat random -->
        # NOTE --> THIS IS !!!REALLY REALLY REALLY!!! NOT IN THE SPIRIT OF (UNIT) TESTING - WHICH SHOULD NEVER BE ~RANDOM
        # doing it to get a little more coverage of testing without writing permutations of explicit tests ...

        Settings.init(config_file='./tests/test_configs/simulate_singledomain_for_all_domains.cfg')
        ContextLogger.createLoggingHandlers(config=Settings.config)
        logger = ContextLogger.getLogger('')
        reload(Ontology.FlatOntologyManager)        # since this has a singleton class
        Ontology.init_global_ontology()
        domains = TestingUtils.get_loop_over_domains()
        for dstring in domains:
            Settings.config.set("GENERAL", 'domains', dstring)
            logger.info("Starting GP Single Domain Simulation for "+dstring)

            # [policy_DOMAINTAG]
            Settings.config.add_section('policy_'+dstring)
            Settings.config.set('policy_'+dstring, 'learning','True')
            Settings.config.set('policy_'+dstring, 'policytype','gp')
            # no inpolicy file give --> starts with empty file (random policy)
            Settings.config.set('policy_'+dstring, 'outpolicyfile','tests/test_gp/'+dstring)
            if nprand.uniform() > 0.5:
                Settings.config.set('policy_'+dstring, 'belieftype','baseline')
            else:
                Settings.config.set('policy_'+dstring, 'belieftype','focus')

            # [gppolicy_DOMAINTAG]
            Settings.config.add_section('gppolicy_'+dstring)
            if nprand.uniform() > 0.5:
                Settings.config.set('gppolicy_'+dstring, 'kernel','polysort')
            else:
                Settings.config.set('gppolicy_'+dstring, 'kernel','gausssort')
            if nprand.uniform() > 0.5:
                Settings.config.set('gppolicy_'+dstring, 'actionkerneltype','delta')
            else:
                Settings.config.set('gppolicy_'+dstring, 'actionkerneltype','hdc')
            reload(Ontology.FlatOntologyManager)        # since this has a singleton class
            Ontology.init_global_ontology()
            simulator = Simulate.SimulationSystem(error_rate=0.1)
            simulator.run_dialogs(2)    # run 2 dialogues

def Test():
#    test = TGPPolicy()
#    print "Executing tests in",test.__class__.__name__
##    test.test_simulate_multidomain()
#    start = time.time()
#    test.test_simulate_singledomain_for_all_domains()
#    end = time.time()
#    print("Done in {0} , {1} /run".format(end-start, (end-start)/100))
#    print "Done"

    test = TEntropyMinimizationPolicy()
    print "Executing tests in",test.__class__.__name__
#    test.test_simulate_multidomain()
    start = time.time()
    test.test_simulate_singledomain_for_all_domains()
    end = time.time()
    print("Done in {0} , {1} /run".format(end-start, (end-start)/100))

    test = TRandomQuestionPolicy()
    print "Executing tests in",test.__class__.__name__
#    test.test_simulate_multidomain()
    start = time.time()
    test.test_simulate_singledomain_for_all_domains()
    end = time.time()
    print("Done in {0} , {1} /run".format(end-start, (end-start)/100))

    test = TNaiveDatabaseEntropyPolicy()
    print "Executing tests in",test.__class__.__name__
#    test.test_simulate_multidomain()
    start = time.time()
    test.test_simulate_singledomain_for_all_domains()
    end = time.time()
    print("Done in {0} , {1} /run".format(end-start, (end-start)/100))

    test = THDCPolicy()
    print "Executing tests in",test.__class__.__name__
#    test.test_simulate_multidomain()
    start = time.time()
    test.test_simulate_singledomain_for_all_domains()
    end = time.time()
    print("Done in {0} , {1} /run".format(end-start, (end-start)/100))


if __name__ == '__main__':
    Test()
