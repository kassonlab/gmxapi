/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2017, by the GROMACS development team, led by
 * Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
 * and including many others, as listed in the AUTHORS file in the
 * top-level source directory and at http://www.gromacs.org.
 *
 * GROMACS is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2.1
 * of the License, or (at your option) any later version.
 *
 * GROMACS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with GROMACS; if not, see
 * http://www.gnu.org/licenses, or write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 * If you want to redistribute modifications to GROMACS, please
 * consider that scientific software is very special. Version
 * control is crucial - bugs must be traceable. We will be happy to
 * consider code for inclusion in the official distribution, but
 * derived work must not be called official GROMACS. Details are found
 * in the README & COPYING files - if they are missing, get the
 * official version at http://www.gromacs.org.
 *
 * To help us fund GROMACS development, we humbly ask that you cite
 * the research papers on the package. Check out http://www.gromacs.org.
 */
/*! \internal \file
 * \brief Exports Python bindings for gmx.core module.
 *
 * \ingroup module_python
 */

#include <memory>
#include "core.h"

#include "gmxpy_api.h"

#include "gmxapi/status.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace gmxpy;

// Export Python module.

/// Set module.__name__
const char* const name = "core";

/// used to set __doc__
/// pybind11 uses const char* objects for docstrings. C++ raw literals can be used.
const char* const docstring = R"delimeter(
Gromacs core module
===================

gmx.core provides Python access to the Gromacs C++ API so that client code can be
implemented in Python, C++, or a mixture. The classes provided are mirrored on the
C++ side in the gmxapi namespace.

This documentation is generated from docstrings exported by C++ extension code.

)delimeter";

/*! \brief Export gmx.core Python module in shared object file.
 *
 * One goal of these bindings is to declare a buffer type suitable for numpy Nx3 array output.
 * If we want to pass access but not ownership to Python, we need to make
 * sure we can allow a C++ shared pointer ref count to be increased.
 * The buffer protocol requires that the exporter (this code) keeps the
 * memory valid for the exported view until all consumers are done and
 * the PyBuffer_Release(buffer *view) is issued. I'm not sure, but I assume
 * pybind11 manages that for us by holding a shared_ptr to this. However, there
 * seem to be subtleties I overlooked in some testing, so this warrants
 * further investigation.
 *
 * To be safe (and in general) we can use the keep_alive<>() call policy
 * and return_value_policy annotations.
 * The keep_alive<Nurse, Patient>() call policy keeps Patient alive as long
 * as Nurse is alive. Indices for Nurse or Patient are 0 for the return value
 * of the annotated function
 * and higher numbers for arguments. For member functions, index 1 is used
 * for the this* object.
 *
 * The pybind11 documentation notes "For functions returning smart pointers, it is not necessary to specify a return value policy."
 * and
 * "It is even possible to completely avoid copy operations with Python expressions like np.array(matrix_instance, copy = False)"
 * \ingroup module_python
 */

// Instantiate the module
PYBIND11_MODULE(core, m) {

    using namespace gmxpy::detail;

    m.doc() = docstring;

    export_gmxapi(m);

    // Export core bindings
    py::class_< ::gmxapi::Status > gmx_status(m, "Status", "Holds status for API operations.");


    // Get bindings exported by the various components.
    export_md(m);
    export_system(m);
}
