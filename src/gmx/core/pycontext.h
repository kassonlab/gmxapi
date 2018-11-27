/*! \file
 * \brief Declarations for Context wrappers.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#ifndef GMXPY_PYCONTEXT_H
#define GMXPY_PYCONTEXT_H

#include "pybind11/pybind11.h"

#include "gmxapi/context.h"
#include "gmxapi/md.h"

namespace gmxpy
{

class MDArgs
{
public:
    std::vector<std::string> value;
};

/*!
 * \brief Wrapper for gmxapi::Context
 *
 * Proxies gmxapi::Context methods and includes additions not yet provided by
 * by upstream library.
 */
class PyContext {
public:
    PyContext();
    void setMDArgs(const MDArgs &mdArgs);
    std::shared_ptr<gmxapi::Session> launch(const gmxapi::Workflow &work);
    std::shared_ptr<gmxapi::Context> get() const;

    void addMDModule(pybind11::object forceProvider);

    /*!
     * \brief Borrow shared ownership of the System's container of associated modules.
     *
     * Used with gmxapi::MDHolder to add MD Modules to the simulation to be run.
     *
     * \return handle to be passed to gmxapi::MDHolder
     *
     */
    std::shared_ptr<gmxapi::MDWorkSpec> getSpec() const;

private:
    std::shared_ptr<gmxapi::Context> context_;
    std::shared_ptr<gmxapi::MDWorkSpec> workNodes_;
};


} // end namespace gmxpy

#endif //GMXPY_PYCONTEXT_H
