import argparse
import json

# From SummaryAction.SummaryAction
actions = [ "inform", "inform_byname", "inform_alternatives", "bye", "repeat", "reqmore",
        "restart", "hello",]
parser = argparse.ArgumentParser(description='Determine size of ontology for e.g. DL network inputs')
parser.add_argument('ontologyfile', metavar='ontologyfile', nargs=1)


args = parser.parse_args()
ont_f = args.ontologyfile[0]

with open(ont_f) as f:
    ontology = json.load(f)

informables_size = sum(map(len, ontology['informable'].values()))
informables_none_and_dontcare = len(ontology['informable']) * 2

system_requestable_actions = len(ontology['system_requestable']) * 3

method = 6 
discourseact_size = len(ontology['discourseAct'])
requestable_size = len(ontology['requestable'])
matches_beliefs = 5*4 + 5*1
lastActionInformNone = 1
offerhappened = 1

input_size = sum([
    informables_size,
    informables_none_and_dontcare,
    method,
    discourseact_size,
    requestable_size,
    matches_beliefs,
    lastActionInformNone,
    offerhappened,
    ])

action_size = len(actions) + system_requestable_actions

print("Input size: \t {}".format(input_size))
print("Action size: \t {}".format(action_size))
