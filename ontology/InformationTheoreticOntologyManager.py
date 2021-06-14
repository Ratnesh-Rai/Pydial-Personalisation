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
InformationTheoreticOntologyManager.py - Domain class and Multidomain API
==========================================================

Copyright CUED Dialogue Systems Group 2015 - 2017

Controls Access to the ontology files.

.. seealso:: CUED Imports/Dependencies: 

    import :mod:`utils.Settings` |.|
    import :mod:`utils.ContextLogger` |.|
    import :mod:`ontology.OntologyUtils`
    import :mod:`ontology.FlatOntologyManager`

************************

'''

__author__ = "Floris den Hengst <f.den.hengst@vu.nl"
import copy, math, json
import numpy as np

import os
import DataBaseSQLite
from ontology import OntologyUtils
from FlatOntologyManager import FlatOntologyManager
from utils import Settings, ContextLogger
logger = ContextLogger.getLogger('')

class InformationTheoreticOntologyManager(FlatDomainOntologyManager):
    '''Utilities for information theoretic ontology queries.
    Implements some additional functions to the FlatDomainOntology to do some Information
    Theoretic Conversation planning and evaluation.
    '''
    def __init__(self, domain_string, root_in=None):
        super(InformationTheoreticOntologyManager, self).__init__(domain_string, root_in)
        # TODO: initiliase information space (if we can here)

    def getOptimalDiscriminatedConstraint(self, constraints):
        '''
        Returns a constraint that halves the available information space, that is: the information
        space adhering to ``constraints``, without considering uncertainty.
        '''


