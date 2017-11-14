#ifndef PYGMX_SYSTEM_H
#define PYGMX_SYSTEM_H

#include <memory>
#include <string>

#include "core.h"
//#include "pyrunner.h"

#include "gmxapi/gmxapi.h"
#include "gmxapi/system.h"

namespace gmxpy
{

class PyMD;
class PySingleNodeRunner;

class PySystem
{
public:
    static std::shared_ptr<PySystem> from_tpr(const std::string& filename);

    PySingleNodeRunner get_runner();

    PyMD get_md();

    //void set_runner(std::shared_ptr<PySingleNodeRunner> runner);

private:
    std::shared_ptr<gmxapi::System> system_;
};

} // end namespace gmxpy

#endif // header guard

