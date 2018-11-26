//
// Created by Eric Irrgang on 11/20/18.
//

#ifndef GMXAPICOMPAT_EXCEPTIONS_H
#define GMXAPICOMPAT_EXCEPTIONS_H

#include <exception>
#include <string>

namespace gmxapicompat {

/*!
 * \brief Generic exception class for gmxapicompat.
 */
class Exception : public std::exception {
public:
    using std::exception::exception;

    explicit Exception(const std::string& message) :
            message_{message} {}
    explicit Exception(const char* message) : Exception(std::string(message)) {}

    const char *what() const noexcept override {
        return message_.c_str();
    }

private:
    std::string message_;
};

/*!
 * \brief The key name provided for a key-value mapping is invalid.
 */
class KeyError : public Exception {
    using Exception::Exception;
};

/*!
 * \brief The value provided for a key-value mapping is invalid.
 */
class ValueError : public Exception {
    using Exception::Exception;
};

/*!
 * \brief Value provided for a key-value mapping is of an incompatible type.
 */
class TypeError : public Exception {
    using Exception::Exception;
};

} // end namespace gmxapicompat
#endif //GMXAPICOMPAT_EXCEPTIONS_H
