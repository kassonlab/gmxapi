/*! \file
 * \brief Helper code for TPR file access.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include "tprfile.h"

#include "gromacs/mdtypes/inputrec.h"
#include "gromacs/topology/topology.h"
#include "gromacs/mdtypes/state.h"
#include "gromacs/fileio/oenv.h"
#include "gromacs/fileio/tpxio.h"
#include "gromacs/fileio/trxio.h"
#include "gromacs/options/timeunitmanager.h"
#include "gromacs/utility/cstringutil.h"
#include "gromacs/utility/programcontext.h"


bool gmxpy::copy_tprfile(std::string infile, std::string outfile, double until_t) {
    bool success = false;

    const char * top_fn = infile.c_str();

    t_inputrec  irInstance;
    t_inputrec *ir = &irInstance;
    gmx_mtop_t        mtop;
    t_state           state;
    read_tpx_state(top_fn, ir, &state, &mtop);


    char              buf[200], buf2[200];



    /* set program name, command line, and default values for output options */
    gmx_output_env_t *oenv;
    gmx::TimeUnit  timeUnit = gmx::TimeUnit_Default;
    bool bView{false}; // argument that says we don't want to view graphs.
    int xvgFormat{0};
    output_env_init(&oenv, gmx::getProgramContext(),
                    static_cast<time_unit_t>(timeUnit + 1), bView, // NOLINT(misc-misplaced-widening-cast)
                    static_cast<xvg_format_t>(xvgFormat + 1), 0);

    int64_t run_step = ir->init_step;
    double run_t    = ir->init_step*ir->delta_t + ir->init_t;

    ir->nsteps = static_cast<int64_t>((until_t - run_t)/ir->delta_t + 0.5);

    ir->init_step = run_step;

    write_tpx_state(outfile.c_str(), ir, &state, &mtop);

    success = true;
    return success;
}
