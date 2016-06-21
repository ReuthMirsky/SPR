# SPR
Sequential Plan Recognition

Usage: SPR.py     \<Domain file\>    \<Observations\>     \<Strategy\>    \<Gold Standard\>

\<Domain file\> path to the lisp and-or representation of the domain and a sequence of observations

\<Observations\> is the number of observations after which the querying process should begin

\<Strategy\> is the type for probing strategy used. The options are:
  - probeByRandom
  - probeByMostProbablePlan
  - probeByMostProbableHypothesis
  - probeByEntropy
  - probeByEntropySubtrees (if using this option, should uncomment lines 143-149 in the file ./Source/Algorithm.py)
   
\<Gold Standard\> path to an xml of the correct hypothesis
