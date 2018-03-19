//
// Created by Eric Irrgang on 3/18/18.
//

#include "core.h"

#include "gmxapi/context.h"


namespace gmxpy
{

namespace detail
{

namespace py = pybind11;


//-dd <vector> (0 0 0)
//Domain decomposition grid, 0 is optimize
//-npme <int> (-1)
//Number of separate ranks to be used for PME, -1 is guess
//-nt <int> (0)
//Total number of threads to start (0 is guess)
//-ntmpi <int> (0)
//Number of thread-MPI ranks to start (0 is guess)
//-ntomp <int> (0)
//Number of OpenMP threads per MPI rank to start (0 is guess)
//-ntomp_pme <int> (0)
//Number of OpenMP threads per MPI rank to start (0 is -ntomp)
//-nsteps <int> (-2)
//Run this number of steps, overrides .mdp file option (-1 means infinite, -2 means use mdp option, smaller is invalid)
//-maxh <real> (-1)
//Terminate after 0.99 times this time (hours)

void setMDArgs(std::vector<std::string>* mdargs, py::dict params)
{
    mdargs->clear();
    if (params.contains("grid"))
    {
        assert(py::len(params["grid"]) > 0);
        std::vector<std::string> vals;
        for (auto&& val : params["grid"])
        {
            vals.emplace_back(py::cast<std::string>(py::str(val)));
        }
        mdargs->emplace_back("-dd");
        for(auto&& val : vals)
        {
            mdargs->emplace_back(val);
        }
    }
    if (params.contains("pme_ranks"))
    {
        auto val = py::cast<std::string>(py::str(params["pme_ranks"]));
        mdargs->emplace_back("-npme");
        mdargs->emplace_back(val);
    }
    if (params.contains("threads"))
    {
        auto val = py::cast<std::string>(py::str(params["threads"]));
        mdargs->emplace_back("-nt");
        mdargs->emplace_back(val);
    }
    if (params.contains("tmpi"))
    {
        auto val = py::cast<std::string>(py::str(params["tmpi"]));
        mdargs->emplace_back("-ntmpi");
        mdargs->emplace_back(val);
    }
    if (params.contains("threads_per_rank"))
    {
        auto val = py::cast<std::string>(py::str(params["threads_per_rank"]));
        mdargs->emplace_back("-ntomp");
        mdargs->emplace_back(val);
    }
    if (params.contains("pme_threads_per_rank"))
    {
        auto val = py::cast<std::string>(py::str(params["pme_threads_per_rank"]));
        mdargs->emplace_back("-ntomp_pme");
        mdargs->emplace_back(val);
    }
    if (params.contains("steps"))
    {
        auto val = py::cast<std::string>(py::str(params["steps"]));
        mdargs->emplace_back("-nsteps");
        mdargs->emplace_back(val);
    }
    if (params.contains("max_hours"))
    {
        auto val = py::cast<std::string>(py::str(params["max_hours"]));
        mdargs->emplace_back("-maxh");
        mdargs->emplace_back(val);
    }
}

void export_context(py::module &m)
{
    using ::gmxapi::Context;
    // Export execution context class
    py::class_<Context, std::shared_ptr<Context>> context(m, "Context");
    context.def(py::init(), "Create a default execution context.");
    context.def("setMDArgs", &Context::setMDArgs, "Set MD runtime parameters.");

    using MDArgs = std::vector<std::string>;
    py::class_<MDArgs, std::unique_ptr<MDArgs>> mdargs(m, "MDArgs");
    mdargs.def(py::init(), "Create an empty MDArgs object.");
    mdargs.def("set", &setMDArgs, "Assign parameters in MDArgs from Python dict.");
}

} // end namespace gmxpy::detail

} // end namespace gmxpy
