/*
    Portable header to provide the 32 and 64 bits type.

    Not a compatible replacement for <stdint.h>, do not blindly use it as such.
*/

#ifndef FIXEDINT_H_INCLUDED
#define FIXEDINT_H_INCLUDED

#if defined(__OPENCL_VERSION__)
// Use OpenCL's native types - they're always the right size
typedef uchar uint8_t;
typedef ushort uint16_t;
typedef uint uint32_t;   // Always 32-bit in OpenCL
typedef ulong uint64_t;  // Always 64-bit in OpenCL
typedef char int8_t;
typedef short int16_t;
typedef int int32_t;
typedef long int64_t;
#endif

#define UINT64_C(v) v##ULL
#define INT64_C(v) v##LL

#endif
