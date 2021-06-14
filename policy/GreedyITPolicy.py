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
GreedyITPolicy.py - Dialogue manager that greedily navigates through information space
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

import HDCPolicy 
import SummaryUtils
from ontology import Ontology
from utils import ContextLogger, Settings
logger = ContextLogger.getLogger('')


class GreedyITPolicy(HDCPolicy.HDCPolicy):
    """
    Handcrafted policy derives from Policy base class. Based on the slots defined in the ontology and fix thresholds, defines a rule-based policy. 
    
    If no info is provided by the user, the system will always ask for the slot information in the same order based on the ontology. 
    """
    def __init__(self, domainString):
        super(GreedyITPolicy, self).__init__(domainString) # inherited from Policy.Policy() is self.domainString


    def _getRequest(self, belief, array_slot_summary):
        '''
        Selects a slot to request from the user.
        '''

        # This is added for confreq.
        need_grounding = SummaryUtils.getTopBeliefs(belief, 0.8, domainString=self.domainString)

        for slot in Ontology.global_ontology.get_sorted_system_requestable_slots(self.domainString):
            summary = array_slot_summary[slot]
            (_, topprob) = summary['TOPHYPS'][0]
            #(_, secprob) = summary['TOPHYPS'][1]

            if topprob < 0.8:
                # Add implicit confirmation (for confreq.)
                grounding_slots = copy.deepcopy(need_grounding)
                if slot in grounding_slots:
                    del grounding_slots[slot]

                grounding_result = []
                for grounding_slot in grounding_slots:
                    if len(grounding_result) < 3:
                        (value, _) = grounding_slots[grounding_slot]
                        #(value, prob) = grounding_slots[grounding_slot]
                        grounding_result.append('%s="%s"' % (grounding_slot, value))

                if not grounding_result or not self.use_confreq:
                    return True, 'request(%s)' % slot
                else:
                    return True, 'confreq(' + ','.join(grounding_result) + ',%s)' % slot

        return False, 'null()'

