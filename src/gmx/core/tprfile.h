/*! \file
 * \brief Declare TPR file helpers.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#ifndef GMXPY_TPRFILE_H
#define GMXPY_TPRFILE_H

#include <string>

namespace gmxpy
{

/*!
 * \brief Copy and possibly update TPR file by name.
 *
 * \param infile Input file name
 * \param outfile Output file name
 * \param end_time Replace `nsteps` in infile with `end_time/dt`
 * \return true if successful, else false
 */
bool copy_tprfile(std::string infile, std::string outfile, double end_time);

} // end namespace gmxpy

#endif //GMXPY_TPRFILE_H
