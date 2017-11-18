//
// Created by Eric Irrgang on 11/14/17.
//

#ifndef GMXPY_API_H
#define GMXPY_API_H
/*! \internal \file
 * \brief Describe a consistent interface for Python bindings to gmxapi.
 *
 * In order for multiple projects to offer Python bindings that can share access to gmxapi objects,
 * we need to define a minimal set of gmxapi objects and some protocols. Any Python bindings
 * to gmxapi classes should be local to the module, since the fully defined classes are already
 * defined in the gmxapi library. However, any Python module can receive a gmxapi object from
 * another module and use its own local bindings for the C++ object type.
 *
 * To maximize compatibility and minimize reference counting complexity, objects shared in this
 * way should be copyable and simple, such as a struct with a single managed pointer to a more
 * complete gmxapi object.
 *
 * One aim is to allow interoperability between gmxapi clients without a dependency on the gmxpy
 * package, since only the Python-level classes in gmx and gmx.core are intended to be subclassed.
 * The C++ code in gmxpy is not intended as a stable API. This file, too, should probably be
 * decoupled from the gmxpy distribution.
 *
 * This file documents the bindings that another API client should implement locally, describes
 * the protocols to interact between API clients at the C++ level, and provides a reference
 * implementation of the required Python bindings using pybind11. You can either reimplement the
 * bindings however you choose, or if you like pybind11 you can just use this header file.
 *
 * To just use the bindings here, call the export_gmxapi() function in your pybind11 module
 * definition, as described.
 *
 * \ingroup module_python
 */

#include "gmxapi/gmxapi.h"
#include "pybind11/pybind11.h"

#include <string>

// To emphasize that this source code is local to a project, I'm leaving this namespace anonymous.
// Feel free to name it if you want.
namespace
{

namespace py=pybind11;

/*!
 * \brief Call this function when defining a pybind11 C++ extension module.
 *
 * \param mymodule the pybind11 module you are exporting bindings for.
 */
static void export_gmxapi(py::module& mymodule);

class PYBIND11_EXPORT MyHolder : public gmxapi::MDHolder
{
    public:
        using gmxapi::MDHolder::MDHolder;

        explicit MyHolder(const std::string& name) :
            MDHolder(std::make_shared<gmxapi::MDWorkSpec>())
        {
            name_ = name;
        }
};

void export_gmxapi(py::module& mymodule)
{
}

} // end anonymous namespace

#endif //GMXPY_API_H
