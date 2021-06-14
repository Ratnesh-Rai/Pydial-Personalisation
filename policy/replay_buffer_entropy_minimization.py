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

""" 
Data structure for implementing experience replay, episode level
"""
from collections import deque
import numpy as np
from Policy import Action, State, TerminalAction, TerminalState
from utils import ContextLogger, Settings, DiaAct
from evaluation.SuccessEvaluator import ObjectiveSuccessEvaluator
import pprint
import operator
import copy
logger = ContextLogger.getLogger('')

REWARD_INDEX = 2
TERMINAL_BOOL_INDEX = -1
EPISODE_VARS_LEN = 6

global_buffer = {}

class ReplayBufferEpisode():

    def __init__(self, domainString, buffer_size=float('inf'), batch_size=float('inf'), random=None):
        """
        The right side of the deque contains the most recent experiences 
        """
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.count = 0
#        self.buffer = deque()
        self.buffer = global_buffer
        self.finals_only = []
        self.random = random
        self.domainString = domainString
        self.episode = []
        self.episode_em = []
        self.s_prev, self.a_prev, self.r_prev = (None,)*3

    def list_to_tuples(self, to_tuple):
        """
        recursively turns all lists into a multidimensional input_list
        into tuples.
        """
        return tuple(map(self.list_to_tuples, to_tuple)) if isinstance(to_tuple, (list ,tuple)) else to_tuple

    def get_base_acts(self, state):
        system_act = state.state.getLastSystemAct(self.domainString)
        user_acts = state.state.userActs()[self.domainString]
        return system_act, user_acts

    def to_base_acts(self, episode):
        sequence_to_store = []
        final_answer = False
        for elem in episode:
            state = elem[0]
            if not isinstance(state.state, TerminalState):
                (system_act, user_acts) = self.get_base_acts(state)
                sequence_to_store.append(system_act)
                sequence_to_store.append(user_acts)
        return self.list_to_tuples(sequence_to_store)
    
    def validate_success(self, task, episode):
        sequence_to_store = []
        final_answer = False
        for count, elem in enumerate(episode):
            state = elem[0]
            if not isinstance(state.state, TerminalState):
                (system_act, _) = self.get_base_acts(state)
                if system_act is not None and system_act.act == 'inform':
                    # Check if name is in fields, it's a recommendation then
                    name_items = filter(lambda dact_item: dact_item.slot == 'name' and dact_item.op == '=',
                            system_act.items)
                    n_name_items = len(name_items)
                    if n_name_items > 1:
                        logger.warning("Recommending many items at once!")

                    # Although multiple recommendation are allowed, only one correct
                    # recommendation is stored
                    for item in name_items:
                        # validate the recommendation against the constraints
                        if(ObjectiveSuccessEvaluator._isValidVenueStatic(item.val, task,
                            self.domainString)):
                            final_answer = system_act
                            # skip final system-user pair when answer was found
                            sequence_to_store = self.episode_em[:(count * 2)-1]
                            break
        return (final_answer, sequence_to_store)


    def store_em_specific(self, sequence_to_store, answer_to_store):
        """
        Stores the current record as a ((q1,...,qn), A) tuple
        """
        # TODO: implement usage of buffer size
        sequence_to_store = self.list_to_tuples(sequence_to_store)
        # We assume we only inform by constraints
        answer_to_store = filter(lambda i: i.slot == 'name', answer_to_store.items)[0].val
        self.finals_only.append(answer_to_store)
        for subseq in range(1, len(sequence_to_store)+1):
            subseq_to_store = sequence_to_store[:subseq]
            if subseq_to_store in self.buffer:
                self.buffer[subseq_to_store].append(answer_to_store)
            else:
                self.buffer[subseq_to_store] = [answer_to_store,]

    def record_em_specific(self, state, action):
        (_, user_act) = self.get_base_acts(state)
        # Extract only the actions itself, drop the confidence scores under the assumption that
        # the maximum one is the right one. This is necessary as Entropy Minimization cannot deal
        # with uncertainty.
        if len(user_act) < 1:
            logger.warning('No user acts!')
            self.episode_em.append(action)
            return
        user_act_max_conf = max(user_act, key=lambda i: i[1])[0]
        # NOTE: assumes that system initiates conversation
        self.episode_em.extend([DiaAct.DiaAct(user_act_max_conf), action])

    def record(self, state, action, summaryAction, reward, task=None, terminal=False):
        """
        Records s, a, r, s' tuples:

        Record the experience:
            Turn #  User: state         System: action                  got reward
            Turn 1  User: Cheap         System: location?               -1
            Turn 2  User: North         System: inform(cheap, north)    -1    
            Turn 3  User: Bye           System: inform(XXX) --> bye     -1
            Turn 4  User: Terminal_s    System: terminal_a              20

        As:
            Experience 1: (Cheap, location?, -1, North)
            Experience 2: (North, inform(cheap, north), -1+20, Bye)
        """
        # make a deepcopy, since the belieftrackingmanager mutates state
        state = copy.deepcopy(state)
        if (all(map(lambda x: x == None, [self.s_prev, self.a_prev, self.r_prev,]))):
            self.s_prev, self.a_prev, self.r_prev = \
                            state, action, reward
            self.record_em_specific(state, summaryAction)
            return
        else:
            if terminal and len(self.episode_em) > 0:
                #- 1  # add dialogue succes reward to last added experience , -1 for goodbye turn
                self.episode[-1][REWARD_INDEX] += reward

                # change this experience to terminal
                self.episode[-1][TERMINAL_BOOL_INDEX] = terminal
                
                # check if the dialogue was successful
                (answer_to_store, sequence_to_store) = self.validate_success(task,
                        self.episode)

                # add episodic experience to buffer
                if answer_to_store:
                    self.store_em_specific(self.episode_em, answer_to_store) 

                self.s_prev, self.a_prev, self.r_prev = (None,)*3
                self.episode = []
                self.episode_em = []
            else: # not terminal state
                self.record_em_specific(state, summaryAction)
                self.episode.append(\
                        [self.s_prev,
                         self.a_prev,
                         self.r_prev,
                         state,
                         terminal,
                        ])
                self.s_prev, self.a_prev, self.r_prev = state, action, reward
                self.count += 1

    def size(self):
        return self.count

    def sample_batch(self, history=None):
        """
        Returns a sample of `batch_size` from the history, stored describing the states, actions,
        rewards, resulting states and an array indicating whether it was the terminal state (e.g.
        only `True` for the final item in the sample.
        """
        if history is None:
            history = self.episode_em
        history = self.list_to_tuples(history)
        batch = []
        count = len(self.buffer)
        if count < 1:
            return self.finals_only
        elif count < self.batch_size:
            batch_size = count
        else:
            batch_size = self.batch_size
        # TODO: implement different batch sizes
        #   * turn the episode so far into tuples
        #   * filter the buffer for the episode so far
        #   * draw sample of size `batch_size`

        # if batch_size == 1:
        #     batch = self.buffer 
        # else:
        #     batch_ids = self.random.random_integers(0, self.count-1, batch_size)
        #     batch = operator.itemgetter(*batch_ids)(self.buffer)
        try:
            batch = self.buffer[history]
        except KeyError:
            batch = self.finals_only
        return batch

    def clear(self):
        #self.buffer.clear()
        self.count = 0
        self.s_prev, self.a_prev, self.r_prev, = None, None, None, None, None
        self.episode = []
        self.episode_em = []
