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
RegexSemI_Loans.py - regular expression based Loans SemI decoder
===============================================================


HELPFUL: http://regexr.com

"""

import RegexSemI_generic
import re,os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from utils import ContextLogger
logger = ContextLogger.getLogger('')


class RegexSemI_Loans(RegexSemI_generic.RegexSemI_generic):
    """
    """
    def __init__(self, repoIn=None):
        self.domainTag = "Loans"
        RegexSemI_generic.RegexSemI_generic.__init__(self, self.domainTag)  #better than super() here - wont need to be changed for other domains
        self.create_domain_dependent_regex() 

    def create_domain_dependent_regex(self):
        """
        """
        super(RegexSemI_Loans, self).create_domain_dependent_regex()
        self.slot_vocab['interestrate'] = '(interest|(interest rate)|rate)'
        self.slot_vocab['haspurpose'] = '((has)?(\ purpose))'
        self.slot_vocab['hasmaximumprincipal'] = '((has)?(\ max(imum)?)(\ principal))'
        self.slot_vocab['hasminimalprincipal'] = '((has)?(\ minimal)(\ principal))'
        self.slot_vocab['hasmaximumduration'] = '((has)?(\ max(imum)?)(\ duration))'
        self.slot_vocab['hasminimalduration'] = '((has)?(\ minimal)(\ duration))'
        self.slot_vocab['hasmaximumage'] = '((has)?(\ max(imum)?)(\ age))'
        self.slot_vocab['hasminimalage'] = '((has)?(\ minimal)(\ age))'
        self.slot_vocab['requiresaccount'] = '((require|requires)?(\ account))'
        self.slot_vocab['bkrregistration'] = '((bkr)?(\ registration))'
        self.slot_vocab['bkrtest'] = '((bkr)?(\ test))'
        self.slot_vocab['allowsforrepaymentwithdrawal'] = '((withdraw)(\ repayments))'
#        self.slot_vocab[''] = '()'
        # Generate regular expressions for requests:
        self._set_request_regex()
            
        # FIXME:  many value have synonyms -- deal with this here:
        self._set_value_synonyms()  # At end of file - this can grow very long
        self._set_inform_regex()


    def _set_request_regex(self):
        """
        """
        self.request_regex = dict.fromkeys(self.USER_REQUESTABLE)
        for slot in self.request_regex.keys():
            # FIXME: write domain dependent expressions to detext request acts
            self.request_regex[slot] = self.rREQUEST+"\ "+self.slot_vocab[slot]
            self.request_regex[slot] += "|(?<!"+self.DONTCAREWHAT+")(?<!want\ )"+self.IT+"\ "+self.slot_vocab[slot]
            self.request_regex[slot] += "|(?<!"+self.DONTCARE+")"+self.WHAT+"\ "+self.slot_vocab[slot]

        # FIXME:  Handcrafted extra rules as required on a slot to slot basis:
        #self.request_regex["pricerange"] += "|(how\ much\ is\ it)"
        #self.request_regex["food"] += "|(what\ (type\ of\ )*food)"
        #self.request_regex["phone"] += "|(phone(\ num(ber)*)*)"
        #self.request_regex["postcode"] += "|(postcode)|(post\ code)|(zip\ code)"
        #self.request_regex["addr"] += "|(address)"
        #self.request_regex["signature"] += "|(signature)|(best\ dish)|(specialty)|(recipe)"
        #self.request_regex["description"] += "|(description)|(more\ information)|(more\ details)|(describe)"

    def _set_inform_regex(self):
        """
        """
        self.inform_regex = dict.fromkeys(self.USER_INFORMABLE)
        for slot in self.inform_regex.keys():
            self.inform_regex[slot] = {}
            for value in self.slot_values[slot].keys():
                if value == 'car':
                    pattern = "(car[^e])"
                else:
                    pattern = self.slot_values[slot][value]
                self.inform_regex[slot][value] = self.rINFORM+"\ "+pattern
                self.inform_regex[slot][value] += "|"+ pattern+ self.WBG
                #self.inform_regex[slot][value] += "|((what|about|which)(\ (it\'*s*|the))*)\ "+slot+"(?!\ (is\ it))" 
                self.inform_regex[slot][value] += "|(\ |^)"+ pattern + "(\ (please|and))*"
                
                
                # FIXME:  Handcrafted extra rules as required on a slot to slot basis:

            # FIXME: value independent rules 
            # TODO: Should these be included to support the dontcare case?
            #nomatter = r"\ doesn\'?t matter"
            #dontcare = r"((any(\ (kind|type)(\ of)?)?)|((i\ )?(don\'?t|do\ not)\ care\ (what|which|a?bout|for))(\ (kind|type)(\ of)?)?)\ "
            #if slot == "pricerange":
            #    slot_term = r"(the\ )*(price|price(\ |-)*range)"
            #    self.inform_regex[slot]['dontcare'] = dontcare+slot_term
            #    self.inform_regex[slot]['dontcare'] += r"|" + slot_term + nomatter

            #if slot == "area":
            #    LOCATION = r"(area|location|place|part\ of\ town)"
            #    slot_term = r"(the\ )*"+LOCATION
            #    self.inform_regex[slot]['dontcare'] = dontcare+slot_term
            #    self.inform_regex[slot]['dontcare'] += r"|" + slot_term + nomatter
            #    self.inform_regex[slot]['dontcare'] += r"|any(\ ?where)(\ is\ (fine|ok\b|good|okay))?"
            #    
            #if slot == "food":
            #    slot_term = r"(the\ )*"+slot
            #    self.inform_regex[slot]['dontcare'] = dontcare+slot_term
            #    self.inform_regex[slot]['dontcare'] += r"|" + slot_term + nomatter

        
    def _decode_confirm(self, obs):
        """
        """
        #TODO?
        pass


    # TODO: udpate these
    pass
    #def _set_value_synonyms(self):
    #    """Starts like: 
    #        self.slot_values[slot] = {value:"("+str(value)+")" for value in DOMAINS_ontology["informable"][slot]}
    #        # Can add regular expressions/terms to be recognised manually:
    #    """
        #FIXME: 
        #---------------------------------------------------------------------------------------------------
        # TYPE:
        #self.inform_type_regex = r"(restaurant|cafe|(want|looking for) food|(place|some(thing|where)) to eat)"
        # SLOT: area 
        #slot = 'area'
        # {u'west': '(west)', u'east': '(east)', u'north': '(north)', u'south': '(south)', u'centre': '(centre)'}
        #self.slot_values[slot]['north'] = "((the)\ )*(north|kings\ hedges|arbury|chesterton)"
        #self.slot_values[slot]['east'] = "((the)\ )*(east|castle|newnham)"
        #self.slot_values[slot]['west'] = "((the)\ )*(west|abbey|romsey|cherry hinton)"
        #self.slot_values[slot]['south'] = "((the)\ )*(south|trumpington|queen ediths|coleridge)"
        #self.slot_values[slot]['centre'] = "((the)\ )*(centre|center|downtown|central|market)"  # lmr46, added rule for detecting the center
#         self.slot_values[slot]['dontcare'] = "any(\ )*(area|location|place|where)"    
        # SLOT: pricerange
        #slot = 'pricerange'
        # {u'moderate': '(moderate)', u'budget': '(budget)', u'expensive': '(expensive)'}
        #self.slot_values[slot]['moderate'] = "(to\ be\ |any\ )*(moderat|moderate|moderately\ priced|mid|middle|average)"
        #self.slot_values[slot]['moderate']+="(?!(\ )*weight)"
        #self.slot_values[slot]['cheap'] = "(to\ be\ |any\ )*(budget|cheap|bargin|bargain|inexpensive|cheapest|low\ cost)"
        #self.slot_values[slot]['expensive'] = "(to\ be\ |any\ )*(expensive|expensively|dear|costly|pricey)"
#         self.slot_values[slot]['dontcare'] = "any\ (price|price(\ |-)*range)"
        # SLOT: food
        #slot = "food"
        # rely only on ontology values for now
        #self.slot_values[slot]["asian oriental"] = "(oriental|asian)"
        #self.slot_values[slot]["gastropub"] = "(gastropub|gastro pub)"
        #self.slot_values[slot]["italian"] = "(italian|pizza|pasta)"
        #self.slot_values[slot]["north american"] = "(american|USA)"
        
        #---------------------------------------------------------------------------------------------------

#END OF FILE
