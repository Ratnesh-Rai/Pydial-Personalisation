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
RandomQuestionPolicy.py - Dialogue manager that randomly asks for desired feature until no
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
logger = ContextLogger.getLogger('')

NONE_MARKER = "**NONE**"
NULL_ACTION_MARKER = "null()"

class RandomQuestionPolicy(Policy.Policy):
    """
    Random Question policy derives from Policy base class. Randomly requests attributes until
    either all attributes are known or a single item remains in scope.
    
    """
    def __init__(self, domainString, summary_belief_threshold, acceptable_entity_threshold=1):
        '''
        Initializes a RandomQuestionPolicy

        :param domainString: str representing the domain for this policy
        :param summary_belief_threshold: float representing the threshold after which the
        certainty of the value for a slot given the current belief is deemed sufficient to be
        accepted
        :param acceptable_entity_threshold: int representing the threshold on number of entities
        still open given the currently accepted contraints after which a recommendation will be
        made

        '''
        super(RandomQuestionPolicy, self).__init__(domainString) # inherited from Policy.Policy() is self.domainString

        self.acceptable_entity_threshold = acceptable_entity_threshold
        self.global_belief_threshold = summary_belief_threshold


    def get_global_action(self, global_summary, belief):
	"""
	Hardcoded action selection based on global_summary.
	"""
        # Describes 'global' state of the conversation using 'global summary features'
        logger.debug('Belief summarized as: ' + pprint.pformat(global_summary))
        if global_summary['GLOBAL_FINISHED']:
            return PolicyUtils.getGlobalAction(belief, 'BYE', domainString=self.domainString)
        elif global_summary['GLOBAL_RESTART']:
            return PolicyUtils.getGlobalAction(belief, 'RESTART', domainString=self.domainString)
        elif global_summary['GLOBAL_REPEAT']:
            return PolicyUtils.getGlobalAction(belief, 'REPEAT', domainString=self.domainString)
        elif global_summary['GLOBAL_BYNAME']:
            return PolicyUtils.getGlobalAction(belief, 'INFORM_REQUESTED', domainString=self.domainString)
        elif (global_summary['GLOBAL_REQMORE'] or
             global_summary['GLOBAL_THANKYOU'] or
             global_summary['GLOBAL_ACK']):
            return PolicyUtils.getGlobalAction(belief, 'REQMORE', domainString=self.domainString)
        elif global_summary['GLOBAL_BYALTERNATIVES']:
            return PolicyUtils.getGlobalAction(belief, 'INFORM_ALTERNATIVES', domainString=self.domainString)
	return None

    def recommend_entity(self, accepted_constraints, acceptable_entities):
	"""
	Select an entity from `acceptable_entities` and 
	"""
	# TODO: add possibility for multiple recommendations at once...
	#   * reimplement getInformExactEntity to support this
	#   * change the expression below to use new implementation
	#   * add entries for multiple informs in template. Idea: include some
	#   differentiating features of the recommended entities
	n_acceptable_entities = len(acceptable_entities)
	accepted_constraints_flat = PolicyUtils.flattenBelief(accepted_constraints)

	discriminable = Ontology.global_ontology.isDiscriminable(self.domainString,
								 accepted_constraints_flat)
	    
	logger.debug("Accepted {} constraints, yielding {} acceptable entities which are {} discriminable".format(accepted_constraints,
	    n_acceptable_entities, discriminable))
	if (n_acceptable_entities > 0 and 
	    (n_acceptable_entities <= self.acceptable_entity_threshold or not discriminable or
		len(accepted_constraints) ==
		    Ontology.global_ontology.get_length_system_requestable_slots(self.domainString))):
	    random_entity = Settings.random.choice(acceptable_entities,1)[0]
	    return PolicyUtils.getInformAcceptedSlotsAboutEntity(accepted_constraints,
								random_entity,
								float('inf'))
	elif n_acceptable_entities == 0:
	    # No acceptable candidates found, inform user on this
		accepted_constraint_values = {key: value[0] for key, value in accepted_constraints.items()}
		return SummaryUtils.getInformNoneVenue(accepted_constraint_values)
	else:
	    return None

    def get_constraints_verification(self, belief):
	# Get list of all slots
	slots = Ontology.global_ontology.get_sorted_system_requestable_slots(self.domainString)
	Settings.random.shuffle(slots) # in-place operation
	for slot in slots:
	    # sort slot belief values by belief value (highest belief values first)
	    # store as list of tuples [(slotvalue, certainty),..].
	    # break if an action has been found
	    sorted_belief = sorted(belief['beliefs'][slot].items(), key=lambda tup:
				   tup[1], reverse=True)
	    top_certainty = sorted_belief[0][1]

	    if top_certainty < self.global_belief_threshold:
		if(sorted_belief[1][0] != NONE_MARKER
		   and top_certainty - sorted_belief[1][1] < .2):
		    return PolicyUtils.getSelect(slot, sorted_belief[0][0],
						sorted_belief[1][0])
		elif top_certainty > .6:
		    return PolicyUtils.getConfirm(slot=sorted_belief[0][0])
	return None

    def get_additional_constraints(self, accepted_constraints):

	accepted_constraints_flat = PolicyUtils.flattenBelief(accepted_constraints)
	discriminable = Ontology.global_ontology.isDiscriminable(self.domainString,
								 accepted_constraints_flat)
	all_slots = set(Ontology.global_ontology.get_sorted_system_requestable_slots(
		self.domainString))
	uncertain_slots = all_slots - set(accepted_constraints.keys())
	# Ask a random question
	if(discriminable and len(uncertain_slots) > 0):
	    # TODO: include logic for confreq():
	    #  * if more than 3 slots with top probability < .8 
	    #  * and use_confreq is set in the config (never in the supplied confs)
	    #  * then do a confreq action, e.g. 'implicitly ask for confirmation' by
	    # listing the top values for these slots

	    # ask a random question from the available (=uncertain) slots
	    ask_for = Settings.random.choice(list(uncertain_slots), 1)[0]
	    return PolicyUtils.getRequest(ask_for)
	return None

    def nextAction(self, belief):
        '''
        Selecting the next system action.
        
        This method is automatically executed by :func:`~act_on` thus at each turn.
        
        :param belief: the state the policy acts on
        :type belief: dict
        :returns: the next system action
        '''
        act = None
        logger.debug('Selecting action based on: ' + pprint.pformat(belief))
        
        # 1. analogous to HDC's getGlobal
        global_summary = SummaryUtils.globalSummary(belief, domainString=self.domainString)
	act = self.get_global_action(global_summary, belief)
        
	if act == None: 
	    # Check how many db entities are available given current constraints,
            # using some parameter for certainty
            accepted_constraints = SummaryUtils.getTopBeliefs(belief,
                                                              self.global_belief_threshold,
                                                              domainString=self.domainString)
	    accepted_constraints_dact = PolicyUtils.dactItemBelief(accepted_constraints)
	    accepted_constraints_flat = PolicyUtils.flattenBelief(accepted_constraints)

            # filter all items by the items available according to accepted constraints
            acceptable_entities = Ontology.global_ontology.entity_by_features(self.domainString,
                                                                              accepted_constraints_dact)
            n_acceptable_entities = len(acceptable_entities)
            # 2. analogous to HDC's getInform
	    # recommend acceptable entities 
	    act = self.recommend_entity(accepted_constraints, acceptable_entities)
            # 3. analogous to HDC's getConfirmSelect
	    if act == None:
		act = self.get_constraints_verification(belief)
            if act == None:
                # 4. analogous to HDC's getRequest
                # Check if there is a differentiating question left to ask (assuming accepted
                # constraints)
		act = self.get_additional_constraints(accepted_constraints)
	    if act == None: 
		logger.debug("Could not find suitable action: " + pprint.pformat(belief))
		act = PolicyUtils.getReqMore()
	if act == None:
	    # Should not happen
	    logger.error(
		"No action at end of policy: " + pprint.pformat(belief))
	    act = PolicyUtils.getReqMore()
        return act

