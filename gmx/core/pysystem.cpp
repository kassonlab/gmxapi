#include "pysystem.h"

#include <memory>

#include "pymd.h"

#include "gmxapi/system.h"

namespace gmxpy
{

std::shared_ptr<PySystem> PySystem::from_tpr(const std::string& filename)
{
    auto system = std::make_shared<PySystem>();
    system->system_ = gmxapi::fromTprFile(filename);
    return system;
}

std::shared_ptr<gmxapi::System> from_tpr(std::string filename)
{
    auto system = gmxapi::fromTprFile(filename);
    return std::move(system);
}

} // end namespace gmxpy
