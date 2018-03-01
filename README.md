#About
This repository contains the modified version of FastDownward translator described in the 
paper "Automatic Extraction of Axioms in Planning".

#Dependencies

##Gurobi Optimization 6.5.0

Get Gurobi Optimization 6.5.0 from Grubi Optimization.
Configure the environmental variables as below.
You also need to obtain a gurobi license file.

```.bashrc
export GUROBI_HOME="$HOME/gurobi650/linux64"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"
```

##Gurobi Python Module

```
cd $(HOME)/gurobi650/linux64; python setup.py install
```
