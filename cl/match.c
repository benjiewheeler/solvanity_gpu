bool has_prefix(const char* addr, __constant uchar* prefix_chars, uint prefix_len, bool ignore_case) {
    if (prefix_len == 0)
        return true;

    for (uint i = 0; i < prefix_len; i++) {
        uchar addr_c = (uchar)addr[i];
        uchar prefix_c = prefix_chars[i];

        if (ignore_case) {
            uchar addr_lower = (addr_c >= 'A' && addr_c <= 'Z') ? addr_c + 32 : addr_c;
            uchar prefix_lower = (prefix_c >= 'A' && prefix_c <= 'Z') ? prefix_c + 32 : prefix_c;

            if (addr_lower != prefix_lower)
                return false;
        } else {
            if (addr_c != prefix_c)
                return false;
        }
    }

    return true;
}

bool has_suffix(const char* addr, uint addr_len, __constant uchar* suffix_chars, uint suffix_len, bool ignore_case) {
    if (suffix_len == 0)
        return true;

    for (uint i = 0; i < suffix_len; i++) {
        uchar addr_c = (uchar)addr[addr_len - 1 - i];
        uchar suffix_c = suffix_chars[suffix_len - 1 - i];

        if (ignore_case) {
            uchar addr_lower = (addr_c >= 'A' && addr_c <= 'Z') ? addr_c + 32 : addr_c;
            uchar suffix_lower = (suffix_c >= 'A' && suffix_c <= 'Z') ? suffix_c + 32 : suffix_c;

            if (addr_lower != suffix_lower)
                return false;
        } else {
            if (addr_c != suffix_c)
                return false;
        }
    }

    return true;
}

bool only_uppercase(const char* addr, uint addr_len) {
    for (uint i = 0; i < addr_len; i++) {
        uchar c = (uchar)addr[i];

        if (c < 'A' || c > 'Z')
            return false;
    }

    return true;
}

bool only_lowercase(const char* addr, uint addr_len) {
    for (uint i = 0; i < addr_len; i++) {
        uchar c = (uchar)addr[i];

        if (c < 'a' || c > 'z')
            return false;
    }

    return true;
}

bool only_digits(const char* addr, uint addr_len) {
    for (uint i = 0; i < addr_len; i++) {
        uchar c = (uchar)addr[i];

        if (c < '0' || c > '9')
            return false;
    }

    return true;
}

bool only_digits_upper(const char* addr, uint addr_len) {
    for (uint i = 0; i < addr_len; i++) {
        uchar c = (uchar)addr[i];

        if (!((c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z')))
            return false;
    }

    return true;
}

bool only_digits_lower(const char* addr, uint addr_len) {
    for (uint i = 0; i < addr_len; i++) {
        uchar c = (uchar)addr[i];

        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z')))
            return false;
    }

    return true;
}

bool only_letters(const char* addr, uint addr_len) {
    for (uint i = 0; i < addr_len; i++) {
        uchar c = (uchar)addr[i];

        if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')))
            return false;
    }

    return true;
}

