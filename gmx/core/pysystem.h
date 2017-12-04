#ifndef PYGMX_SYSTEM_H
#define PYGMX_SYSTEM_H

#include <memory>
#include <string>

#include "core.h"

#include "gmxapi/gmxapi.h"
#include "gmxapi/system.h"

namespace gmxpy
{

class PySystem
{
public:
    static std::shared_ptr<PySystem> from_tpr(const std::string& filename);

private:
    std::shared_ptr<gmxapi::System> system_;
};

std::shared_ptr<gmxapi::System> from_tpr(std::string filename);

} // end namespace gmxpy

#endif // header guard

