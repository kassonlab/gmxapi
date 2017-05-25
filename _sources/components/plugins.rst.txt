====================
Simulation internals
====================

The applied_forces facility implemented for the electric field module has become
the starting point for discussions on API requirements to allow less tightly
coupled extension of the simulation loop. In order to allow encapsulation of
performance-critical internals and a stable interface to external developers
without compromising the flexibility of the core developers, we need to negotiate
the facilities and access available to low-level simulation extensions.

Additionally, rapid prototyping and and alternative workflows present use cases
for providing access to internal data structures at a higher level before,
during, or after a simulation run. Again, for each use case, we need to conside
an interface that prevents misuse, provides the minimal access, and hides the
implementation sufficiently that external or higher-level code cannot invalidate
assumptions made for optimizations in the core code.

Simulation loop
===============

In general, it should be possible to implement plugins for such things a new
potentials very similarly to built-ins with access to the same optimized
routines, though the interfaces to some can’t possibly be as stable as
higher-level code, so we might consider feature versioning for the plugin API
instead of just an overall API level.

Simulation plugins, call-backs, and API-facilitated introspection or manipulation
require some additional facilities and revised data structures in the core library.

* Hooks in the simulation loop for commonly extended behaviors to allow non-invasive extensibility through plugins
* Publicly derivable interface classes for extension code not (yet) included with Gromacs
* run-time binding of plugins via API calls when Gromacs is used as a library
* granular access to internal machinery for call-backs, rapid prototyping, etc.

Communicator
============
If we want to be able to optimize non-local communication, access to the communicator
should be mediated.

* the ability to register an interest in particular data being available locally at the next (or other specified) iteration
* Some amount of extensibility in adding data to the next outward communication
* Iterators for requested input/output data to allow Gromacs to optimize its availability and access control

Step Scheduling
===============
Various code has a need to manage what steps it is run on and deal with constraints associated with checkpointing and logging phase.

Notifications
=============

Some sort of publisher-subscriber or observer pattern is necessary to allow
MD components to be introduced with minimal coupling.

In addition to standard justifications for encapsulation,
methods to invalidate state should only be called by the object that
owns the relevant data, since whether or not a certain action invalidates
state may depend on implementation. E.g. changing the size of the simulation
box doesn't invalidate domain decomposition if there is only one domain,
while rescaling particle positions invalidates Verlet/neighbor lists for
truncated non-bonded potentials, but not necessarily all force compute
kernels.

In the absence of the Boost signals code, I have seen the
[nano-signal-slot](https://github.com/NoAvailableAlias/nano-signal-slot) package used effectively
to provide signals and slots for handling things like, *e.g.*
`BoxChanged`, `ParticleNumChanged`...
Initial implementation will require only a few signals to connect core modules
(for *e.g.* triggering domain decomposition or pair list rebuilds)
but additional signals and handlers will be added as needed,
and the facility will be very useful for
developers of extension code, such as alchemical techniques (`ParticleTypesChanged`,
`ChargesUpdated`, `NonIntegratorParticleTranslation`, `NBRangeChanged`) and
encapsulated workflows (`TSetChanged`, `NDegreesFreedomChanged`).


Integrator
==========

Some considerations follow.

Objects / Data owned by the integrator are limited to data
generated and used specifically because of the integration
method or algorithm and used to update the configuration
from one simulation step to the next.

* thermostat/barostat internal state
* constraints?
* virial?

Objects used by the Integrator

* simulation box definition
* PRNG
* force / potential evaluators
* particle and topology data
* logger
* messenger
* communicator(s)
* load balancer(s)
* user-provided parameters
* neighbor list
* particle selection / grouping structures
* checkpointing facilities

The integrator, and objects and functors used by the Integrator, should be created
at a higher scope than the simulation loop so that they can
provide facilities to other code before and after simulation
as well as during simulation to objects bound before the loop
begins. Public facilities can include facilities provided to the
integrator and/or functionality and data of interest to users
or other objects.

* applied forces, last calculated values
* contribution to energy and virial
* current parameter values
* state introspection
* parallel / distributed access methods as well as gather operations
* useful "signals" or publish/subscribe hooks for data owned

Some basic abstract interfaces will be obvious, while more
esoteric code should be free to provide extended interfaces.

Less public functionality may still be exposed, possibly through
additional wrappers or a sequence of calls to account for inner loop
optimizations. E.g. ``update()`` or ``calculate()`` methods called by
the simulation runner every step, or methods to invalidate some
aspect of simulation state to force recalculation or reinitialization
of something.
