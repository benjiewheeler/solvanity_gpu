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

bool has_repeating_prefix(const char* addr, uint prefix_len, bool ignore_case) {
    if (prefix_len == 0)
        return true;

    uchar first_char = (uchar)addr[0];
    uchar first_char_lower = first_char >= 'A' && first_char <= 'Z' ? first_char + 32 : first_char;

    for (uint i = 1; i < prefix_len; i++) {
        uchar addr_c = (uchar)addr[i];

        if (ignore_case) {
            uchar addr_lower = (addr_c >= 'A' && addr_c <= 'Z') ? addr_c + 32 : addr_c;

            if (addr_lower != first_char_lower)
                return false;
        } else {
            if (addr_c != first_char)
                return false;
        }
    }

    return true;
}

bool has_repeating_suffix(const char* addr, uint addr_len, uint suffix_len, bool ignore_case) {
    if (suffix_len == 0)
        return true;

    uchar last_char = (uchar)addr[addr_len - 1];
    uchar last_char_lower = last_char >= 'A' && last_char <= 'Z' ? last_char + 32 : last_char;

    for (uint i = 1; i < suffix_len; i++) {
        uchar addr_c = (uchar)addr[addr_len - 1 - i];

        if (ignore_case) {
            uchar addr_lower = (addr_c >= 'A' && addr_c <= 'Z') ? addr_c + 32 : addr_c;

            if (addr_lower != last_char_lower)
                return false;
        } else {
            if (addr_c != last_char)
                return false;
        }
    }

    return true;
}
