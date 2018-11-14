/*! \file
 * \brief Implement System helper code.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include "pysystem.h"

#include <memory>

namespace gmxpy
{

std::shared_ptr<gmxapi::System> from_tpr(std::string filename)
{
    auto system = gmxapi::fromTprFile(filename);
    return std::make_shared<gmxapi::System>(std::move(system));
}

} // end namespace gmxpy
