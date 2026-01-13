#ifndef FE_H
#define FE_H

#include "fixedint.h"

/*
    fe means field element.
    Here the field is \Z/(2^255-19).
    An element t, entries t[0]...t[9], represents the integer
    t[0]+2^26 t[1]+2^51 t[2]+2^77 t[3]+2^102 t[4]+...+2^230 t[9].
    Bounds on each t[i] vary depending on context.
*/

typedef int32_t fe[10];

void fe_0(__generic fe h);
void fe_1(__generic fe h);

void fe_frombytes(__generic fe h, const unsigned char* s);
void fe_tobytes(unsigned char* s, const __generic fe h);

void fe_copy(__generic fe h, const __generic fe f);
int fe_isnegative(const __generic fe f);
int fe_isnonzero(const __generic fe f);
void fe_cmov(__generic fe f, const __generic fe g, unsigned int b);
void fe_cswap(fe f, fe g, unsigned int b);

void fe_neg(__generic fe h, const __generic fe f);
void fe_add(__generic fe h, const __generic fe f, const __generic fe g);
void fe_invert(__generic fe out, const __generic fe z);
void fe_sq(__generic fe h, const __generic fe f);
void fe_sq2(__generic fe h, const __generic fe f);
void fe_mul(__generic fe h, const __generic fe f, const __generic fe g);
void fe_mul121666(fe h, fe f);
void fe_pow22523(__generic fe out, const __generic fe z);
void fe_sub(__generic fe h, const __generic fe f, const __generic fe g);

#endif
