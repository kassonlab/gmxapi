#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2019,2020,2021, by the GROMACS development team, led by
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

"""Support data structuring as a Mapping operation.

Allow native data types and gmxapi Futures to be bound to named fields, then delivered as a
Python ``dict`` at run time.

A Mapping operation is dynamically defined within a workflow script for a specific set of fields
(key names) and value types. As a convenience to the user, the `make_mapping` helper function
generates an appropriate Mapping operation through inspection of its (dictionary) argument.

Pending resolution of https://gitlab.com/gromacs/gromacs/-/issues/2993, the Mapping protocol for
data structuring should be reconciled with C++ data exchange scheme or simply be replaced by
Numpy structured data types: https://numpy.org/doc/stable/user/basics.rec.html#structured-datatypes
"""

import collections.abc
import inspect
import typing

from gmxapi import exceptions
from gmxapi.exceptions import ApiError, UsageError
from gmxapi.operation import OperationHandle, _OutputDataProxyType

from .operation import AbstractOperation, InputCollectionDescription, \
    InputPack, OperationDetailsBase, \
    OutputCollectionDescription, \
    ResourceManager, \
    SourceResource, \
    current_context, \
    define_output_data_proxy, \
    define_publishing_data_proxy
from gmxapi.typing import Future as GenericFuture, OperationDirector, OperationReference, _Op


def describe_input(mapping: collections.abc.Mapping) \
        -> typing.Generator[typing.Tuple[str, inspect.Parameter], None, None]:
    """Generate key-value pairs for an InputCollectionDescription."""
    for key, value in mapping.items():
        if hasattr(value, 'dtype'):
            _dtype = value.dtype
        elif hasattr(value, '_dtype'):
            _dtype = value._dtype
        else:
            _dtype = type(value)
        if not isinstance(_dtype, type) and callable(_dtype):
            _dtype = _dtype()
        assert isinstance(_dtype, type)
        param = inspect.Parameter(key, inspect.Parameter.KEYWORD_ONLY,
                                  default=inspect.Parameter.empty, annotation=_dtype)
        yield key, param

_output_description = OutputCollectionDescription(data=dict)
MappingOutputDataProxy = define_output_data_proxy(_output_description)
MappingPublishingDataProxy = define_publishing_data_proxy(_output_description)


class MappingOperationResources(typing.NamedTuple):
    input: dict
    output: MappingPublishingDataProxy


class Mapping(OperationHandle[MappingOutputDataProxy]):
    """Handle type for Mapping instances."""


def make_mapping_operation(mapping: collections.abc.Mapping):
    """Dynamically create an operation to deliver a Mapping.

    Define the Mapping operation as a dynamically defined OperationDetailsBase subclass.

    The output is a single *data* field holding a ``dict``. This is for compatibility and
    simplicity in the near term. An alternative could be separate arrays of keys and values (or
    the tuple style of an ItemsView), but a :py:class:`dataclasses.dataclass` like return type
    should be distinct from this loosely-typed approach.

    If needed use a separate helper to instantiate it and return the Future for its result.
    """

    # Define the InputCollectionDescription.
    # Get the list of (str, inspect.Parameter) tuples.
    input_collection_description = InputCollectionDescription(describe_input(mapping=mapping))

    _identifiers = tuple((name, param.annotation) for name, param in
                        input_collection_description.signature.parameters.items())

    class MappingDetails(OperationDetailsBase):
        # TODO: Check that we actually hash contents and not just identity.
        _basename = 'gmxapi.Mapping' + str(hash(_identifiers))
        __last_uid = 0

        @classmethod
        def name(cls) -> str:
            return cls._basename.split('.')[-1]

        @classmethod
        def namespace(cls) -> str:
            suffix = '.' + cls.name()
            try:
                index = cls._basename.rindex(suffix)
            except ValueError:
                index = None
            return cls._basename[:index]

        @classmethod
        def director(cls, context):
            return MappingDirector(context)

        @classmethod
        def signature(cls) -> InputCollectionDescription:
            """Mapping of named inputs and input type.

            Used to determine valid inputs before an Operation node is created.

            Overrides OperationDetailsBase.signature() to provide an
            implementation for the bound operation.
            """
            raise ApiError('We did not intend to use this code path.')

        def output_description(self) -> OutputCollectionDescription:
            """Mapping of available outputs and types for an existing Operation node.

            Overrides OperationDetailsBase.output_description() to provide an
            implementation for the bound operation.
            """
            return _output_description

        def publishing_data_proxy(self, *,
                                  instance: SourceResource[MappingOutputDataProxy, MappingPublishingDataProxy],
                                  client_id: int
                                  ):
            """Factory for Operation output publishing resources.

            Used internally when the operation is run with resources provided by instance.

            Overrides OperationDetailsBase.publishing_data_proxy() to provide an
            implementation for the bound operation.
            """
            assert isinstance(instance, ResourceManager)
            return MappingPublishingDataProxy(instance=instance, client_id=client_id)

        def output_data_proxy(self, instance: SourceResource[MappingOutputDataProxy, MappingPublishingDataProxy]):
            assert isinstance(instance, ResourceManager)
            return MappingOutputDataProxy(instance=instance)

        def __call__(self, resources: MappingOperationResources):
            """Execute the operation with provided resources.

            Resources are prepared in an execution context with aid of resource_director()

            After the first call, output data has been published and is trivially
            available through the output_data_proxy()

            Overrides OperationDetailsBase.__call__().
            """
            _output = dict()
            for key, value in resources.input.items():
                _output[key] = value
            resources.output.data = _output

        @classmethod
        def make_uid(cls, input):
            """The unique identity of an operation node tags the output with respect to the input.

            Combines information on the Operation details and the input to uniquely
            identify the Operation node.

            Arguments:
                input : A (collection of) data source(s) that can provide Fingerprints.

            Used internally by the Context to manage ownership of data sources, to
            locate resources for nodes in work graphs, and to manage serialization,
            deserialization, and checkpointing of the work graph.

            The UID is a detail of the generic Operation that _should_ be independent
            of the Context details to allow the framework to manage when and where
            an operation is executed.

            Note:
                This implementation creates a new identifier with every call, even if *input*
                is the same, because we have not developed our Fingerprinting scheme in gmxapi 0.1+.

            Design notes on further refinement:
                TODO: Operations should not single-handedly determine their own uniqueness
                (but they should participate in the determination with the Context).

                Context implementations should be allowed to optimize handling of
                equivalent operations in different sessions or work graphs, but we do not
                yet TODO: guarantee that UIDs are globally unique!

                The UID should uniquely indicate an operation node based on that node's input.
                We need input fingerprinting to identify equivalent nodes in a work graph
                or distinguish nodes across work graphs.

            """
            uid = str(cls._basename) + str(cls.__last_uid)
            cls.__last_uid += 1
            return uid

        @classmethod
        def resource_director(cls, *, input: InputPack = None,
                              output: MappingPublishingDataProxy = None):
            """Directs construction of the Session Resources for the function.

            The Session launcher provides the director with all of the resources previously
            requested/negotiated/registered by the Operation. The director uses details of
            the operation to build the resources object required by the operation runner.

            For the Python Context, the protocol is for the Context to call the
            resource_director instance method, passing input and output containers.

            Raises:
                exceptions.TypeError if provided resource type does not match input signature.
            """
            # Check data compatibility
            for name, value in input.kwargs.items():
                if name != 'output':
                    expected = cls.signature()[name]
                    got = type(value)
                    if got != expected:
                        raise exceptions.TypeError(
                            'Expected {} but got {} for {} resource {}.'.format(expected,
                                                                                got,
                                                                                cls._basename,
                                                                                name))

            resources = MappingOperationResources(input=dict(input.kwargs.items()),
                                                  output=output)

            # TODO: Remove this hack when we can better handle Futures of Containers and Future slicing.
            # for name in resources:
            #     if isinstance(resources[name], (list, tuple)):
            #         resources[name] = datamodel.ndarray(resources[name])

            return resources

    class MappingDirector(OperationDirector[MappingDetails]):
        def __init__(self, context):
            self.context = context

        def __call__(self, resources, label: typing.Optional[str]) -> Mapping[MappingDetails]:
            builder = self.context.node_builder(operation=RegisteredOperation, label=label)

            builder.set_resource_factory(SubscriptionSessionResources)
            builder.set_input_description(StandardInputDescription())
            builder.set_handle(StandardOperationHandle)
            # The runner in the gmxapi.operation context is the servicer for the legacy context.
            builder.set_runner_director(SubscriptionPublishingRunner)
            builder.set_output_factory(_output_factory)
            builder.set_resource_manager(ResourceManager)

            # Note: we have not yet done any dispatching based on *resources*. We should
            # translate the resources provided into the form that the Context can subscribe to
            # using the dispatching resource_factory. In the second draft, this operation
            # is dispatched to a SimulationModuleContext, which can be subscribed directly
            # to sources that are either literal filenames or gmxapi.simulation sources,
            # while standard Futures can be resolved in the standard context.
            #
            assert isinstance(resources, _op.DataSourceCollection)
            for name, source in resources.items():
                builder.add_input(name, source)

            handle = builder.build()
            assert isinstance(handle, StandardOperationHandle)
            return handle

    return MappingDetails


def make_mapping(mapping: typing.Union[collections.abc.Mapping, typing.Sequence[
    collections.abc.Mapping]]) -> \
        GenericFuture[dict]:

    if isinstance(mapping, collections.abc.Mapping):
        _prototype = mapping
    elif isinstance(mapping, collections.abc.Sequence) and len(mapping) >= 1:
        # Use the first element to deduce the key names and value types.
        _prototype = mapping[0]
    else:
        _prototype = None
    if not isinstance(_prototype, collections.abc.Mapping):
        raise UsageError('Provide a mapping or sequence of mappings.')

    _MappingOperation = make_mapping_operation(_prototype)

    def helper(mapping, context=None):
        # Description of the Operation input (and output) occurs in the
        # decorator closure. By the time this factory is (dynamically) defined,
        # the OperationDetails and ResourceManager are well defined, but not
        # yet instantiated.
        # Inspection of the offered input occurs when this factory is called,
        # and OperationDetails, ResourceManager, and Operation are instantiated.

        # This operation factory is specialized for the default package Context.
        if context is None:
            context = current_context()
        else:
            raise exceptions.ApiError('Non-default context handling not implemented.')

        handle = _MappingOperation.director(input=mapping, context=context, label=None)

        return handle

    return helper(mapping).output.data
