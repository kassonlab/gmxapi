#ifndef HARMONICRESTRAINT_ENSEMBLEPOTENTIAL_H
#define HARMONICRESTRAINT_ENSEMBLEPOTENTIAL_H

/*! \file
 * \brief Provide restrained ensemble MD potential for GROMACS plugin.
 *
 * The restraint implemented here uses a facility provided by gmxapi to perform averaging of some
 * array data across an ensemble of simulations. Simpler pair restraints can use less of this
 * example code.
 *
 * Contains a lot of boiler plate that is being generalized and migrate out of this file, but other
 * pair restraints can be implemented by following the example in this and ``ensemblepotential.cpp``.
 * The ``CMakeLists.txt`` file will need to be updated if you add additional source files, and
 * ``src/pythonmodule/export_plugin.cpp`` will need to be updated if you add or change the name of
 * potentials.
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
struct ensemble_input_param_type
{
    // Inputs

    /// distance histogram parameters
    size_t nBins{0};
    double binWidth{0.};

    /// Flat-bottom potential boundaries.
    double minDist{0};
    double maxDist{0};

    /// Experimental reference distribution.
    std::vector<double> experimental{};

    /// Number of samples to store during each window.
    unsigned int nSamples{0};
    double samplePeriod{0};

    /// Number of windows to use for smoothing histogram updates.
    unsigned int nWindows{0};

    /// Harmonic force coefficient
    double k{0};
    /// Smoothing factor: width of Gaussian interpolation for histogram
    double sigma{0};

    // State data

    /// Smoothed historic distribution for this restraint. An element of the array of restraints in this simulation.
    std::vector<double> histogram;

    unsigned int currentSample{0};
    double nextSampleTime;

    /// Accumulated list of samples during a new window.
    std::vector<double> distanceSamples;

    size_t currentWindow{0};
    double windowStartTime{0};
    double nextWindowUpdateTime;
    /// The history of nwindows histograms for this restraint.
    std::vector<plugin::Matrix<double>> windows{};
};

std::unique_ptr<ensemble_input_param_type>
makeEnsembleParams(size_t nbins,
                   double binWidth,
                   double minDist,
                   double maxDist,
                   const std::vector<double>& experimental,
                   unsigned int nSamples,
                   double samplePeriod,
                   unsigned int nWindows,
                   double k,
                   double sigma);

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
class EnsemblePotential
{
    public:
        using input_param_type = ensemble_input_param_type;

        /* No default constructor. Parameters must be provided. */
        EnsemblePotential() = delete;

        /*!
         * \brief Constructor called by the wrapper code to produce a new instance.
         *
         * This constructor is called once per simulation per GROMACS process. Note that until
         * gmxapi 0.0.8 there is only one instance per simulation in a thread-MPI simulation.
         *
         * \param params
         */
        explicit EnsemblePotential(const input_param_type& params);

        /*!
         * \brief Deprecated constructor taking a parameter list.
         *
         * \param nbins
         * \param binWidth
         * \param minDist
         * \param maxDist
         * \param experimental
         * \param nSamples
         * \param samplePeriod
         * \param nWindows
         * \param k
         * \param sigma
         */
        EnsemblePotential(size_t nbins,
                          double binWidth,
                          double minDist,
                          double maxDist,
                          const std::vector<double>& experimental,
                          unsigned int nSamples,
                          double samplePeriod,
                          unsigned int nWindows,
                          double k,
                          double sigma);

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
class RestraintModule<Restraint<EnsemblePotential>>;

} // end namespace plugin

#endif //HARMONICRESTRAINT_ENSEMBLEPOTENTIAL_H
