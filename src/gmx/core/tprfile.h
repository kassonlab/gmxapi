/*! \file
 * \brief Declare TPR file helpers.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#ifndef GMXPY_TPRFILE_H
#define GMXPY_TPRFILE_H

#include <string>
#include <vector>

#include "exceptions.h"
#include "mdparams.h"

namespace gmxapicompat {

/*!
 * \brief Facade for objects that can provide atomic data for a configuration.
 */
class StructureSource;

/*!
 * \brief Facade for objects that can provide molecular topology information for a structure.
 */
class TopologySource;

/*!
 * \brief Proxy to simulation state data.
 */
class SimulationState;

/*!
 * \brief Manager for TPR file resources.
 *
 * Manager object should be shared by all users of resource associated with a
 * particular file.
 *
 * Multiple read-only handles may be issued if there are no write-handles.
 * One write handle may be issued if there are no other open handles.
 *
 * A const TprFile may only issue read file-handles, allowing handles to be
 * issued more quickly by avoiding atomic resource locking.
 *
 * \note Shared ownership of file manager could be avoided if owned by a Context.
 * It is appropriate for a Context to own and mediate access to the manager because
 * it provides the filesystem abstraction and in order to more intelligently
 * map named file paths to resources. For now, TprFileHandles share ownership
 * of the TprFile manager object via shared_ptr.
 */
class TprFile;

/*!
 * \brief Handle for a TPR file resource.
 *
 * Can provide StructureSource, TopologySource, GmxMdParams, and SimulationState
 */
class TprReadHandle
{
public:
    explicit TprReadHandle(std::shared_ptr<TprFile> tprFile);
    explicit TprReadHandle(TprFile&& tprFile);
    ~TprReadHandle();

    std::shared_ptr<TprFile> get() const ;
private:
    std::shared_ptr<TprFile> tprFile_;
};

/*!
 * \brief Open a TPR file and retrieve a handle.
 *
 * \param filename Path of file to read.
 * \return handle that may share ownership of TPR file resource.
 */
TprReadHandle readTprFile(const std::string& filename);

/*!
 * \brief Write a new TPR file to the filesystem with the provided contents.
 *
 * \param filename output file path
 * \param params simulation parameters
 * \param structure system structure (atomic configuration)
 * \param state simulation state
 * \param topology molecular topology
 */
void writeTprFile(const std::string &filename,
                  const GmxMdParams &params,
                  const StructureSource &structure,
                  const SimulationState &state,
                  const TopologySource &topology);

/*!
 * \brief Helper function for early implementation.
 *
 * Allows extraction of TPR file information from special params objects.
 *
 * \todo This is a very temporary shim!
 */
TprReadHandle getSourceFileHandle(const GmxMdParams &params);

/*!
 * \brief
 * \param filehandle
 * \return
 *
 * \todo replace with a helper template on T::topologySource() member function existence.
 */

TopologySource getTopologySource(const TprReadHandle& filehandle);

/*!
 * \brief
 * \param filehandle
 * \return
 *
 * \todo template on T::simulationState() member function existence.
 */
SimulationState getSimulationState(const TprReadHandle& filehandle);

StructureSource getStructureSource(const TprReadHandle& filehandle);

/*!
 * \brief Get an initialized parameters structure.
 * \param fileHandle
 * \return
 */
GmxMdParams getMdParams(const TprReadHandle& fileHandle);

std::vector<std::string> keys(const GmxMdParams& params);

class StructureSource
{
public:
    std::shared_ptr<TprFile> tprFile_;
};

class TopologySource
{
public:
    std::shared_ptr<TprFile> tprFile_;
};

class SimulationState
{
public:
    std::shared_ptr<TprFile> tprFile_;
};

} // end namespace gmxapicompat

namespace gmxpy
{

/*!
 * \brief Copy TPR file.
 *
 * \param input TPR source to copy from
 * \param outfile output TPR file name
 * \return true if successful. else false.
 */
bool copy_tprfile(const gmxapicompat::TprReadHandle& input, std::string outfile);

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
