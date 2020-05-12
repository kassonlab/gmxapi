#ifndef ENSEMBLETIMER_H
#define ENSEMBLETIMER_H

/*! \file
 * \brief Provide an ensemble MD plugin to profile the facility with minimal overhead.
 *
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include <vector>
#include <array>
#include <mutex>

#include "gmxapi/gromacsfwd.h"

#include "gromacs/restraint/restraintpotential.h"
#include "gromacs/utility/real.h"

#include "restraint.h"
#include "sessionresources.h"

namespace plugin
{

/*!
 * \brief Structure for input and state.
 */
struct ensemble_timer_param_type
{
    std::vector<plugin::Matrix<double>> ensemble_data;
};

std::unique_ptr<ensemble_timer_param_type>
makeTimerParams();

/*!
 * \brief a residue-pair bias calculator for use in restrained-ensemble simulations.
 *
 * Applies a force between two sites according to the difference between an experimentally observed
 * site pair distance distribution and the distance distribution observed earlier in the simulation
 * trajectory. The sampled distribution is averaged from the previous `nwindows` histograms from all
 * ensemble members. Each window contains a histogram populated with `nsamples` distances recorded at
 * `sample_period` step intervals.
 *
 * \internal
 * During a the window_update_period steps of a window, the potential applied is a harmonic function of
 * the difference between the sampled and experimental histograms. At the beginning of the window, this
 * difference is found and a Gaussian blur is applied.
 */
class EnsembleTimer
{
    public:
        using input_param_type = ensemble_timer_param_type;

        /* No default constructor. Parameters must be provided. */
        EnsembleTimer() = delete;

        /*!
         * \brief Constructor called by the wrapper code to produce a new instance.
         *
         * This constructor is called once per simulation per GROMACS process. Note that until
         * gmxapi 0.0.8 there is only one instance per simulation in a thread-MPI simulation.
         *
         * \param params
         */
        explicit EnsembleTimer(const input_param_type& params);

        /*!
         * \brief Evaluates the pair restraint potential.
         *
         * In parallel simulations, the gmxapi framework does not make guarantees about where or
         * how many times this function is called. It should be simple and stateless; it should not
         * update class member data (see ``ensemblepotential.cpp``. For a more controlled API hook
         * and to manage state in the object, use ``callback()``.
         *
         * \param v position of the site for which force is being calculated.
         * \param v0 reference site (other member of the pair).
         * \param t current simulation time (ps).
         * \return container for force and potential energy data.
         */
        gmx::PotentialPointData calculate(gmx::Vector v,
                                          gmx::Vector v0,
                                          gmx_unused double t);

        /*!
         * \brief An update function to be called on the simulation master rank/thread periodically by the Restraint framework.
         *
         * Defining this function in a plugin potential is optional. If the function is defined,
         * the restraint framework calls this function (on the first rank only in a parallel simulation) before calling calculate().
         *
         * The callback may use resources provided by the Session in the callback to perform updates
         * to the local or global state of an ensemble of simulations. Future gmxapi releases will
         * include additional optimizations, allowing call-back frequency to be expressed, and more
         * general Session resources, as well as more flexible call signatures.
         */
        void callback(gmx::Vector v,
                      gmx::Vector v0,
                      double t,
                      const Resources& resources);

    private:
        /// Aggregate data structure holding object state.
        input_param_type state_;
};


// Important: Just declare the template instantiation here for client code.
// We will explicitly instantiate a definition in the .cpp file where the input_param_type is defined.
extern template
class RestraintModule<Restraint<EnsembleTimer>>;

} // end namespace plugin

#endif //ENSEMBLETIMER_H
