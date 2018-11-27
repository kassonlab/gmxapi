//
// Created by Eric Irrgang on 11/26/18.
//

#ifndef GMXPY_TYPETEMPLATES_H
#define GMXPY_TYPETEMPLATES_H


#include <type_traits>

#include "mdparams.h"

namespace gmxapicompat {

namespace traits {

// These can be more than traits. We might as well make them named types.
struct gmxNull {
    static const GmxapiType value = GmxapiType::gmxNull;
};
struct gmxMap {
    static const GmxapiType value = GmxapiType::gmxMap;
};
struct gmxInt32 {
    static const GmxapiType value = GmxapiType::gmxInt32;
};
struct gmxInt64 {
    static const GmxapiType value = GmxapiType::gmxInt64;
};
struct gmxFloat32 {
    static const GmxapiType value = GmxapiType::gmxFloat32;
};
struct gmxFloat64 {
    static const GmxapiType value = GmxapiType::gmxFloat64;
};
struct gmxBool {
    static const GmxapiType value = GmxapiType::gmxBool;
};
struct gmxString {
    static const GmxapiType value = GmxapiType::gmxString;
};
struct gmxMDArray {
    static const GmxapiType value = GmxapiType::gmxMDArray;
};
//struct gmxFloat32Vector3 {
//    static const GmxapiType value = GmxapiType::gmxFloat32Vector3;
//};
//struct gmxFloat32SquareMatrix3 {
//    static const GmxapiType value = GmxapiType::gmxFloat32SquareMatrix3;
//};

} // end namespace traits

// Use an anonymous namespace to restrict these template definitions to file scope.
namespace {
// Partial specialization of functions is not allowed, which makes the following tedious.
// To-do: switch to type-based logic, struct templates, etc.
template<typename T, size_t s>
GmxapiType mapCppType() {
    return GmxapiType::gmxNull;
}

template<typename T>
GmxapiType mapCppType() {
    return mapCppType<T, sizeof(T)>();
};

template<>
GmxapiType mapCppType<bool>() {
    return GmxapiType::gmxBool;
}

template<>
GmxapiType mapCppType<int, 4>() {
    return GmxapiType::gmxInt32;
}

template<>
GmxapiType mapCppType<int, 8>() {
    return GmxapiType::gmxInt64;
};


template<>
GmxapiType mapCppType<float, 4>() {
    return GmxapiType::gmxFloat32;
}

template<>
GmxapiType mapCppType<double, 8>() {
    return GmxapiType::gmxFloat64;
};

} // end anonymous namespace

} // end namespace gmxapicompat

#endif //GMXPY_TYPETEMPLATES_H
