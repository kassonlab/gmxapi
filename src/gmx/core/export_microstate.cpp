//
// Created by Eric Irrgang on 8/10/18.
//

#include "core.h"
#include "microstate.h"

// TprFile and MDCheckpoint must be exported to Python before this export function
// is called to ensure proper binding. In the future, we could handle this
// assurance more robustly by querying the registered Context type for named
// features or otherwise passing something around to each of the export functions,
// but such checks would happen at the time of Python module import. I can't
// think of a way to generate a compile-time error if, say, gmxpy::TprFile is
// referenced before export_tprfile will have had a chance to register the class
// and holder type.
void gmxpy::detail::export_microstate(pybind11::module &m) {
    namespace py = pybind11;

    py::class_<Microstate> microstate(m, "Microstate", "Simulation microstate");

    // Get ownership of a microstate proxy object.
    m.def("get_microstate",
        [](const TprFile& tprFile, const MDCheckpoint& checkpoint) -> std::unique_ptr<Microstate>
        {
            return readMicrostate(tprFile, checkpoint);
        },
          "Get a handle to the simulation microstate associated with the provided inputs.");

}
