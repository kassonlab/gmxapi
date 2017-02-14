#ifndef GMX_PYGMX_H
#define GMX_PYGMX_H

#include <string>
#include "pybind11/pybind11.h"
#include "gromacs/version.h"

namespace py = pybind11;

namespace pygmx
{

const auto gmx_version{GMX_VERSION};

int version();

} // end pygmx

#endif // GMX_PYGMX_H
