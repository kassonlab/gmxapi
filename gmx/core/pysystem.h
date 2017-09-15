#ifndef PYGMX_SYSTEM_H
#define PYGMX_SYSTEM_H

#include <memory>
#include <string>

#include "core.h"
#include "pyrunner.h"

namespace gmxpy
{

class PySystem
{
public:
    static std::shared_ptr<PySystem> from_tpr(const std::string& filename);

    PySingleNodeRunner get_runner();

    //void set_runner(std::shared_ptr<PySingleNodeRunner> runner);

private:
    std::shared_ptr<gmxapi::System> system_;
};

} // end namespace gmxpy

#endif // header guard

