import glob, os
import json
import sys
import pprint

argname = sys.argv[1]

all_values = set()

print("looking for attribute ", argname)
for f in glob.glob("*.json"):
    print(f)
    contents = json.load(open(f))
    all_values |= set(contents[argname])

pprint.pprint(all_values)
