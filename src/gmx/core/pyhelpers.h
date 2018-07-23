//
// Created by Eric Irrgang on 11/17/17.
//

#ifndef GMXPY_PYHELPERS_H
#define GMXPY_PYHELPERS_H

/*! \file
 * \brief Helpers for broad Python interoperability
 *
 * # Python interoperability
 *
 * We would like to be able to pass gmxapi C++ objects through the Python interpreter
 * regardless of how bindings are provided for any given extension module.
 * To do this, we use the Python Capsule machinery to hold a pointer to a
 * pointer to something that we can use to get a proper handle to the object.
 * The name of the capsule is used for typing and API compatibility checking.
 *
 * # C API
 *
 * We would like
 *
 * \ingroup module_python
 */


/*! Make a new Python Capsule object allowing access to member data.
 *
 * Ensure that the owning object stays alive as long as the capsule.
 *
 * The capsule holds a pointer to a pointer to an API object that is guaranteed to be valid
 * only during the function call in which the capsule was passed. In actuality, we can ensure
 * that the object that generated the capsule has a keepalive for the lifetime of the capsule,
 * and thereby guarantee that the pointed-to pointer is valid for the lifetime of the capsule,
 * but let's not commit ourselves to that yet. Instead, the consumer should access the pointed-to
 * object, probably to get a managed pointer, and then set the pointed-to pointer to zero to
 * signify that the container is no longer being used. We can provide a helper function for
 * this. It is not clear that it is a necessary protocol, but we'll use the pointer-to-pointer
 * plan anyway because (1) a capsule with a nullptr has special meaning, and (2) we always know
 * how big a pointer is, so it is an easy target to manage.
 *
 *
 * The struct needs to be able to outlive the capsule, and must not outlive the object it
 * is wrapping. It might be easiest, then, to let the wrapped object manage the struct and
 * extend the lifetime of the wrapped object by generating the capsule using a bound method
 * with a keepalive policy.
 *
 * Other considerations: We could allocate the struct from the heap, but that seems
 * like a waste of time, and sooner or later someone is going to accidentally leave one on
 * the stack that will get deallocated before the PyCapsule is garbage collected. We could
 * have null destructors for capsules pointing to stack data, but there is still the chance
 * of trying to dereference the Capsule pointer into an invalid part of the stack later.
 *
 * py::capsule SendingClass::encapsulate()
 * {
 *      return py::capsule(this->pyCapsule.get(), SendingClass::capsuleName);
 * };
 * *
 * receivingclass.def("method", [](py::capsule o){
 *     auto name = o.name();
 *     // check name...
 *     // The following probably only works if there are resolvable bindings for the type in the capsule
 *     //SendingClass::data_t * data = o;
 *     auto data = static_cast<SendingClass::data_t *>(PyCapsule_GetPointer(o.ptr(), name));
 *     if (data != nullptr)
 *     {
 *          // get something out of it and let it go.
 *     }
 * };
 */

static struct basic_holder {
    version_t api_version_major;
    version_t api_version_minor;
    void* ptr;
};

template<class T, version_t MAJOR, version_t MINOR>
struct holder {};

template<class T*, version_t MAJOR, version_t MINOR>
struct holder
{
    version_t api_version_major{MAJOR};
    version_t api_version_minor{MINOR};
    T* ptr{nullptr};
};

template<class T> void delete_holder_capsule(PyObject*);

template<class T*>
void delete_holder_capsule(PyObject* o)
{
    auto name = PyCapsule_GetName(o);
    if (PyCapsule_IsValid(o, name))
    {
        auto holder = static_cast<T*>(PyCapsule_GetPointer(o, name));
        // PyCapsule_IsValid() should assure us that holder != nullptr
        assert(holder != nullptr);
        delete holder;
    }
    // \todo should probably throw an APIError if failed.
}

/*!
 * \brief Call a function after wrapping its first argument in a
 * \tparam F
 * \tparam T
 * \tparam ArgsT
 * \param raw
 * \param pargs
 * \return
 */
template<class F, class T, class... ArgsT>
auto callEncapsulated(T raw, Args... pargs) -> decltype(F(raw, pargs...))
{};

#endif //GMXPY_PYHELPERS_H
