===============
Execution model
===============

stub


*explain what happens (serializability, factory functions) when outputs are used as inputs*

..  uml:: diagrams/graphSequence.pu

Output is generated to satisfy data dependencies when a Session is launched from
the ``gmx`` graph-enabled Context.

..  uml:: diagrams/launchSequence.pu

We maximize opportunities for deferred execution and minimal data copies while
minimizing code dependencies and implementation overhead by specifying some
protocols for data proxies, data futures, and data access control.

..  uml:: diagrams/outputAccessSequence.pu

Operations
==========

*illustrate the implications for what happens in the mdrun CLI program or libgromacs MD session.*

..  uml:: diagrams/operationFactory.pu

