
/*! \internal \file
 * \brief Declares symbols to be exported to gmx.core Python module.
 *
 */
#ifndef PYGMX_CORE_H
#define PYGMX_CORE_H

namespace pygmx
{

/*! \brief Wraps Trajectory Analyis Runner for Python interface.
 *
 * Exported to Python as gmx.core.TafRunner
 */
class PyRunner : public gmx::trajectoryanalysis::Runner
{
public:
    /*
    /// Empty constructor not yet used.
    PyRunner() = delete;
    */

    /// Empty constructor used for testing.
    PyRunner();

    /*
    /// Construct runner with a single bound module.
    PyRunner(std::shared_ptr<gmx::TrajectoryAnalysisModule>);
    */

    virtual ~PyRunner();

    /*! \brief Advance the current frame one step.
     *
     * Returns when data dependencies on the next trajectory frame have been
     * satisfied.
     */
    void next();
private:

};

// class CachingTafModule;

} // end namespace pygmx

#endif // PYGMX_CORE_H
