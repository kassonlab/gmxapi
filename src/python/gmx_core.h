
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
#include <stdexcept>

namespace gmx
{
class OptionsVisitor;

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

/// Apply a OptionsVisitor that prints out the contents of the Options collection.
void print_options(const PyOptions& pyoptions); // can't, really...

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
/*! This is a temporary shim to experiment with how to manage multidimensional
 * data of arbitrary size in ways that are friendly to old code, new code, and STL.
 */
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
    TrajDataArray() = delete;
    TrajDataArray(const TrajDataArray&) = delete;
    const TrajDataArray& operator=(const TrajDataArray&) = delete;

    /// Allocate space for an NxD array
    TrajDataArray(size_t N) :
        data_(N*D),
        N_(N)
    {
    };

    /// Copy from raw data pointer.
    TrajDataArray(Scalar* data_src, size_t N) :
        data_(N*D),
        N_(N)
    {
        std::copy(data_src, data_src + N*D, data_.begin());
    };

    // Move constructor
    //TrajDataArray(TrajDataArray&& )

    /// Simple destructor.
    ~TrajDataArray() { };

    /// Get width of data
    /*! \return number of columns (dimensionality for arrays of vectors)
     */
    size_t dim() const { return D; };
    /// Get number of elements
    /*! \return number of rows (number of elements for arrays of vectors)
     */
    size_t N() const { return N_; };

    /*! \brief Get raw pointer to managed data
     *
     * \return the pointer to the underlying contiguous data storage
     * This is very bad if the caller tries to delete the result.
     */
    Scalar* data() { return data_.data(); };

    /*! \brief indexing operator
     *
     * \param i (first) index in the two-dimensional array
     * \return a copy (not a reference) of row i as a std::vector of length D
     * TODO: Not sure why this isn't a std::array. span or array view could be
     * even better. But first some thought would need to go into the expected
     * readable/writable behavior. Note that the return value *will be copied*
     * when returned to Python unless shared via a shared_ptr or transfered via
     * unique_ptr to a class that Python is aware of (no casting necessary).
     */
    std::vector<Scalar> operator[](const size_t i) const
    {
        if (i < N_)
        {
            return std::vector<Scalar>(&data_[i*D], &data_[i*D] + D);
        }
        else
        {
            throw std::out_of_range("bad index value to Trajectory data");
        }
    }

private:
    /// Flattened array of data
    std::vector<Scalar> data_;
    /// Actual dimensions are N_ x D
    const size_t N_;
};

/*! \brief Minimal wrapper for t_trxframe.
 *
 * Hopefully very temporary. Wrapping and exposing t_trxframe is silly.
 * The next step is probably to provide a flexible wrapper to arbitrary
 * TrajectoryAnalysisDataModule data, trajectory or derived.
 * \ingroup module_python
 * \internal
 */
class PyTrajectoryFrame
{
public:
    /*! \brief Share ownership of a t_trxframe
     *
     * \param frame a managed frame pointer (with an appropriate deleter) that we can safely share.
     * These shared pointers must originate from gmx::trajectory::trxframe_copy
     * where a sensible deleter is provided. Unfortunately, this does not allow
     * the lifetime of a member array to be decoupled from the rest of the frame.
     */
    explicit PyTrajectoryFrame(std::shared_ptr<t_trxframe> frame);

    /*! Copy a t_trxframe
     *
     * \param frame a t_trxframe object to make a deep copy of
     * The copy is performed by gmx::trajectory::trxframe_copy, which provides
     * a sensible deleter, but cannot allow the lifetime of member arrays to
     * be decoupled from the whole frame.
     */
    explicit PyTrajectoryFrame(const t_trxframe& frame);

    /// With current t_trxframe usage, we have to be careful.
    PyTrajectoryFrame() = delete;
    /// TODO: this should be fine now, but need to test.
    const PyTrajectoryFrame& operator=(const PyTrajectoryFrame&) = delete;

    /// Return a handle to a buffer of positions
    /* Ideally, this buffer's life is not tied to the frame it is in, but it is
     * while we are using t_trxframe. We can copy the arrays for now to be on
     * the safe side, which happens in the TrajDataArray constructor used.
     * There is also something weird about lifetime management if a unique_ptr
     * is used to provide the buffer interface to Python. Maybe the py::buffer_info
     * does not keep alive the object that provides it, but a quick stepping
     * through the code looks like the object does not survive the conversion
     * from unique_ptr to shared_ptr in the export, so we can just use a shared_ptr
     * return value for now.
     */
    std::shared_ptr< TrajDataArray<real, 3> > x();

private:
    /// Handle to a shareable t_trxframe object
    std::shared_ptr<t_trxframe> frame_;
};

// class CachingTafModule;

} // end namespace pyapi
} // end namespace gmx

#endif // PYGMX_CORE_H
