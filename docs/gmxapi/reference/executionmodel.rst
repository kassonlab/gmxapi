===============
Execution model
===============

Basic graph model
=================

The gmxapi idiom is that an API session consists of creating a work graph and
then executing it. Or, rather, optionally fetching results and/or causing the
graph to be executed.

Graph nodes are instances of Operations. Graph edges connect Operation outputs
to Operation inputs.

Graphs are directed and acyclic with limited statefulness. Rather than increase
the complexity of the graph model, state and looping are handled with subgraphs
(hierarchical operations), manipulated through additional API functions to
minimize the exposure of graph execution details.

gmxapi Context
==============

The role of a Context is to launch (graphs of) work by providing operation
implementations with resources, data, and API facilities. Data and data futures
have a single owning (local) Context, but a future in one Context may depend on
data from another context. When data becomes available in its owning Context,
the owning Context notifies the data subscribers, which can include other
Contexts in which consuming Futures or Operations exist. The locality of data is
irrelevant to high level Future and Operation interfaces, so the Context
implementations are free to exchange or duplicate data/operation ownership as
optimization details.

gmxapi Operations
=================

High level code and end users should only need to interact with Operation
creation functions and the output data accessors of the returned objects.
The execution context of the work is implicit and automatic, if possible, but
the API is structured to allow for extensible handling of graph execution.

Implementation considerations
-----------------------------

Operation implementations should be decoupled from the the core library or
Context facilities. It is reasonable to require modules to be recompiled to
be compatible with newer library code, but preferably only to gain access to
new features or interfaces. It is generally unreasonable to require module
source code to be updated to retain compatibility or implement new required
interfaces.

This means that operation modules have a minimally complex entry point, built
with the help of a library header, that allows the operation to make itself
available to an API context. The client passes a Context implementation object
to the module entry point so that the module implementation can register itself.
In general, this functionality can be implemented as part of the factory that
the client passes operation parameters to when acquiring a reference to an
operation instance / work node. The Context passed is the Context in which the
handle and output futures are to be local. It may not be the same Context in
which the inputs are owned, or even in which the new operation will be executed.

Such a factory is responsible for dispatching operation builder clients (directors)
in the correct Context or sub-Context (which may need to be created).
The dispatcher

The result of negotiation between the Operation and the Output Context

In Python, we have several ways to

Basic protocol overview
-----------------------

1. Client code calls a function to get an object representing a node
   (or part of a node) in a graph of work.
2. The instance can self-describe its available outputs and interfaces,
   which the client may inspect or use as input for other new operation instances.
3. Execution is not guaranteed to occur and data is not guaranteed to be
   available in local resources until the client forces data to cross the API barrier,
   either through explicit access to a Future result or through other explicit action.

Execution and resource management are encapsulated in Context details.
References to facets of the instance implement standard protocols to self-describe
to a Context how to obtain objects or data related to the Operation,
and how to prepare or checkpoint resources used by the Operation.

High level client protocol
--------------------------

General client protocol
-----------------------

Registration protocol
---------------------

Launch protocol
---------------

Operation instantiation
-----------------------

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

Examples
========

Python
------

C++ simulation extension
------------------------

GROMACS library operation
-------------------------
