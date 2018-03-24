#ifndef PYGMX_SYSTEM_H
#define PYGMX_SYSTEM_H

#include "core.h"

#include <memory>
#include <string>

#include "gmxapi/gmxapi.h"
#include "gmxapi/system.h"

namespace gmxpy
{

std::shared_ptr<gmxapi::System> from_tpr(std::string filename);

} // end namespace gmxpy

#endif // header guard

