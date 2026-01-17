#include "base58.h"

__constant static char alphabet[] = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

__constant static char alphamap[] = {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0,  1,  2,
                                     3,  4,  5,  6,  7,  8,  -1, -1, -1, -1, -1, -1, -1, 9,  10, 11, 12, 13, 14, 15, 16, -1, 17, 18, 19, 20,
                                     21, -1, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, -1, -1, -1, -1, -1, -1, 33, 34, 35, 36, 37, 38, 39,
                                     40, 41, 42, 43, -1, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, -1, -1, -1, -1, -1};

size_t base58_encode(const char* in, char* out) {
    // leading zeroes
    size_t zero_count = 0;
    for (size_t i = 0; i < 32 && !in[i]; ++i) {
        out[zero_count++] = '1';
    }

    in += zero_count;
    size_t in_len = 32 - zero_count;
    out += zero_count;

    // encoding
    size_t idx = 0;
    for (size_t i = 0; i < in_len; ++i) {
        unsigned int carry = (unsigned char)in[i];
        for (size_t j = 0; j < idx; ++j) {
            carry += (unsigned int)out[j] << 8;
            out[j] = (unsigned char)(carry % 58);
            carry /= 58;
        }
        while (carry > 0) {
            out[idx++] = (unsigned char)(carry % 58);
            carry /= 58;
        }
    }

    // apply alphabet and reverse
    size_t c_idx = idx >> 1;
    for (size_t i = 0; i < c_idx; ++i) {
        char s = alphabet[(unsigned char)out[i]];
        out[i] = alphabet[(unsigned char)out[idx - (i + 1)]];
        out[idx - (i + 1)] = s;
    }
    if ((idx & 1)) {
        out[c_idx] = alphabet[(unsigned char)out[c_idx]];
    }

    // Remove trailing null bytes
    size_t total_len = zero_count + idx;
    while (total_len > 0 && out[total_len - 1] == '\0') {
        total_len--;
    }

    return total_len;
}
