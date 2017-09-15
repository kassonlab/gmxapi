#include "pysystem.h"

#include <memory>

#include "gmxapi/system.h"

namespace gmxpy
{

PySingleNodeRunner PySystem::get_runner()
{
    PySingleNodeRunner runner{system_->runner()};
    return std::move(runner);
}

std::shared_ptr<PySystem> PySystem::from_tpr(const std::string& filename)
{
    auto system = std::make_shared<PySystem>();
    system->system_ = gmxapi::fromTprFile(filename);
    return system;
}

} // end namespace gmxpy