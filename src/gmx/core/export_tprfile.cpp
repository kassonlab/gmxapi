//
// Created by Eric Irrgang on 8/10/18.
//

#include "core.h"
#include "mdparams.h"
#include "tprfile.h"
#include <pybind11/stl.h>

namespace gmxpy {


void detail::export_tprfile(pybind11::module &m)
{
    namespace py = pybind11;
    using gmxapicompat::GmxMdParams;
    using gmxapicompat::TprReadHandle;
    using gmxapicompat::readTprFile;

    py::class_<GmxMdParams> mdparams(m, "SimulationParameters");
    // We don't want Python users to create invalid params objects, so don't
    // export a constructor until we can default initialize a valid one.
    //    mdparams.def(py::init());
    mdparams.def("extract",
            [](const GmxMdParams& self)
            {
                py::dict dictionary;
                for (const auto& key : gmxapicompat::keys(self))
                {
                    const auto& paramType = gmxapicompat::mdParamToType(key);
                    if (gmxapicompat::isFloat(paramType))
                    {
                        dictionary[key.c_str()] = extractParam(self, key, double());
                    }
                    else if (gmxapicompat::isInt(paramType))
                    {
                        dictionary[key.c_str()] = extractParam(self, key, int64_t());
                    }
                }
                return dictionary;
            },
            "Get a dictionary of the parameters.");

//    mdparams.def("set",
//                 [](GmxMdParams* self, py::dict input)
//                 {},
//                 "Set several parameters at once."
//                 );

    // Overload a setter for each known type and None
    mdparams.def("set",
                 [](GmxMdParams* self, const std::string& key, py::int_ value)
                 {
                     gmxapicompat::setParam(self, key, py::cast<int64_t>(value));
                 },
                 py::arg("key").none(false),
                 py::arg("value").none(false),
                 "Use a dictionary to update simulation parameters.");
    mdparams.def("set",
                 [](GmxMdParams* self, const std::string& key, py::float_ value)
                 {
                     gmxapicompat::setParam(self, key, py::cast<double>(value));
                 },
                 py::arg("key").none(false),
                 py::arg("value").none(false),
                 "Use a dictionary to update simulation parameters.");
    mdparams.def("set",
                 [](GmxMdParams* self, const std::string& key, py::none)
                 {
                     // unsetParam(self, key);
                 },
                 py::arg("key").none(false),
                 py::arg("value"),
                 "Use a dictionary to update simulation parameters.");


    py::class_<TprReadHandle> tprfile(m, "TprFile");
    tprfile.def("params",
            [](const TprReadHandle& self)
            {
                auto params = gmxapicompat::getMdParams(self);
                return params;
            });

    m.def("read_tprfile",
            &readTprFile,
            py::arg("filename"),
            "Get a handle to a TPR file resource for a given file name.");

    m.def("write_tprfile",
            [](std::string filename, const GmxMdParams& parameterObject)
            {
                auto tprReadHandle = gmxapicompat::getSourceFileHandle(parameterObject);
                auto params = gmxapicompat::getMdParams(tprReadHandle);
                auto structure = gmxapicompat::getStructureSource(tprReadHandle);
                auto state = gmxapicompat::getSimulationState(tprReadHandle);
                auto topology = gmxapicompat::getTopologySource(tprReadHandle);
                gmxapicompat::writeTprFile(filename, params, structure, state, topology);
            },
            py::arg("filename").none(false),
            py::arg("parameters"),
            "Write a new TPR file with the provided data.");

    m.def("copy_tprfile",
          [](const gmxapicompat::TprReadHandle& input, std::string outfile)
          {
              return gmxpy::copy_tprfile(input, outfile);
          },
          py::arg("source"),
          py::arg("destination"),
          "Copy a TPR file from `source` to `destination`."
          );

    m.def("copy_tprfile",
          [](std::string input, std::string output, double end_time)
          {
              return gmxpy::copy_tprfile(input, output, end_time);
          },
          py::arg("source"),
          py::arg("destination"),
          py::arg("end_time"),
          "Copy a TPR file from `source` to `destination`, replacing `nsteps` with `end_time`.");
}

} // end namespace gmxpy
