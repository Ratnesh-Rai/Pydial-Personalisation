###############################################################################
# PyDial: Multi-domain Statistical Spoken Dialogue System Software
###############################################################################
#
# Copyright 2015 - 2017
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
SplitPolicy.py - Dialogue manager that is composed of two policies
questions remain to be asked
====================================================

Copyright CUED Dialogue Systems Group 2015 - 2017

.. seealso:: CUED Imports/Dependencies: 

    import :mod:`policy.Policy` |.|
    import :mod:`policy.HDCPolicy` |.|
    import :mod:`policy.PolicyUtils` |.|
    import :mod:`policy.SummaryUtils` |.|
    import :mod:`utils.Settings` |.|
    import :mod:`utils.ContextLogger`

************************

'''

__author__ = "Floris den Hengst <f.den.hengst@vu.nl>"

import copy
import pprint

import Policy
import PolicyUtils
import SummaryUtils
from ontology import Ontology
from utils import ContextLogger, Settings

from GPPolicy import GPPolicy
from ENACPolicy import ENACPolicy
from A2CPolicy import A2CPolicy
from DQNPolicy import DQNPolicy

logger = ContextLogger.getLogger('')

NONE_MARKER = "**NONE**"
NULL_ACTION_MARKER = "null()"

policy_map = {
        'dqn': DQNPolicy,
        'enac': ENACPolicy,
        'a2c': A2CPolicy,
        'gp': GPPolicy,
}

class SplitPolicy(Policy.Policy):
    """
    Random Question policy derives from Policy base class. Randomly requests attributes until
    either all attributes are known or a single item remains in scope.
    
    """
    def __init__(self, in_policy_file, out_policy_file, domainString, learning, *args, **kwargs):
        super(SplitPolicy, self).__init__(domainString, learning)
        if Settings.config.has_option('splitpolicy', 'use_upfront_knowledge'):
            self.use_upfront_knowledge = Settings.config.getboolean('splitpolicy', 'use_upfront_knowledge')
        if Settings.config.has_option('splitpolicy', 'base_policy'):
            self.base_policy_str = eval(Settings.config.get('splitpolicy', 'base_policy'))
            self.base_policy = policy_map[self.base_policy_str]
        if self.use_upfront_knowledge is False:
            logger.error('Cannot create SplitPolicy without upfront knowledge')
        
        in_policy_file0 = in_policy_file + 'p0'
        out_policy_file0 = out_policy_file + 'p0'
        in_policy_file1 = in_policy_file + 'p1'
        out_policy_file1 = out_policy_file + 'p1'
        
        self.policy_0_c = 0
        self.policy_1_c = 0

        if self.base_policy_str == 'gp':
            self.policy_0 = self.base_policy(domainString, learning, policyfilesuffix='p0')
            self.policy_1 = self.base_policy(domainString, learning, policyfilesuffix='p1')
        elif self.base_policy_str in ['a2c', 'enac']:
            self.policy_0 = self.base_policy(in_policy_file0, out_policy_file0, domainString,
                    learning)
            self.policy_1 = self.base_policy(in_policy_file1, out_policy_file1, domainString,
                    learning)
        else:
            self.policy_0 = self.base_policy(in_policy_file0, out_policy_file0, domainString,
                    learning, *args, **kwargs)
            self.policy_1 = self.base_policy(in_policy_file1, out_policy_file1, domainString,
                    learning, *args, **kwargs)

    def act_on(self, state, hyps=None, user_act=None):
        beliefstate = state.getDomainState(self.domainString)
        uk_vector = beliefstate['upfrontKnowledge']
        group = filter(lambda i: i[1] == 1.0, uk_vector)[0][0][0]

        if hyps is not None: 
            args = (state, hyps, user_act)
        else:
            args = (state, user_act)

        if group == 0:
            system_action = self.policy_0.act_on(*args)
            self.lastSystemAction = self.policy_0.lastSystemAction
            self.policy_0_c += 1
        elif group == 1:
            system_action = self.policy_1.act_on(*args)
            self.lastSystemAction = self.policy_1.lastSystemAction
            self.policy_1_c += 1
        else:
            logger.error('Unknown group {}'.format(group))

        # necessary storage for Agent (in case of context switches)
        return system_action

    def record(self, *args, **kwargs):
        if self.policy_0_c > 0:
            self.policy_0.record(*args, **kwargs)
        if self.policy_1_c > 0:
            self.policy_1.record(*args, **kwargs)

    def finalizeRecord(self, *args, **kwargs):
        if self.policy_0_c > 0:
            self.policy_0.finalizeRecord(*args, **kwargs)
        if self.policy_1_c > 0:
            self.policy_1.finalizeRecord(*args, **kwargs)

    def loadPolicy(self, filename):
        """
        load model and replay buffer
        """
        self.policy_0.loadPolicy(filename + 'p0')
        self.policy_1.loadPolicy(filename + 'p1')

    def savePolicy(self, FORCE_SAVE=False):
        self.policy_0.savePolicy(FORCE_SAVE)
        self.policy_1.savePolicy(FORCE_SAVE)

    def restart(self):
        self.lastSystemAction = None
        self.policy_0_c = 0
        self.policy_1_c = 0
        self.policy_0.restart()
        self.policy_1.restart()

    def train(self):
        if self.policy_0_c > 0:
            self.policy_0.train()
        if self.policy_1_c > 0:
            self.policy_1.train()

    def convertStateAction(self, state, action):
        if self.base_policy is GPPolicy:
            return self.policy_0.convertStateAction(state, action)
        else:
            return super(SplitPolicy, self).convertStateAction(state, action)

