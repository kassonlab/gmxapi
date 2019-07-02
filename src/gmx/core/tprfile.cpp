/*! \file
 * \brief Helper code for TPR file access.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include "tprfile.h"

#include <cassert>

#include <map>
#include <memory>
#include <string>
#include <vector>

#include "gromacs/mdtypes/inputrec.h"
#include "gromacs/topology/topology.h"
#include "gromacs/mdtypes/state.h"
#include "gromacs/fileio/oenv.h"
#include "gromacs/fileio/tpxio.h"
#include "gromacs/fileio/trxio.h"
#include "gromacs/options/timeunitmanager.h"
#include "gromacs/utility/cstringutil.h"
#include "gromacs/utility/programcontext.h"

#include "exceptions.h"
#include "mdparams.h"
#include "typetemplates.h"

namespace gmxapicompat
{

class TprFile
{
public:
    explicit TprFile(const std::string& infile) :
            irInstance_{std::make_unique<t_inputrec>()},
            mtop_{std::make_unique<gmx_mtop_t>()},
            state_{std::make_unique<t_state>()}
    {
        t_inputrec *ir = irInstance_.get();
        read_tpx_state(infile.c_str(), ir, state_.get(), mtop_.get());
    }
    ~TprFile() = default;
    TprFile(TprFile&& source) noexcept = default;
    TprFile& operator=(TprFile&&) noexcept = default;

    /*!
     * \brief Get a reference to the input record in the TPR file.
     *
     * Note that this implementation allows different objects to share ownership
     * of the TprFile and does not provide access restrictions to prevent multiple
     * code blocks writing to the input record. This should be resolved with a
     * combination of managed access controlled handles and through better
     * management of the data structures in the TPR file. I.e. the t_inputrec is
     * not copyable, moveable, nor default constructable (at least, to produce a
     * valid record), and it does not necessarily make sense to map the library
     * data structure to the file data structure (except that we don't have another
     * way of constructing a complete and valid input record).
     *
     * \todo We can't play fast and loose with the irInstance for long...
     *
     * \return
     */
    t_inputrec& inputRecord() const
    {
        assert(irInstance_);
        return *irInstance_;
    }

    gmx_mtop_t& molecularTopology() const
    {
        assert(mtop_);
        return *mtop_;
    }

    t_state& state() const
    {
        assert(state_);
        return *state_;
    }
private:
    // These types are not moveable in GROMACS 2019, so we use unique_ptr as a
    // moveable wrapper to let TprFile be moveable.
    std::unique_ptr<t_inputrec>  irInstance_;
    std::unique_ptr<gmx_mtop_t>        mtop_;
    std::unique_ptr<t_state>           state_;

};

/*!
 * \brief Static map of GROMACS 2019 mdp file entries to normalized "type".
 *
 * \return
 */
const std::map<std::string, GmxapiType> simulationParameterTypeMap()
{
    return {
            {"integrator", GmxapiType::gmxString},
            {"tinit",      GmxapiType::gmxFloat64},
            {"dt",         GmxapiType::gmxFloat64},
            {"nsteps",     GmxapiType::gmxInt64},
            {"init-step",     GmxapiType::gmxInt64},
            {"simulation-part",     GmxapiType::gmxInt64},
            {"comm-mode",     GmxapiType::gmxString},
            {"nstcomm",     GmxapiType::gmxInt64},
            {"comm-grps",     GmxapiType::gmxMDArray}, // Note: we do not have processing for this yet.
            {"bd-fric",     GmxapiType::gmxFloat64},
            {"ld-seed",     GmxapiType::gmxInt64},
            {"emtol",     GmxapiType::gmxFloat64},
            {"emstep",     GmxapiType::gmxFloat64},
            {"niter",     GmxapiType::gmxInt64},
            {"fcstep",     GmxapiType::gmxFloat64},
            {"nstcgsteep",     GmxapiType::gmxInt64},
            {"nbfgscorr",     GmxapiType::gmxInt64},
            {"rtpi",     GmxapiType::gmxFloat64},
            {"nstxout",     GmxapiType::gmxInt64},
            {"nstvout",     GmxapiType::gmxInt64},
            {"nstfout",     GmxapiType::gmxInt64},
            {"nstlog",     GmxapiType::gmxInt64},
            {"nstcalcenergy",     GmxapiType::gmxInt64},
            {"nstenergy",     GmxapiType::gmxInt64},
            {"nstxout-compressed",     GmxapiType::gmxInt64},
            {"compressed-x-precision",     GmxapiType::gmxFloat64},
//            {"compressed-x-grps",     GmxapiType::gmxMDArray},
//            {"energygrps",     GmxapiType::gmxInt64},
            {"cutoff-scheme",     GmxapiType::gmxString},
            {"nstlist",     GmxapiType::gmxInt64},
            {"ns-type",     GmxapiType::gmxString},
            {"pbc",     GmxapiType::gmxString},
            {"periodic-molecules",     GmxapiType::gmxBool},
//            ...

    };
};

/*
 * Visitor for predetermined known types.
 *
 * Development sequence:
 * 1. map pointers
 * 2. map setters ()
 * 3. template the Visitor setter for compile-time extensibility of type and to prune incompatible types.
 * 4. switch to Variant type for handling (setter templated on caller input)
 * 5. switch to Variant type for input as well? (Variant in public API?)
 */

const std::map<std::string, bool t_inputrec::*> boolParams()
{
    return {
            {"periodic-molecules", &t_inputrec::bPeriodicMols},
//            ...
    };
}

const std::map<std::string, int t_inputrec::*> int32Params()
{
    return {
            {"simulation-part",     &t_inputrec::simulation_part},
            {"nstcomm",     &t_inputrec::nstcomm},
            {"niter",     &t_inputrec::niter},
            {"nstcgsteep",     &t_inputrec::nstcgsteep},
            {"nbfgscorr",     &t_inputrec::nbfgscorr},
            {"nstxout",     &t_inputrec::nstxout},
            {"nstvout",     &t_inputrec::nstvout},
            {"nstfout",     &t_inputrec::nstfout},
            {"nstlog",     &t_inputrec::nstlog},
            {"nstcalcenergy",     &t_inputrec::nstcalcenergy},
            {"nstenergy",     &t_inputrec::nstenergy},
            {"nstxout-compressed",     &t_inputrec::nstxout_compressed},
            {"nstlist",     &t_inputrec::nstlist},
//            ...
    };
}

const std::map<std::string, float t_inputrec::*> float32Params()
{
    return {
            {"bd-fric",     &t_inputrec::bd_fric},
            {"emtol",     &t_inputrec::em_tol},
            {"emstep",     &t_inputrec::em_stepsize},
            {"fcstep",     &t_inputrec::fc_stepsize},
            {"rtpi",     &t_inputrec::rtpi},
            {"compressed-x-precision",     &t_inputrec::x_compression_precision},
//            ...

    };
}
const std::map<std::string, double t_inputrec::*> float64Params()
{
    return {
            {"dt", &t_inputrec::delta_t},
            {"tinit", &t_inputrec::init_t},
//            ...

    };
}
const std::map<std::string, int64_t t_inputrec::*> int64Params()
{
    return {
            {"nsteps",     &t_inputrec::nsteps},
            {"init-step",     &t_inputrec::init_step},
            {"ld-seed",     &t_inputrec::ld_seed},
//            ...

    };
}

/*!
 * \brief Static mapping of parameter names to gmxapi types for GROMACS 2019.
 *
 * \param name MDP entry name.
 * \return enumeration value for known parameters.
 *
 * \throws gmxapi_compat::ValueError for parameters with no mapping.
 */
GmxapiType mdParamToType(const std::string& name)
{
    const auto staticMap = simulationParameterTypeMap();
    auto entry = staticMap.find(name);
    if(entry == staticMap.end())
    {
        throw ValueError("Named parameter has unknown type mapping.");
    }
    return entry->second;
};


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
class GmxMdParamsImpl final
{
public:
    /*!
     * \brief Create an initialized but empty parameters structure.
     *
     * Parameter keys are set at construction, but all values are empty. This
     * allows the caller to check for valid parameter names or their types,
     * while allowing the consuming code to know which parameters were explicitly
     * set by the caller.
     *
     * To load values from a TPR file, see getMdParams().
     */
    GmxMdParamsImpl();

    explicit GmxMdParamsImpl(std::shared_ptr<TprFile> tprfile);

    /*!
     * \brief Get the current list of keys.
     *
     * \return
     */
    std::vector<std::string> keys() const
    {
        std::vector<std::string> keyList;
        for (auto&& entry : int64Params_)
        {
            keyList.emplace_back(entry.first);
        }
        for (auto&& entry : intParams_)
        {
            keyList.emplace_back(entry.first);
        }
        for (auto&& entry : floatParams_)
        {
            keyList.emplace_back(entry.first);
        }
        for (auto&& entry : float64Params_)
        {
            keyList.emplace_back(entry.first);
        }
        return keyList;
    };

    template<typename T> T extract(const std::string& key) const
    {
        auto value = T();
        // should be an APIError
        throw TypeError("unhandled type");
    }

    void set(const std::string& key, const int64_t& value)
    {
        if (int64Params_.find(key) != int64Params_.end())
        {
            int64Params_[key] = std::make_pair(value, true);

            if (source_)
            {
                auto memberPointer = int64Params().at(key);
                source_->inputRecord().*memberPointer = value;
            }
        }
        else if (intParams_.find(key) != intParams_.end())
        {
            // TODO: check whether value is too large?
            intParams_[key] = std::make_pair(static_cast<int>(value), true);

            if (source_)
            {
                auto memberPointer = int32Params().at(key);
                source_->inputRecord().*memberPointer = value;
            }

        }
        else
        {
            throw KeyError("Named parameter is incompatible with integer type value.");
        }
    };

    void set(const std::string& key, const double& value)
    {
        if (float64Params_.find(key) != float64Params_.end())
        {
            float64Params_[key] = std::make_pair(value, true);

            if (source_)
            {
                auto memberPointer = float64Params().at(key);
                source_->inputRecord().*memberPointer = value;
            }

        }
        else if (floatParams_.find(key) != floatParams_.end())
        {
            // TODO: check whether value is too large?
            floatParams_[key] = std::make_pair(static_cast<float>(value), true);

            if (source_)
            {
                auto memberPointer = float32Params().at(key);
                source_->inputRecord().*memberPointer = value;
            }

        }
        else
        {
            throw KeyError("Named parameter is incompatible with floating point type value.");
        }
    };
//
//    // Uses expression SFINAE of the return type to be sure of the right overload
//    // at template instantiation. Causes compile error if a setter is not available
//    // for the parameter type T.
//    template<typename T> auto set(const std::string& key, const T& value) -> decltype(setParam(key, value), void())
//    {
//        this->set(key, value);
//    }

    TprReadHandle getSource() const
    {
        // Note: might return a null handle. Need to decide what that means and how to address it.
        return TprReadHandle(source_);
    }

private:

    // Hold the settable parameters and whether or not they have been set.
    // TODO: update to gmxapi named types?
    std::map<std::string, std::pair<int64_t, bool>> int64Params_;
    std::map<std::string, std::pair<int, bool>> intParams_;
    std::map<std::string, std::pair<float, bool>> floatParams_;
    std::map<std::string, std::pair<double, bool>> float64Params_;

    std::shared_ptr<TprFile> source_;
};

void setParam(gmxapicompat::GmxMdParams *params, const std::string &name, double value)
{
    assert(params != nullptr);
    assert(params->params_ != nullptr);
    params->params_->set(name, value);
}

void setParam(gmxapicompat::GmxMdParams *params, const std::string &name, int64_t value)
{
    assert(params != nullptr);
    assert(params->params_ != nullptr);
    params->params_->set(name, value);
}

/*!
 * \brief A GmxMdParams implementation that depends on TPR files.
 *
 * \param tprfile
 */
GmxMdParamsImpl::GmxMdParamsImpl(std::shared_ptr<gmxapicompat::TprFile> tprfile) :
        source_{std::move(tprfile)}
{
    for (const auto& definition : int64Params())
    {
        auto& params = int64Params_;

        // the rest of this loop is copy->paste-able
        const auto& key = definition.first;
        auto memberPointer = definition.second;
        if (source_)
        {
            auto& irInstance = source_->inputRecord();
            auto fileValue = irInstance.*memberPointer;
            params[key] = std::make_pair(fileValue, true);
        } else
        {
            params[key] = {};
        }
    }
    for (const auto& definition : int32Params())
    {
        auto& params = intParams_;

        // the rest of this loop is copy->paste-able
        const auto& key = definition.first;
        auto memberPointer = definition.second;
        if (source_)
        {
            auto& irInstance = source_->inputRecord();
            auto fileValue = irInstance.*memberPointer;
            params[key] = std::make_pair(fileValue, true);
        } else
        {
            params[key] = {};
        }
    }
    for (const auto& definition : float32Params())
    {
        auto& params = floatParams_;

        // the rest of this loop is copy->paste-able
        const auto& key = definition.first;
        auto memberPointer = definition.second;
        if (source_)
        {
            auto& irInstance = source_->inputRecord();
            auto fileValue = irInstance.*memberPointer;
            params[key] = std::make_pair(fileValue, true);
        } else
        {
            params[key] = {};
        }
    }
    for (const auto& definition : float64Params())
    {
        auto& params = float64Params_;

        // the rest of this loop is copy->paste-able
        const auto& key = definition.first;
        auto memberPointer = definition.second;
        if (source_)
        {
            auto& irInstance = source_->inputRecord();
            auto fileValue = irInstance.*memberPointer;
            params[key] = std::make_pair(fileValue, true);
        } else
        {
            params[key] = {};
        }
    }

}

GmxMdParamsImpl::GmxMdParamsImpl() :
        GmxMdParamsImpl(nullptr)
{}

template<>
int GmxMdParamsImpl::extract<int>(const std::string& key) const {
    const auto& params = intParams_;
    const auto& entry = params.find(key);
    if (entry == params.cend())
    {
        throw KeyError("Parameter of the requested name and type not defined.");
    }
    else if (! entry->second.second)
    {
        // TODO: handle invalid and unset parameters differently.
        throw KeyError("Parameter of the requested name not set.");
    }
    else
    {
        return entry->second.first;
    }
}

template<>
int64_t GmxMdParamsImpl::extract<int64_t>(const std::string& key) const {
    const auto& params = int64Params_;
    const auto& entry = params.find(key);
    if (entry == params.cend())
    {
        throw KeyError("Parameter of the requested name and type not defined.");
    }
    else if (! entry->second.second)
    {
        // TODO: handle invalid and unset parameters differently.
        throw KeyError("Parameter of the requested name not set.");
    }
    else
    {
        return entry->second.first;
    }
}
template<>
float GmxMdParamsImpl::extract<float>(const std::string& key) const {
    const auto& params = floatParams_;
    const auto& entry = params.find(key);
    if (entry == params.cend())
    {
        throw KeyError("Parameter of the requested name and type not defined.");
    }
    else if (! entry->second.second)
    {
        // TODO: handle invalid and unset parameters differently.
        throw KeyError("Parameter of the requested name not set.");
    }
    else
    {
        return entry->second.first;
    }
}
template<>
double GmxMdParamsImpl::extract<double>(const std::string& key) const {
    const auto& params = float64Params_;
    const auto& entry = params.find(key);
    if (entry == params.cend())
    {
        throw KeyError("Parameter of the requested name and type not defined.");
    }
    else if (! entry->second.second)
    {
        // TODO: handle invalid and unset parameters differently.
        throw KeyError("Parameter of the requested name not set.");
    }
    else
    {
        return entry->second.first;
    }
}


int extractParam(const GmxMdParams &params, const std::string &name, int) {
    assert(params.params_);
    return params.params_->extract<int>(name);
}

int64_t extractParam(const GmxMdParams &params, const std::string &name, int64_t) {
    assert(params.params_);
    int64_t value{};
    // Allow fetching both known integer types.
    try {
        value = params.params_->extract<int>(name);
    }
    catch (const KeyError& error)
    {
        // If not found as a regular int, check for int64.
        try {
            value = params.params_->extract<int64_t >(name);
        }
        catch (const KeyError& error64)
        {
            throw KeyError("Parameter of the requested name not set.");
        }
    }
    // Any other exceptions propagate out.
    return value;
}

float extractParam(const GmxMdParams &params, const std::string &name, float) {
    assert(params.params_);
    return params.params_->extract<float>(name);
}

double extractParam(const GmxMdParams &params, const std::string &name, double) {
    assert(params.params_);
    double value{};
    // Allow fetching both single and double precision.
    try {
        value = params.params_->extract<double>(name);
    }
    catch (const KeyError& errorDouble)
    {
        // If not found as a double precision value, check for single-precision.
        try {
            value = params.params_->extract<float>(name);
        }
        catch (const KeyError& errorFloat)
        {
            throw KeyError("Parameter of the requested name not set.");
        }
    }
    // Any other exceptions propagate out.
    return value;
}

std::vector<std::string> keys(const GmxMdParams &params) {
    return params.params_->keys();
}


TprReadHandle readTprFile(const std::string& filename) {
    auto tprfile = gmxapicompat::TprFile(filename);
    auto handle = gmxapicompat::TprReadHandle(std::move(tprfile));
    return handle;
}

GmxMdParams getMdParams(const TprReadHandle &fileHandle) {
    auto tprfile = fileHandle.get();
    // TODO: convert to exception / decide whether null handles are allowed.
    assert(tprfile);
    GmxMdParams params;
    params.params_ = std::make_unique<GmxMdParamsImpl>(tprfile);
    return params;
}

TopologySource getTopologySource(const TprReadHandle &filehandle) {
    TopologySource source;
    source.tprFile_ = filehandle.get();
    return source;
}

SimulationState getSimulationState(const TprReadHandle &filehandle) {
    SimulationState source;
    source.tprFile_ = filehandle.get();
    return source;
}

StructureSource getStructureSource(const TprReadHandle &filehandle) {
    StructureSource source;
    source.tprFile_ = filehandle.get();
    return source;
}

TprReadHandle::TprReadHandle(std::shared_ptr<TprFile> tprFile) :
    tprFile_{std::move(tprFile)}
{
}

TprReadHandle getSourceFileHandle(const GmxMdParams &params)
{
    return params.params_->getSource();
}

void writeTprFile(const std::string &filename,
                  const GmxMdParams &params,
                  const StructureSource &structure,
                  const SimulationState &state,
                  const TopologySource &topology)
{
    assert(params.params_);
    // The only way we can check for consistent input right now is to make sure
    // it all comes from the same file.
    if (structure.tprFile_.get() != state.tprFile_.get() ||
        state.tprFile_.get() != topology.tprFile_.get() ||
        topology.tprFile_.get() != params.params_->getSource().get().get() ||
        params.params_->getSource().get().get() != structure.tprFile_.get()
    )
    {
        throw ValueError("writeTprFile does not yet know how to reconcile data from different TPR file sources.");
    }

    auto tprFileHandle = params.params_->getSource();
    auto tprFile = tprFileHandle.get();
    assert(tprFile);
    auto& inputRecord = tprFile->inputRecord();
    auto& writeState = tprFile->state();
    auto& writeTopology = tprFile->molecularTopology();
    write_tpx_state(filename.c_str(), &inputRecord, &writeState, &writeTopology);

}

TprReadHandle::TprReadHandle(TprFile &&tprFile) :
    TprReadHandle{std::make_shared<TprFile>(std::move(tprFile))}
{
}

std::shared_ptr<TprFile> TprReadHandle::get() const {
    return tprFile_;
}

// defaulted here to delay definition until after member types are defined.
TprReadHandle::~TprReadHandle() = default;

GmxMdParams::~GmxMdParams() = default;

GmxMdParams::GmxMdParams() :
    params_{std::make_unique<GmxMdParamsImpl>()}
{}

GmxMdParams::GmxMdParams(GmxMdParams &&) noexcept = default;

GmxMdParams &GmxMdParams::operator=(GmxMdParams &&) noexcept = default;

} // end namespace gmxapicompat

namespace gmxpy
{

// maybe this should return a handle to the new file?
bool copy_tprfile(const gmxapicompat::TprReadHandle& input, std::string outfile)
{
    if (!input.get())
    {
        return false;
    }
    gmxapicompat::writeTprFile(outfile,
                               gmxapicompat::getMdParams(input),
                               gmxapicompat::getStructureSource(input),
                               gmxapicompat::getSimulationState(input),
                               gmxapicompat::getTopologySource(input));
    return true;
}

bool copy_tprfile(std::string infile, std::string outfile, double until_t) {
    bool success = false;

    const char * top_fn = infile.c_str();

    t_inputrec  irInstance;
    t_inputrec *ir = &irInstance;
    gmx_mtop_t        mtop;
    t_state           state;
    read_tpx_state(top_fn, ir, &state, &mtop);


    char              buf[200], buf2[200];



    /* set program name, command line, and default values for output options */
    gmx_output_env_t *oenv;
    gmx::TimeUnit  timeUnit = gmx::TimeUnit_Default;
    bool bView{false}; // argument that says we don't want to view graphs.
    int xvgFormat{0};
    output_env_init(&oenv, gmx::getProgramContext(),
                    static_cast<time_unit_t>(timeUnit + 1), bView, // NOLINT(misc-misplaced-widening-cast)
                    static_cast<xvg_format_t>(xvgFormat + 1), 0);

    int64_t run_step = ir->init_step;
    double run_t    = ir->init_step*ir->delta_t + ir->init_t;

    ir->nsteps = static_cast<int64_t>((until_t - run_t)/ir->delta_t + 0.5);

    ir->init_step = run_step;

    write_tpx_state(outfile.c_str(), ir, &state, &mtop);

    success = true;
    return success;
}

} // end namespace gmxpy
