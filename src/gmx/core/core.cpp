/*! \internal \file
 * \brief Exports Python bindings for gmx.core module.
 *
 * \ingroup module_python
 */

#include "core.h"

#include <memory>

#include "tprfile.h"
#include "gmxapi/status.h"
#include "gmxapi/version.h"

#include "pybind11/pybind11.h"

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

    // Export core bindings

    m.def("has_feature", &gmxapi::Version::hasFeature, "Check the gmxapi library for a named feature.");

    py::class_< ::gmxapi::Status > gmx_status(m, "Status", "Holds status for API operations.");


    // Get bindings exported by the various components.
    // In the current implementation, sequence may be important. Exports that
    // reference bindings from other exports should not be called before the
    // dependencies are exported.
    export_tprfile(m);
    export_md(m);
    export_context(m);
    export_system(m);

}
