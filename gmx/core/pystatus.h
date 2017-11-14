//
// Created by Eric Irrgang on 11/14/17.
//

#ifndef GMXPY_PYSTATUS_H
#define GMXPY_PYSTATUS_H

#include "gmxapi/status.h"

namespace gmxpy
{


/*! \brief Generic return value for API calls.
 *
 * \internal
 * \ingroup module_python
 */
class PyStatus
{
    public:
        PyStatus() : success_(false)
        {};

        PyStatus(const PyStatus &status) : success_{status.success_}
        {};

        virtual ~PyStatus() = default;

        explicit PyStatus(const bool &status) : success_(status)
        {};

        explicit PyStatus(const gmxapi::Status& status) : success_(status.success())
        {};

        bool success() const
        { return success_; };

    private:
        bool success_{false};
};

} // end namespace gmxpy

#endif //GMXPY_PYSTATUS_H
