/*! \file
 * \brief Provide Python bindings and helper functions for setting up restraint
 * potentials.
 *
 * There is currently a lot of boilerplate here that will be generalized and
 * removed in a future version. In the mean time, follow the example for
 * EnsembleRestraint to create the proper helper functions and instantiate the
 * necessary templates.
 *
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include "export_plugin.h"

#include <cassert>

#include <memory>

#include "gmxapi/exceptions.h"
#include "gmxapi/gmxapi.h"
#include "gmxapi/md.h"
#include "gmxapi/md/mdmodule.h"

#include "ensemblepotential.h"

// Make a convenient alias to save some typing...
namespace py = pybind11;

// TODO: Improve readability by instantiating some template specializations as
//  type aliases.
using plugin::EnsemblePotential;
using plugin::makeEnsembleParams;
using plugin::Matrix;
using plugin::PyRestraint;
using plugin::Restraint;
using plugin::RestraintBuilder;
using plugin::RestraintModule;

using EnsembleRestraintBuilder = RestraintBuilder<EnsemblePotential>;

/*!
 * \brief Factory function for use by the Session launcher.
 *
 * Creates an object that can participate in the building of a work node.
 *
 * \param element WorkElement provided through Context
 * \return ownership of new builder object for the protocol in gmxapi.simulation.Context
 */
std::unique_ptr<EnsembleRestraintBuilder> createEnsembleBuilder(const py::object &element)
{
    using std::make_unique;
    using data_t = EnsemblePotential::input_param_type;
    auto builder = make_unique<EnsembleRestraintBuilder>(element);
    (*builder)
            .add_input("nbins", &data_t::nBins)
            .add_input("binWidth", &data_t::binWidth)
            .add_input("min_dist", &data_t::minDist)
            .add_input("max_dist", &data_t::maxDist)
            .add_input("experimental", &data_t::experimental)
            .add_input("nsamples", &data_t::nSamples)
            .add_input("sample_period", &data_t::samplePeriod)
            .add_input("nwindows", &data_t::nWindows)
            .add_input("k", &data_t::sigma)
            .add_input("sigma", &data_t::sigma);
    return builder;
}

////////////////////////////////////////////////////////////////////////////////
// New potentials modeled after EnsembleRestraint should define a Builder class
// and define a factory function here, following the previous two examples. The
// factory function should be exposed to Python following the examples near the
// end of the PYBIND11_MODULE block.
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// The PYBIND11_MODULE block uses the pybind11 framework (ref
// https://github.com/pybind/pybind11 ) to generate Python bindings to the C++
// code elsewhere in this repository. A copy of the pybind11 source code is
// included with this repository. Use syntax from the examples below when
// exposing a new potential, along with its builder and parameters structure. In
// future releases, there will be less code to include elsewhere, but more
// syntax in the block below to define and export the interface to a plugin.
// pybind11 is not required to write a GROMACS extension module or for
// compatibility with the ``gmx`` module provided with gmxapi. It is sufficient
// to implement the various protocols, C API and Python function names, but we
// do not provide example code for other Python bindings frameworks.
////////////////////////////////////////////////////////////////////////////////

// The first argument is the name of the module when importing to Python. This
// should be the same as the name specified as the OUTPUT_NAME for the shared
// object library in the CMakeLists.txt file. The second argument, 'm', can be
// anything but it might as well be short since we use it to refer to aspects of
// the module we are defining.
PYBIND11_MODULE(myplugin, m)
{
    m.doc() = "sample plugin"; // This will be the text of the module's docstring.

    // Matrix utility class (temporary). Borrowed from
    // http://pybind11.readthedocs.io/en/master/advanced/pycpp/numpy.html#arrays
    py::class_<Matrix<double>, std::shared_ptr<Matrix<double>>>(
            m, "Matrix", py::buffer_protocol())
            .def_buffer([](Matrix<double> &matrix) -> py::buffer_info {
                return py::buffer_info(
                        matrix.data(),  /* Pointer to buffer */
                        sizeof(double), /* Size of one scalar */
                        py::format_descriptor<double>::format(), /* Python struct-style
                                                                    format descriptor */
                        2, /* Number of dimensions */
                        { matrix.rows(), matrix.cols() }, /* Buffer dimensions */
                        { sizeof(double) * matrix.cols(), /* Strides (in bytes) for each index */
                          sizeof(double) });
            });

    //////////////////////////////////////////////////////////////////////////
    // Begin EnsembleRestraint
    //
    // Define Builder to be returned from ensemble_restraint Python function
    // defined further down.
    pybind11::class_<EnsembleRestraintBuilder> ensembleBuilder(
            m, "EnsembleBuilder");
    ensembleBuilder.def("add_subscriber", &EnsembleRestraintBuilder::addSubscriber);
    ensembleBuilder.def("build", &EnsembleRestraintBuilder::build);

    // Define a more concise name for the template instantiation...
    using PyEnsemble = PyRestraint<RestraintModule<Restraint<EnsemblePotential>>>;

    // Export a Python class for our parameters struct
    py::class_<Restraint<EnsemblePotential>::input_param_type> ensembleParams(
            m, "EnsembleRestraintParams");
    m.def("make_ensemble_params", &makeEnsembleParams);

    // API object to build.
    py::class_<PyEnsemble, std::shared_ptr<PyEnsemble>> ensemble(
            m, "EnsembleRestraint");
    // EnsembleRestraint can only be created via builder for now.
    ensemble.def("bind", &PyEnsemble::bind, "Implement binding protocol");
    /*
     * To implement gmxapi_workspec_1_0, the module needs a function that a
     * Context can import that produces a builder that translates workspec
     * elements for session launching. The object returned by our function needs
     * to have an add_subscriber(other_builder) method and a build(graph)
     * method. The build() method returns None or a launcher. A launcher has a
     * signature like launch(rank) and returns None or a runner.
     */

    // Generate the name operation that will be used to specify elements of Work
    // in gmxapi workflows. WorkElements will then have namespace: "myplugin"
    // and operation: "ensemble_restraint"
    m.def("ensemble_restraint",
          [](const py::object element) { return createEnsembleBuilder(element); });
    //
    // End EnsembleRestraint
    ///////////////////////////////////////////////////////////////////////////
}
