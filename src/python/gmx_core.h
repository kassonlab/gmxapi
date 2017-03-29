
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
#include "gromacs/options/options.h"


namespace gmx
{
/*! \brief API wrappers for Python bindings
 */
class OptionsVisitor;

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
    PyOptions(const PyOptions&) = delete;
    const PyOptions& operator=(const PyOptions&) = delete;
    // Copy semantics seem likely to involve multiple pointers to the same object rather than copies of the options object, but we'll see...
    // gmx::Options objects have implementation members that look like they are not meant to be copied...

    /// Get a raw pointer to the member data.
    gmx::Options* data();

    /// Provide a manager for OptionsVisitors
    /*! visitor may modify itself during traversal.
     */
    void view_traverse(gmx::OptionsVisitor&& visitor) const;
//    void modify_traverse(gmx::OptionsVisitor& visitor);

    bool parse();

private:
    gmx::Options options_;
    std::string filename_;
};

// Apply a OptionsVisitor that prints out the contents of the Options collection.
void print_options(const PyOptions& pyoptions);

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
    void initialize(PyOptions& options);

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

/// Wrapper for flat data structure
template<typename Scalar, size_t D>
class TrajDataArray
{
public:
    /*
    // Create empty container
    TrajDataArray() :
        data_{}
    {};
    */

    // Allocate space for an NxD array
    TrajDataArray(size_t N) :
        data_(N*D),
        N_(N)
    {};

    // Copy from raw data pointer.
    TrajDataArray(Scalar* data, size_t N) :
        data_(data, data + N*D),
        N_(N)
    {
    };

    // Move constructor
    //TrajDataArray(TrajDataArray&& )

    // The destructor cannot deallocate the memory pointed to.
    ~TrajDataArray() {};

    size_t dim() const { return D; };
    size_t N() const { return N_; };
    Scalar* data() { return data_.data(); };

private:
    std::vector<Scalar> data_; // Flat
    // Actual dimensions
    const size_t N_;
};

class PyTrajectoryFrame
{
public:
    /// Share ownership of a t_trxframe
    PyTrajectoryFrame(std::shared_ptr<t_trxframe> frame);

    /// Return a handle to a buffer of positions
    std::shared_ptr< TrajDataArray<real, 3> > x();

private:
    /// Handle to a t_trxframe object
    std::shared_ptr<t_trxframe> frame_;
};

// class CachingTafModule;

} // end namespace pyapi
} // end namespace gmx

#endif // PYGMX_CORE_H
