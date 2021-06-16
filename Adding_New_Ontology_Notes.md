Pydial implements many different algorithms.

* Train the agent: ``python pydial.py train config/<myconfig-abc> [--trainerrorrate=10]``
* Plot train results: ``python pydial.py plot _tutoriallogs/*train*``
* Test using custom parameters: ``python pydial test config/<myconfig-abc> <iteration>
  --trainerrorrate=10 --testerrorrate='(0,10,50)'``
* Plot test results: ``python pydial plot _tutoriallogs/*eval* --printtab``
* Chat with trained agent: ``python pydial.py chat _tutorialconfigs/<my-setup>.eval.cfg``

# List of parameterized dialogue actions
Actions are passed in string format and decoded/parsed everywhere.
Very annoying.

From `utils/DiaAct:50`:
```
known_format = {'hello':0,
                       'bye':0,
                       'inform':2,
                       'request':1,
                       'confreq':1,
                       'select':3,
                       'affirm':2,
                       'negate':2,
                       'deny':3,
                       'repeat':0,
                       'confirm':2,
                       'reqalts':2,
                       'null':0,
                       'badact':0,
                       'thankyou':0}
```
Action names are instantiated in ``policy/SummaryAction:88``
These can be converted to 'master actions' by ``SummaryAction.Convert`` at line 109:
* master action: 
* summary action: 

## Intuition behind system dialogue actions 
* `hello()`: opening/greeting.
  `Hello, welcome to the adaptive loan advisor. How may I help you?`
* `bye()`: closing greeting.
   `Thanks you and goodbye.`
* `inform(name, x,.., z)`: Recommend `name` and mention features `x,..,z`.
  `An overdraft would be suitable, it has a variable interest rate and can be used for any purpose`.
*  `request(x, [y,..,z])`: Request desired value for feature `x`, optionally offering options
   `[y,..,z]`.
   `What is the purpose of the loan? Is it a car, boat or refinancing purpose?`
* `confreq(count, interest_rate=variable)`: 'Implicit confirmation' by listing the number of items still accessible.
  `There are 3 loans with a variable interest rate.`
* `select(A=V1,A=V2)`: Ask for explicit differention between `V1` and `V2`.
  `Would you like a loan with a boat or car purpose?`
* `affirm(A=V1,B=V2)`: Confirmative reaction to question, additionally provide information on `A`
  and `B`
  `Yes, and the purpose is boat and the interest rate is fixed.`
* `negate(A=V1,B2=V2)`: Negative reaction to question, additionally provide information on `A` and
  `B`
  `No, and the purpose is boat and the interest rate is fixed.`
* `deny(A=V1,..,C=Vz)`: Deny that `A` has value `V1` etc.
  `The purpose is not boat and the interest rate is not fixed`
* `repeat()`: Ask user to repeat last utterance.
  `Could you repeat that please?`
* `confirm(A=V1,..,C=Vz)`: Check with user whether feature `A` should have property `V1` etc.
  `Let me check, the purpose is boat, right?`
* `null()`: erroneous actions, should never be selected.
* `badact()`: erroneous actions, should never be selected.
* `thankyou()`: seems to be never selected by system?
* `reqmore()`: seems to be never selected by system?

# Topic tracker
How are available topics found?
The keyword topic tracker uses hardcoded keywords in ``topictracker/RuleTopicTrackers:113``

To disable the topic tracker, pass `singledomain = True` as a parameter under `[GENERAL]`.

# Ontology
All ontologies should have a `name' column, this is hardcoded.

## Create new ontology
1. Create a .csv with at least a `name` column.
Make sure that there are no column headers.
2. Open sqlite3 in `pydial/ontology/ontologies` give the filename you want to use.
```
$ sqlite3 MyDomain.db
```
3. Create a new database with the right column headers, using *lowercase only*.
```
sqlite> create table MyDomain(name,header2,eader3);
```
NOTE: avoid spaces in the header names
4. Enable csv mode and import the file. Use the fully quantified filename and include target table:
```
sqlite> .mode csv
sqlite> .import /path/to/file.csv MyDomain
```
5. Follow further instructions in PyDial documentation: ``How to add a new domain".
   * Open up the ontologytool:
     ```
     python scripts/ontologyTool.py -n -d MyDomain --db ./path/to/ontology.db
     ```
6. Use the ``templatestub`` command to generate a templatestub for this domain (to be
   filled out).
7. Calculate the domain size using the script in ``ontology/ontologies/ontology_size.py`` and add to the deeplearning-style policies' ``get_n_in``:
  * A2CPolicy
  * ACERPolicy
  * DQNPolicy
  * ENACPolicy

# New domain
When adding a new domain, make sure to add the ontology, create and populate the SemO template
file and create a SemI (RexexSemI_<NEWDOMAIN>).

# Learning policies
Policies that learn have to be instantiated using an in_policyfile
* TODO: check if can be empty
These consist of two `pickle` files:
* `.prm` a parameters file containing....
* `.dct` a dictionary file containing the object and state-actions?
GPSarsa seems to learn incrementally, whereas e.g. A2CPolicy learn on a history.
* Could we rephrase entropy-based learning to an incremental setting?
* If not, how does this impact the learning setup?

## Beliefstate -- flatten
In flattening the belief state, the following are included:
* Belief values for all distinct values for all informables (#v)
* Belief values for ``**NONE**`` and ``dontcare`` for all informables (2*#i)
* Belief values for supported method (`byconstraint`, `byalternatives` etc.): 6
* Belief values for all ``discourseActs`` (to denote the last action): 6
* Belief values to represent whether constraints have been asked for all requestables (#req)
* Belief value describing how many entities are matched by how many slots (1-5) and whether there
  are items left to discriminate on (5 * 5)
* Belief value to denote the last action informed about no matches: lastInformNone (1)
* Belief value to denote that an offered happened: offerHappened (1)
