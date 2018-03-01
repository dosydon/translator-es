# About
This repository contains the modified version of FastDownward translator described in the 
paper "Automatic Extraction of Axioms in Planning".

# Dependencies

## Gurobi Optimization 6.5.0

Get Gurobi Optimization 6.5.0 from Grubi Optimization.
Configure the environmental variables as below.
You also need to obtain a gurobi license file.

```.bashrc
export GUROBI_HOME="$HOME/gurobi650/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
```

## Gurobi Python Module

```
cd $(HOME)/gurobi650/linux64; python setup.py install
```

# How to Use

This program has two additional options.
"group\_choice" lets you choose the strategy used to group fluents to form variables.
Thits program seeks to cover the set of all fluents using the fewest mutex+none groups (subsets
of fluents).
"default" greedily selects the
mutex+none group with the largest cardinality until all fluents are covered.

"exact" solves the set covering problem optimally.

"essential" utilizes exactly1-groups to find inessential fluents.
With "--axiom" option enabled, the program express exactly1-groups as axioms.

```
--group_choice GROUP_CHOICE
	default | exact | essential 
 --axiom               exactly1 group to axioms
```
