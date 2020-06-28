A model file from the MVNHMM learn process must be in the same folder as is used as inputfile. For example, ancillary/params

The output json file is used for HMMGC simulations.

**Usage:**

`python learn_processV2.py -f inputfile -o output.json`

`python learn_processV2.py -d directory -f fileprefix -o output.json`

**Optional arguments:**

`-l locationCount` *(default = 387)*

`-s stateCount` *(default = 4)*

`-g gammas` *(default = 1)*
