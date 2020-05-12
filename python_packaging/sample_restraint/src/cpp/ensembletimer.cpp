/*! \file
 * \brief Code to implement the potential declared in ensemblepotential.h
 *
 * This file currently contains boilerplate that will not be necessary in future gmxapi releases, as
 * well as additional code used in implementing the restrained ensemble example workflow.
 *
 * A simpler restraint potential would only update the calculate() function. If a callback function is
 * not needed or desired, remove the callback() code from this file and from ensemblepotential.h
 *
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include "ensembletimer.h"

#include <cassert>
#include <cmath>

#include <memory>
#include <vector>

#include "gmxapi/context.h"
#include "gmxapi/session.h"
#include "gmxapi/md/mdsignals.h"

#include "sessionresources.h"

namespace plugin
{
using std::make_unique;

EnsembleTimer::EnsembleTimer(const input_param_type& params) :
    state_(params)
{
}

//
//
// HERE is the (optional) function that updates the state of the restraint periodically.
// It is called before calculate() once per timestep per simulation (on the master rank of
// a parallelized simulation).
//
//
void EnsembleTimer::callback(gmx::Vector v,
                                 gmx::Vector v0,
                                 double t,
                                 const Resources& resources)
{
    // We request a handle each time before using resources to make error handling easier if there is a failure in
    // one of the ensemble member processes and to give more freedom to how resources are managed from step to step.
    auto ensemble = resources.getHandle();
    Matrix<double> matrix1(1,1);
    Matrix<double> matrix2(1,1);
    // Get global reduction (sum) and checkpoint.
    ensemble.reduce(matrix1, &matrix2);
}


//
//
// HERE is the function that does the calculation of the restraint force.
//
//
gmx::PotentialPointData EnsembleTimer::calculate(gmx::Vector v,
                                                    gmx::Vector v0,
                                                    double /* t */)
{
    return { } ;
}

std::unique_ptr<ensemble_timer_param_type>
makeTimerParams() {
    auto params = std::make_unique<ensemble_timer_param_type>();
    return params;
};

// Important: Explicitly instantiate a definition for the templated class declared in ensemblepotential.h.
// Failing to do this will cause a linker error.
template
class ::plugin::RestraintModule<Restraint<EnsembleTimer>>;

} // end namespace plugin
