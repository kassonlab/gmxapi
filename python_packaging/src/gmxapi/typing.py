#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2019,2021, by the GROMACS development team, led by
# Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
# and including many others, as listed in the AUTHORS file in the
# top-level source directory and at http://www.gromacs.org.
#
# GROMACS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# GROMACS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GROMACS; if not, see
# http://www.gnu.org/licenses, or write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
#
# If you want to redistribute modifications to GROMACS, please
# consider that scientific software is very special. Version
# control is crucial - bugs must be traceable. We will be happy to
# consider code for inclusion in the official distribution, but
# derived work must not be called official GROMACS. Details are found
# in the README & COPYING files - if they are missing, get the
# official version at http://www.gromacs.org.
#
# To help us fund GROMACS development, we humbly ask that you cite
# the research papers on the package. Check out http://www.gromacs.org.

"""Extra support for type hinting and generics.

Provides additional support for annotation and static type checking.
Extends the specifications of the abstract base classes in gmxapi.abc.
"""
from abc import abstractmethod
from typing import Optional, TypeVar, Generic, NewType, Type

import gmxapi.abc
# from gmxapi.abc import Context as AbstractContext

# Use SourceTypeVar and ResultTypeVar for static type hints, annotations, and as a parameter to generics.
# Use valid_source_types and valid_result_types for run-time type checking.
ResultTypeVar = TypeVar('ResultTypeVar', *(str, bool, int, float, dict, gmxapi.abc.NDArray))
valid_result_types = ResultTypeVar.__constraints__

# TODO: What about None?
SourceTypeVar = TypeVar('SourceTypeVar',
                        *(str, bool, int, float, dict, gmxapi.abc.NDArray))
valid_source_types = SourceTypeVar.__constraints__

# Place holder for type annotations of Context objects.
# TODO: Expand to support some static type checking.
_Context = TypeVar('_Context', bound=gmxapi.abc.Context)
# Type variable that binds to subclasses of the forward referenced OperationImplentation ABC.
_Op = TypeVar('_Op', bound=gmxapi.abc.OperationImplementation)

# Note: We could make many types generic in SourceContext and TargetContext and
# compose functionality into instances of a helpful base class with the option of
# subclassing the generic base with concrete types. If we want to reserve the word
# "Context" for an execution context, then we can say that a SourceResource or
# TargetEnvironment can each be either a Context or an OperationExecutionDirector.
#
# We can't
# generally add type-hinting details in terms of a specialized generic, but we
# can require a particular version of a generic and we can use the inferred
# type parameter value in limited cases, including to fully specify other generics.
# For instance, we can't assert that a generic with a particular parameter has
# additional attributes, but we can overload a function that produces an object
# with those attributes. More generally, using some sort of identity function like
# that may be the solution to the type erasure of a generic abstract base class.
# For static type checking of dynamically defined subclasses, we can use a decorator
# to reduce boiler plate if the type checker does a decent job of resolving closures.
# Ironically, there may be cases where we want to *avoid* annotating the return
# value to allow the static source analyzer to infer the dynamically typed return value.


class Future(Generic[ResultTypeVar]):
    """Generic result data."""
    def dtype(self) -> Type[ResultTypeVar]:
        ...

    def result(self) -> ResultTypeVar:
        ...


class OperationReference(gmxapi.abc.OperationReference, Generic[_Op]):
    """Object with an OperationReference interface.

    Generic version of AbstractOperationReference, parameterized by operation
    implementation.

    Now that Python 3.7 is required, it will be straightforward to merge the gmxapi.typing and
    gmxapi.abc modules, which should be a welcome simplification.
    """

    @abstractmethod
    def run(self):
        """Assert execution of an operation.

        After calling run(), the operation results are guaranteed to be available
        in the local context.
        """

    @property
    @abstractmethod
    def output(self):
        """Get a proxy collection to the output of the operation.

        Developer note: The 'output' property exists to isolate the namespace of
        output data from other operation handle attributes and we should consider
        whether it is actually necessary or helpful. To facilitate its possible
        future removal, do not enrich its interface beyond that of a collection
        of OutputDescriptor attributes. The OutputDataProxy also serves as a Mapping,
        with keys matching the attributes. We may choose to keep only this aspect
        of the interface instead of trying to keep track of the set of attributes.
        """
        ...


# TODO: With Python 3.8+, use typing.Protocol.
class OperationDirector(Generic[_Op]):
    """Generic abstract operation director.

    An operation director is instantiated for a specific operation and context
    by a dispatching factory to add a computational element to the work managed
    by the context.
    """
    def __call__(self, resources, label: Optional[str]) -> OperationReference[_Op]:
        """Add an element of work (node) and return a handle to the client.

        Implements the client behavior in terms of the NodeBuilder interface
        for a NodeBuilder in the target Context. Return a handle to the resulting
        operation instance (node) that may be specialized to provide additional
        interface particular to the operation.
        """
        ...


class OperationImplementation(Generic[_Op], gmxapi.abc.OperationImplementation):
    """Essential interface of an Operation implementation.

    Describe the essential features of an Operation that can be registered with
    gmxapi to support building and executing work graphs in gmxapi compatible
    execution contexts.
    """
    # The executable part of an operation consumes a distinct resource type.
    # The resource type may be opaque, because it is created through a factory
    # and only used in passing to a function object.
    ResourceType = NewType('ResourceType', object)

    def name(self) -> str:
        """The name of the operation.

        Generally, this corresponds to a callable attribute of a Python module
        (named by namespace()) that acts as a factory for new operation instances.
        It is also used by Context implementations to locate code supporting
        the operation.
        """
        ...

    def namespace(self) -> str:
        """The namespace of the operation.

        Generally, the namespace corresponds to a Python module importable in
        the execution environment.
        """

    # Note that this indicates that the ABC requires subclasses to provide a generic function,
    # which _is_ the factory behavior we are trying to specify.
    # TODO: Confirm that this type-checks correctly.
    # We may need to look more at how the type checking is implemented to see how
    # to do this right.
    def director(self, context) -> OperationDirector[_Op]:
        """Factory to get an OperationDirector appropriate for the context."""
        ...
