
/*! \internal \file
 * \brief Declares symbols to be exported to gmx.core Python module.
 *
 * Declares namespace gmx::pyapi
 */
#ifndef PYGMX_CORE_H
#define PYGMX_CORE_H

#include <memory>
#include "gromacs/trajectoryanalysis/analysismodule.h"
#include "gromacs/trajectoryanalysis/runner.h"

namespace gmx
{
/*! \brief API wrappers for Python bindings
 */
namespace pyapi
{
using std::shared_ptr;

/*! \brief Wraps an Options collection for exporting to Python.
*/
class PyOptions
{
public:
    /// Create an empty options container.
    PyOptions();
    /// Create an options container with our only known option.
    PyOptions(std::string filename);
    ~PyOptions();
    PyOptions(const PyOptions&) = default;
    // Copy semantics seem likely to involve multiple pointers to the same object rather than copies of the options object, but we'll see...
    // gmx::Options objects have implementation members that look like they are not meant to be copied...

    /// Get a raw pointer to the member data.
    gmx::Options & data();

    bool parse();

private:
    shared_ptr<gmx::Options> options_;
    std::string filename_;
};

/*! \brief Wraps Trajectory Analyis Runner for Python interface.
 *
 * Exported to Python as gmx.core.TafRunner
 */
class PyRunner
{
public:
    /// Empty constructor not yet used.
    PyRunner() = delete;

    /// Construct runner with a single bound module.
    PyRunner(shared_ptr<gmx::TrajectoryAnalysisModule> module);

    virtual ~PyRunner();

    /// Process options.
    void initialize(PyOptions options);

    /*! \brief Advance the current frame one step.
     *
     * Returns when data dependencies on the next trajectory frame have been
     * satisfied.
     */
    bool next();

private:
    /// has a common runner for most behavior
    gmx::trajectoryanalysis::Runner runner_;

    /// binds to one analysis module
    shared_ptr<gmx::TrajectoryAnalysisModule> module_;
};

// class CachingTafModule;

} // end namespace pyapi
} // end namespace gmx

#endif // PYGMX_CORE_H
