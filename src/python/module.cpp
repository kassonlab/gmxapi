#include "pybind11/pybind11.h"
#include "pygmx.h"

const char* const name = "pygmx"; // set __name__
const char* const docstring = "GMX module"; // set __doc__

PYBIND11_PLUGIN(pygmx) {
    // Instantiate the module
    py::module m(name, docstring);

    // Declare classes
    // Declare a buffer type suitable for numpy Nx3 array output.
    // If we want to pass access but not ownership to Python, we need to make
    // sure we can allow a C++ shared pointer ref count to be increased.
    // The buffer protocol requires that the exporter (this code) keeps the
    // memory valid for the exported view until all consumers are done and
    // the PyBuffer_Release(buffer *view) is issued. I'm not sure, but I assume
    // pybind11 manages that for us by holding a shared_ptr to this.
    py::class_< pygmx::TrajDataArray<real, 3>, std::shared_ptr<pygmx::TrajDataArray<real, 3> > >(m, "TrajDataBuffer", py::buffer_protocol())
        .def_buffer(
            [](pygmx::TrajDataArray<real, 3> &data) -> py::buffer_info
            {
                return py::buffer_info(
                    data.data(),                        /* Pointer to buffer */
                    sizeof(real),                          /* Size of one scalar */
                    py::format_descriptor<real>::format(), /* Python struct-style format descriptor */
                    2,                                      /* Number of dimensions */
                    { data.N(), data.dim() },                 /* Python buffer dimensions */
                    { sizeof(real) * data.dim(), sizeof(real) }  /* Strides (in bytes) for each index in C++ */
                );
            }
        )
        // I don't see a way to safely perform a no-copy construction from a
        // buffer if TrajDataArray can have multiple references on the C++ side.
        // If the Python buffer views are all closed and there are no more
        // Python references to the object, then any remaining C++ references
        // to the object will have their data become invalid. If we want to set
        // data in TrajDataArray objects with minimal copies, we can use the
        // element access methods.
        // TO DO: only accept dense numpy arrays with array_t arguments.
        // py::array_t<real, py::array::c_style | py::array::forcecast> data
        .def("__init__", [](pygmx::TrajDataArray<real, 3> &data, py::buffer b)
        {
            /* Request a buffer descriptor from Python */
            py::buffer_info info = b.request();

            /* Some sanity checks ... */
            if (info.format != py::format_descriptor<real>::format())
            {
                throw std::runtime_error("Incompatible format: expected a array of type real!");
            };
            if (info.ndim != 2 || info.shape[0] != 3)
            {
                throw std::runtime_error("Incompatible buffer dimension!");
            };

            // Construct in place
            // It is important that the reference count of the buffer object b
            // should be incremented to prevent Python garbage collection from
            // deallocating the memory in the TrajDataArray object. I assume
            // pybind11 takes care of that.
            new (&data) pygmx::TrajDataArray<real, 3>(static_cast<real *>(info.ptr), info.shape[0]);
        });
    py::class_<pygmx::TrajectoryFrame>(m, "TrajectoryFrame")
        .def(py::init<const gmx_trr_header_t&>())
        //.def("box", &pygmx::TrajectoryFrame::box, "box matrix");
        .def("position", &pygmx::TrajectoryFrame::position, "position");
    py::class_<pygmx::Trajectory>(m, "Trajectory")
        .def(py::init<const std::string &>())
        .def("dump", &pygmx::Trajectory::dump, "Dump trajectory")
        .def_property_readonly("version", &pygmx::Trajectory::version)
        .def("nextFrame", &pygmx::Trajectory::nextFrame);
    // Define module-level functions.
    m.def("version", &pygmx::version, "Get Gromacs version");
    return m.ptr();
}
