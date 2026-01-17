#include "base58/base58.c"
#include "ed25519/fe.c"
#include "ed25519/ge.c"
#include "ed25519/keypair.c"
#include "ed25519/sha512.c"
#include "match.c"

void increment_le(const __generic uchar* inp, size_t inc, uchar* out) {
    unsigned int carry = 0;

#pragma unroll
    for (size_t i = 0; i < 32; i++) {
        // Extract byte from inc (LSB first)
        unsigned int inc_byte = (i < sizeof(size_t)) ? ((inc >> (i * 8)) & 0xFF) : 0;

        // Add input byte + increment byte + carry
        unsigned int sum = inp[i] + inc_byte + carry;

        // Store result and propagate carry
        out[i] = (uchar)(sum & 0xFF);
        carry = sum >> 8;
    }
}

void increment_be(const __generic uchar* inp, size_t inc, uchar* out) {
    unsigned int carry = 0;

#pragma unroll
    for (int i = 31; i >= 0; i--) {
        // Calculate which byte of inc to use
        size_t byte_idx = 31 - i;
        unsigned int inc_byte = (byte_idx < sizeof(size_t)) ? ((inc >> (byte_idx * 8)) & 0xFF) : 0;

        // Add input byte + increment byte + carry
        unsigned int sum = inp[i] + inc_byte + carry;

        // Store result and propagate carry
        out[i] = (uchar)(sum & 0xFF);
        carry = sum >> 8;
    }
}

void generate_seed(const __generic uchar* seed, size_t id, uchar* out) {
    // Increment the seed by the global id
    // using BE just because
    increment_be(seed, id, out);
}

__kernel void generate_vanity_addresses(__global const uchar* base_seed,
                                        __global uchar* results,
                                        __global uint* result_count,
                                        uint match_mode,
                                        __constant uchar* word_chars,
                                        uint word_len) {
    size_t gid = get_global_id(0);
    uchar local_seed[32];
    uchar local_public_key[32];
    uchar local_private_key[64];  // Will be seed || pubkey
    char local_addr_b58[45];

    // generate the local seed from the base seed and the global id
    generate_seed(base_seed, gid, local_seed);

    // generate the public ed25519 key
    ed25519_create_keypair(local_public_key, local_private_key, local_seed);

    // Force privkey to be seed || pubkey format (to match Go convention)
#pragma unroll
    for (int i = 0; i < 32; i++) {
        local_private_key[i] = local_seed[i];
    }
#pragma unroll
    for (int i = 0; i < 32; i++) {
        local_private_key[32 + i] = local_public_key[i];
    }

    // encode the public key in base58
    size_t local_addr_b58_len = base58_encode((char*)local_public_key, local_addr_b58);

    bool match = false;

    switch (match_mode) {
        case 0:
            match = has_prefix(local_addr_b58, word_chars, word_len, false);
            break;

        case 1:
            match = has_prefix(local_addr_b58, word_chars, word_len, true);
            break;

        case 2:
            match = has_suffix(local_addr_b58, local_addr_b58_len, word_chars, word_len, false);
            break;

        case 3:
            match = has_suffix(local_addr_b58, local_addr_b58_len, word_chars, word_len, true);
            break;

        case 4:
            match = has_prefix(local_addr_b58, word_chars, word_len, false) ||
                    has_suffix(local_addr_b58, local_addr_b58_len, word_chars, word_len, false);
            break;

        case 5:
            match = has_prefix(local_addr_b58, word_chars, word_len, true) ||
                    has_suffix(local_addr_b58, local_addr_b58_len, word_chars, word_len, true);
            break;

        case 6:
            match = only_uppercase(local_addr_b58, local_addr_b58_len);
            break;

        case 7:
            match = only_lowercase(local_addr_b58, local_addr_b58_len);
            break;

        case 8:
            match = only_digits(local_addr_b58, local_addr_b58_len);
            break;

        case 9:
            match = only_digits_upper(local_addr_b58, local_addr_b58_len);
            break;

        case 10:
            match = only_digits_lower(local_addr_b58, local_addr_b58_len);
            break;

        case 11:
            match = only_letters(local_addr_b58, local_addr_b58_len);
            break;

        default:
            return;
    }

    if (match) {
        uint idx = atomic_inc(result_count);
        if (idx < 1024) {  // Safety limit
                           // Write ONLY the 64-byte private key (seed || pubkey)
#pragma unroll
            for (int i = 0; i < 64; i++) {
                results[(idx * 64) + i] = local_private_key[i];
            }
        }
    }
}
