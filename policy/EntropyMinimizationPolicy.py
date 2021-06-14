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
EntropyMinimizationPolicy.py - Dialogue manager that asks questions to minimize entropy of final
answer.
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
import collections
import cPickle as pickle

import Policy
import PolicyUtils
import SummaryUtils
import SummaryAction
import RandomQuestionPolicy
from Policy import TerminalAction, TerminalState
from ontology import Ontology
import numpy as np
from utils import ContextLogger, Settings, DiaAct
from replay_buffer_entropy_minimization import ReplayBufferEpisode
import scipy
import math
logger = ContextLogger.getLogger('')

NONE_MARKER = "**NONE**"
NULL_ACTION_MARKER = "null()"

class EntropyMinimizationPolicy(Policy.Policy):
    """
    A policy that derives from Policy base class. Selects respond so as to minimize the entropy
    of the final conversation.
    """

    def __init__(self, in_policy_file, out_policy_file, domainString, learning=False):
        super(EntropyMinimizationPolicy, self).__init__(domainString, learning)

        self.in_policy_file = in_policy_file
        self.out_policy_file = out_policy_file
        self.learning = learning 
        self.user_act = None
        self.summaryaction = SummaryAction.SummaryAction(domainString)

        # Initialise replay buffer
        # Contains semantic representation of the utterances so far, {q1,...,qn} in the Entropy
        # Minimization paper
        self.episodes[domainString] = ReplayBufferEpisode(domainString, random=Settings.random)
        n_entities_in_domain = Ontology.global_ontology.get_db(self.domainString).get_num_unique_entities(cols=['name'])
        # the maximum entropy for the number of 'categories' (e.g. names) in the database
        self.max_db_entropy = math.log(n_entities_in_domain, math.e)
        self.n_actions = len(self.summaryaction.action_names)

        if in_policy_file:
            self.loadPolicy(self.in_policy_file)
    
    def act_on(self, state, user_act=None, hyps=None):
        """
        Returns action based on state and hyps.
        """
        systemAct, nextaIdex = self.nextAction(state)
        #if self.lastSystemAction is None and self.startwithhello:
        #    systemAct, nextaIdex = 'hello()', -1
        #else:
        #    logger.dial('calling nextAction')
        #    systemAct, nextaIdex = self.nextAction(state)

        self.lastSystemAction = systemAct
        self.summaryAct = nextaIdex
        self.prevbelief = state

        systemAct = DiaAct.DiaAct(systemAct)
        return systemAct

    def entropy(self, action_index, user_act):
        """
        Computes the entropy of answers for a given action_index.
        """
        # construct one-step lookahead and extract answer sample from history
        user_act = DiaAct.DiaAct(unicode(user_act))
        lookahead = self.episodes[self.domainString].episode_em + [user_act, action_index]

        sample = np.array(self.episodes[self.domainString].sample_batch(lookahead))
        # compute the probability distribution for the sample
        # compute entropy for the given sample

        # if sample size < 1: use uniform probabilities (e.g. all possible recommendations
        # * the item they recommended).
        sample_length = len(sample)
        if sample_length < 1:
            entropy = self.max_db_entropy
            logger.debug("No experiences yet, using max entropy from db")
        else:
            _, counts = np.unique(sample, return_counts=True)
            counts = counts.astype('float')
            probs = counts / counts.sum()
            entropy = scipy.stats.entropy(probs)
            logger.debug("Computing entropy from "+ str(sample_length) + " similar situations")
        return entropy


    def nextAction(self, beliefstate):
        '''
        select next action

        :param beliefstate: 
        :param hyps:
        :returns: (int) next summary action
        '''
        # Access the semantified conversation history with master action ({q1,...,qn} in the
        # paper) with final outcomes.

        #self.stats[nextaIdex] += 1
        #summaryAct = self.summaryaction.action_names[nextaIdex]
        #beliefstate = beliefstate.getDomainState(self.domainUtil.domainString)
        #masterAct = self.summaryaction.Convert(beliefstate, summaryAct, self.lastSystemAction)
        #return masterAct, nextaIdex
        if len(self.episodes[self.domainString].episode_em) < 1:
            logger.debug('Episode is new')
            nextaIdex = self.summaryaction.action_names.index('hello')
        else:
            aIdex = self.summaryaction.action_names.index('inform_byname')
            user_acts = beliefstate.userActs()[self.domainString]
            uact = max(user_acts, key=lambda x: x[1])[0]

            # For each possible summary action qn+1:
            #   For each possible 'answer'/final outcome of the conversation a \in A
            #       * compute P(a|{q1,...,qn+1})
            #   * compute entropy all outcomes H(A|{q1,...,qn+1}
            # NOTE: parallelize?
            # map summaryActions -> entropy
            summary_entropy_map = {summary_action_index: self.entropy(summary_action_index, uact)
                    for summary_action_index in range(len(self.actions.action_names))}
            entropies = summary_entropy_map.values()
            # Check if all entropies are equal
            if len(set(entropies)) == 1:
                # select a random action
                logger.debug('Equal entropies, select action randomly')
                nextaIdex = Settings.random.randint(0, self.n_actions)
            else:
                # Select question resulting in minimal entropy
                logger.debug('Different entropies, select by entropy')
                nextaIdex = min(summary_entropy_map, key=summary_entropy_map.get)
                logger.debug('action with min entropy: ' +  str(nextaIdex) + "/" +
                        str(self.summaryaction.action_names[nextaIdex]))

        summary_action = self.summaryaction.action_names[nextaIdex]
        beliefstate = beliefstate.getDomainState(self.domainString)
        return self.summaryaction.Convert(beliefstate, summary_action, self.lastSystemAction), nextaIdex

    def finalizeRecord(self, reward, domainInControl = None, task=None):
        '''
        Records the final reward along with the terminal system action and terminal state. To change the type of state/action override :func:`~convertStateAction`.
        
        This method is automatically executed by the agent at the end of each dialogue.
        
        :param reward: the final reward
        :type reward: int
        :param domainInControl: used by committee: the unique identifier domain string of the domain this dialogue originates in, optional
        :type domainInControl: str
        :returns: None
        :param task: list of constraints the user had for this domain
        :type task: list of tuples (slot, operator, slotvalue)
        '''
        if domainInControl is None:
            domainInControl = self.domainString
        if self.episodes[domainInControl] is None:
            logger.warning("record attempted to be finalized for domain where nothing has been recorded before")
            return
        if task is None:
            task = []

        terminal_state, terminal_action = self.convertStateAction(TerminalState(), TerminalAction())        
        episode = self.episodes[domainInControl].episode
        
        # record the record always, but only store it if is was a succesfull recommendation
        self.episodes[domainInControl].record(state=terminal_state, action=terminal_action,
                summaryAction=None, reward=reward, task=task, terminal=True)
        return

    def savePolicy(self, FORCE_SAVE=False):
        """
        save model and replay buffer
        """
        f = open(self.out_policy_file+'.episode', 'wb')
        self.episodes[self.domainString].episode_em = []
        pickle.dump(self.episodes[self.domainString], f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        #logger.info("Saving model to %s and replay buffer..." % save_path)

    def loadPolicy(self, filename):
        """
        load model and replay buffer
        """
        # load replay buffer
        print 'load from: ', filename
        try:
            f = open(filename+'.episode', 'rb')
            self.episodes[self.domainString] = pickle.load(f)
            logger.info("Loading both model from %s and replay buffer..." % filename)
            logger.info("Size of loaded buffer %d" % len(self.episodes[self.domainString].buffer))
            f.close()
        except:
            logger.warning(filename +".episode not found, using pristine policy")

    def record(self, reward, domainInControl=None, weight=None, state=None, action=None):
        """
        Records a turn e.g. a state-action-reward(-state) tuple.
        """
        if domainInControl is None:
            domainInControl = self.domainString
        if self.actToBeRecorded is None:
            self.actToBeRecorded = self.summaryAct

        action = self.actToBeRecorded

        # Store in self.episodes
        # A2C stores a bunch of things, including the predicted value (useful for replay?)
        if domainInControl is None:
            domainInControl = self.domainString
        if self.episodes[domainInControl] is None:
            self.episodes[domainInControl] = Episode(dstring=domainInControl)
        if self.actToBeRecorded is None:
            self.actToBeRecorded = self.lastSystemAction
            
        if state is None:
            state = self.prevbelief
        if action is None:
            action = self.actToBeRecorded
            
        cState, cAction = self.convertStateAction(state, action)
        
        if weight == None:
            self.episodes[domainInControl].record(state=cState, action=cAction,
                    summaryAction=action, reward=reward)
        else:
            self.episodes[domainInControl].record(state=cState, action=cAction,
                    summaryAction=action, reward=reward, ma_weight = weight)

        self.actToBeRecorded = None
        return

    def restart(self):
        '''
        Restarts the policy. Resets internal variables.
        
        This method is automatically executed by the agent at the end/beginning of each dialogue.
        '''
        self.actions.reset() # ic340: this should be called from every restart impelmentation

