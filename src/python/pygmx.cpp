#include "pygmx.h"

namespace pygmx
{

int version()
{
    return int(gmx_version);
}

} // end pygmx
