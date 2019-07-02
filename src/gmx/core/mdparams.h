#ifndef GMXPY_MDPARAMS_H
#define GMXPY_MDPARAMS_H

/*! \file
 * \brief Compatibility header for functionality differences in gmxapi releases.
 *
 * Also handle the transitioning installed headers from GROMACS 2019 moving forward.
 *
 * \todo Configure for gmxapi 0.0.7, 0.0.8, GROMACS 2019, GROMACS master...
 *
 * \defgroup gmxapi_compat
 * \ingroup gmxapi_compat
 */

#include <map>
#include <memory>
#include <string>

#include "exceptions.h"

struct t_inputrec;

/*!
 * \brief Compatibility code for features that may not be in gmxapi yet.
 */
namespace gmxapicompat
{


/*!
 * \brief Label the types recognized by gmxapi.
 *
 * Provide an enumeration to aid in translating data between languages, APIs,
 * and storage formats.
 *
 * \todo The spec should explicitly map these to types in APIs already used.
 * e.g. MPI, Python, numpy, GROMACS, JSON, etc.
 * \todo Actually check the size of the types.
 */
enum class GmxapiType {
    gmxNull, //! Reserved
    gmxMap, //! Mapping of key name (string) to a value of some MdParamType
    gmxBool, //! Boolean logical type
    gmxInt32, //! 32-bit integer type, initially unused
    gmxInt64, //! 64-bit integer type
    gmxFloat32, //! 32-bit float type, initially unused
    gmxFloat64, //! 64-bit float type
    gmxString, //! string with metadata
    gmxMDArray, //! multi-dimensional array with metadata
// Might be appropriate to have convenience types for small non-scalars that
// shouldn't need metadata.
//    gmxFloat32Vector3, //! 3 contiguous 32-bit floating point values.
//    gmxFloat32SquareMatrix3, //! 9 contiguous 32-bit FP values in row-major order.
};


/*!
 * \brief Static map of GROMACS 2019 mdp file entries to normalized "type".
 *
 * \return
 */
const std::map<std::string, GmxapiType> simulationParameterTypeMap();

const std::map<std::string, bool t_inputrec::*> boolParams();
const std::map<std::string, int t_inputrec::*> int32Params();
const std::map<std::string, float t_inputrec::*> float32Params();
const std::map<std::string, double t_inputrec::*> float64Params();
const std::map<std::string, int64_t t_inputrec::*> int64Params();

/*!
 * \brief Static mapping of parameter names to gmxapi types for GROMACS 2019.
 *
 * \param name MDP entry name.
 * \return enumeration value for known parameters.
 *
 * \throws gmxapi_compat::ValueError for parameters with no mapping.
 */
GmxapiType mdParamToType(const std::string& name);

// Forward declaration for private implementation class for GmxMdParams
class GmxMdParamsImpl;

/*!
 * \brief Handle / manager for GROMACS MM computation input parameters.
 *
 * Interface should be consistent with MDP file entries, but data maps to TPR
 * file interface. For type safety and simplicity, we don't have generic operator
 * accessors. Instead, we have templated accessors that throw exceptions when
 * there is trouble.
 *
 * When MDP input is entirely stored in a key-value tree, this class can be a
 * simple adapter or wrapper. Until then, we need a manually maintained mapping
 * of MDP entries to TPR data.
 *
 * Alternatively, we could update the infrastructure used by list_tpx to provide
 * more generic output, but our efforts may be better spent in updating the
 * infrastructure for the key-value tree input system.
 */
class GmxMdParams
{
public:
    GmxMdParams();
    ~GmxMdParams();
    GmxMdParams(const GmxMdParams&) = delete;
    GmxMdParams& operator=(const GmxMdParams&) = delete;
    GmxMdParams(GmxMdParams&&) noexcept;
    GmxMdParams& operator=(GmxMdParams&&) noexcept;

    std::unique_ptr<GmxMdParamsImpl> params_;
};

/*!
 * \brief A set of overloaded functions to fetch parameters of the indicated type, if possible.
 *
 * \param params Handle to a parameters structure from which to extract.
 * \param name Parameter name
 * \param
 *
 * Could be used for dispatch and/or some sort of templating in the future, but
 * invoked directly for now.
 */
int extractParam(const gmxapicompat::GmxMdParams& params, const std::string& name, int);
int64_t extractParam(const gmxapicompat::GmxMdParams& params, const std::string& name, int64_t);
float extractParam(const gmxapicompat::GmxMdParams& params, const std::string& name, float);
double extractParam(const gmxapicompat::GmxMdParams& params, const std::string& name, double);

void setParam(gmxapicompat::GmxMdParams* params, const std::string& name, double value);
void setParam(gmxapicompat::GmxMdParams* params, const std::string& name, int64_t value);
// TODO: unsetParam


// Anonymous namespace to confine helper function definitions to file scope.
namespace
{

bool isFloat(GmxapiType dataType)
{
    return (dataType == GmxapiType::gmxFloat64) || (dataType == GmxapiType::gmxFloat32);
}

bool isInt(GmxapiType dataType)
{
    return (dataType == GmxapiType::gmxInt64) || (dataType == GmxapiType::gmxInt32);
}

} // end anonymous namespace

} // end namespace gmxapicompat

#endif //GMXPY_MDPARAMS_H
