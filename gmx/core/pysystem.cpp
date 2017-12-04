#include "pysystem.h"

#include <memory>

namespace gmxpy
{

std::shared_ptr<gmxapi::System> from_tpr(std::string filename)
{
    auto system = gmxapi::fromTprFile(filename);
    return std::move(system);
}

} // end namespace gmxpy
