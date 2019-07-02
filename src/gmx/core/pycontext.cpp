/*! \file
 * \brief Wrapper code for gmxapi::Context.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */
#include "pycontext.h"

#include <cassert>

#include "gmxapi/gmxapi.h"
#include "gmxapi/md.h"


namespace py = pybind11;

namespace gmxpy
{

void PyContext::setMDArgs(const MDArgs &mdArgs) {
    assert(context_);
    context_->setMDArgs(mdArgs.value);
}

std::shared_ptr<gmxapi::Session> PyContext::launch(const gmxapi::Workflow &work) {
    assert(context_);
    return context_->launch(work);
}

std::shared_ptr<gmxapi::MDWorkSpec> PyContext::getSpec() const {
    assert(workNodes_);
    return workNodes_;
}

std::shared_ptr<gmxapi::Context> PyContext::get() const {
    assert(context_);
    return context_;
}

PyContext::PyContext() :
    context_{std::make_shared<gmxapi::Context>()},
    workNodes_{std::make_shared<gmxapi::MDWorkSpec>()}
{
    assert(context_);
    assert(workNodes_);
}

void PyContext::addMDModule(pybind11::object force_object) {
    // If force_object has a bind method, give it a PyCapsule with a pointer
    // to our C++ object.
    if (py::hasattr(force_object, "bind"))
    {
        auto spec = getSpec();
        auto holder = new gmxapi::MDHolder(spec);
        holder->name_ = "pygmx holder";
        auto deleter = [](PyObject *o) {
            if (PyCapsule_IsValid(o, gmxapi::MDHolder_Name))
            {
                auto holder_ptr = (gmxapi::MDHolder *) PyCapsule_GetPointer(o, gmxapi::MDHolder_Name);
                delete holder_ptr;
                // \todo double-check whether there is something we should do to invalidate a PyCapsule.
            };
        };
        auto capsule = py::capsule(holder,
                                   gmxapi::MDHolder_Name,
                                   deleter);
        py::object bind = force_object.attr("bind");
        // py::capsule does not have bindings and does not implicitly convert to py::object
        py::object obj = capsule;
        bind(obj);
    }
    else
    {
        // Note: Exception behavior is likely to change.
        // Ref: https://github.com/kassonlab/gmxapi/issues/125
        throw py::value_error("Argument must provide a `bind` method.");
    }
}

} // end namespace gmxpy
