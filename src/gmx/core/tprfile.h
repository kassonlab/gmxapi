/*! \file
 * \brief Declare TPR file helpers.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#ifndef GMXPY_TPRFILE_H
#define GMXPY_TPRFILE_H

#include <string>

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
class TprFileHandle
{
public:
    explicit TprFileHandle(std::shared_ptr<TprFile> tprFile);
    explicit TprFileHandle(TprFile&& tprFile);
    ~TprFileHandle();

    std::shared_ptr<TprFile> get() const ;
private:
    std::shared_ptr<TprFile> tprFile_;
};

TprFileHandle readTprFile(const std::string& filename);

/*!
 * \brief
 * \param filehandle
 * \return
 *
 * \todo replace with a helper template on T::topologySource() member function existence.
 */

TopologySource getTopologySource(const TprFileHandle& filehandle);

/*!
 * \brief
 * \param filehandle
 * \return
 *
 * \todo template on T::simulationState() member function existence.
 */
SimulationState getSimulationState(const TprFileHandle& filehandle);

StructureSource getStructureSource(const TprFileHandle& filehandle);

/*!
 * \brief Get an initialized parameters structure.
 * \param fileHandle
 * \return
 */
GmxMdParams getMdParams(const TprFileHandle& fileHandle);

std::vector<std::string> keys(const GmxMdParams& params);

// Anonymous namespace for a template that we want to define at file scope.
namespace {
/*!
 * \brief Procedural interface for setting named parameters.
 *
 * \throws TypeError if parameter and value are of incompatible type.
 * \throws KeyError if parameter is unknown.
 *
 * \note The logic of errors is potentially confusing.
 */
template<typename T>
gmxapicompat::GmxMdParams &setParam(gmxapicompat::GmxMdParams *params,
                                    std::string keyname,
                                    T value) {
    const auto paramType = gmxapicompat::mdParamToType(keyname);
    if (paramType == gmxapicompat::GmxapiType::gmxInt64) {

    } else {
        // If parameter type is registered and we don't have handler code, this is a bug.
        assert(paramType == gmxapicompat::GmxapiType::gmxNull);
        throw gmxapicompat::KeyError(std::string("Unknown parameter name: ") + keyname);
    }
    return *params;
}
} // end anonymous namespace

///*!
// * \brief Extract a parameter to the requested type.
// *
// * \tparam T
// * \param params
// * \param name
// * \return
// *
// * \throws KeyError if parameter cannot be mapped.
// * \throws TypeError if parameter type cannot be converted to T.
// */
//template<typename T>
//T extractParam(const gmxapi_compat::GmxMdParams& params, const std::string& name)
//{
//    gmxapi_compat::GmxapiType paramType;
//    try
//    {
//        paramType = gmxapi_compat::mdParamToType(name);
//    }
//    catch(const gmxapi_compat::ValueError& e)
//    {
//        throw gmxapi_compat::KeyError("No parameter entry for this name and type.");
//    }
//
//    // If
//    if (paramType)
//    {}
//    else
//    {}
//
//    return {};
//}

} // end namespace gmxapicompat

namespace gmxpy
{
/*!
 * \brief Get a dictionary of MDP key-value pairs from a TPR file.
 *
 * \param filename TPR file name
 *
 * \return key-value pairs from filename
 *
 * \todo Move this to gmxapicompat to provide abstraction for different versions.
 * * handle GROMACS 2019, GROMACS master with and without feature
 * * handle TPR versions from GROMACS 2018 and later
 */
//pybind11::dict read_mdparams(const std::string &filename) {
//    using namespace pybind11::literals; // to bring in the `_a` literal
//
//    const char *topology_filename = filename.c_str();
//    t_inputrec irInstance;
//    t_inputrec *ir = &irInstance;
//    gmx_mtop_t mtop;
//    t_state state;
//    read_tpx_state(topology_filename, ir, &state, &mtop);
//
//    return pybind11::dict("nsteps"_a = ir->nsteps);
//}

/*!
 * \brief Write a TPR file using the provided input.
 *
 * \param filename output file name.
 * \param parameters GROMACS input parameters
 * \param structure atomic configuration
 * \param topology molecular topology information
 */
//void write_tpr(const std::string &filename,
//               pybind11::dict parameters,
//               const StructureSource &structureSource,
//               const TopologySource &topology) {
//
//    write_tpx_state(filename.c_str(), ir, &state, &mtop);
//}

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
