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
NaiveEntropyPolicy.py - Dialogue manager that asks questions based on the DB entropy of not-yet
accepted slots
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
import RandomQuestionPolicy
from ontology import Ontology
from utils import ContextLogger, Settings
logger = ContextLogger.getLogger('')

NONE_MARKER = "**NONE**"
NULL_ACTION_MARKER = "null()"

class NaiveDatabaseEntropyPolicy(RandomQuestionPolicy.RandomQuestionPolicy):
    """
    A policy that derives from RandomQuestionPolicy base class. Selects question that is expected to maximally
    reduce the entropy of not-yet-accepted fields in the database. 
    """

    def get_additional_constraints(self, accepted_constraints):
        """
        Asks for additional constraint based on minimizing remaining entropy in the entity
        database.
        """
        slot = Ontology.global_ontology.max_entropy_slot(self.domainString,
                                                         accepted_constraints)
        if not slot:
            return None
        else:
            return PolicyUtils.getRequest(slot)

