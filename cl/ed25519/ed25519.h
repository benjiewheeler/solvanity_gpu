#ifndef ED25519_H
#define ED25519_H

#define ED25519_DECLSPEC

#ifdef __cplusplus
extern "C" {
#endif

void ED25519_DECLSPEC ed25519_create_keypair(unsigned char* public_key, unsigned char* private_key, const unsigned char* seed);

#ifdef __cplusplus
}
#endif

#endif
