/*! \defgroup module_python Python module for accessing Gromacs library
 * The Python module ``gmx`` consists of a high-level interface implemented in
 * pure Python and a low-level interface implemented as a C++ extension in the
 * submodule, gmx.core.
 */
/*! \file
 * \brief Declares symbols to be exported to gmx.core Python module.
 *
 * Declares namespace gmxpy.
 * \ingroup module_python
 */
#ifndef GMXPY_CORE_H
#define GMXPY_CORE_H

#include "pybind11/pybind11.h"


/*! \brief API client code from which to export Python bindings
 *
 * gmxpy is not a public interface. It implements bindings for the public
 * Python API in the C++ Python extension it produces, and it uses the public
 * C++ Gromacs API, but is itself an API *client* and its C++ interfaces are not
 * intended to be used in external code.
 * \ingroup module_python
 */
namespace gmxpy
{

namespace detail
{

void export_md(pybind11::module &m);

void export_context(pybind11::module &m);

void export_system(pybind11::module &m);

void export_tprfile(pybind11::module &m);

} // end namespace gmxpy::detail

}      // end namespace gmxpy

#endif // PYGMX_CORE_H
