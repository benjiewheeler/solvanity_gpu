# GPU Solvanity

Yet another vanity address generator, now with OpenCL

## Motivation

I discovered Wincerchan's [SolvanityCL](https://github.com/WincerChan/SolVanityCL) project and began experimenting with generating addresses on the GPU. As I explored this I wanted more features beyond just prefix and suffix options. This also sparked my interest in GPU programming, which is a novel concept for me, so what better way to do that than by creating yet another vanity address generator?

## Usage

#### Requirements

- A GPU with OpenCL support. (with drivers installed)
- Python 3.10+

```
Usage: python main.py grind [OPTIONS]

Options:
  -m,  --mode             INTEGER  Key matching method
  -w,  --word             TEXT     Prefix/Suffix to match
  -l,  --length           INTEGER  Number of repeating characters to match
  -L,  --limit            INTEGER  Number of matching keys to find  [default: 1]
  -O,  --output-dir       TEXT     Output directory  [default: ./keys]
  -gs, --global-work-size INTEGER  Number of work-items to launch  [default: 65536]
  -ls, --local-work-size  INTEGER  Number of threads per work-item  [default: 32]

Modes:
   0 = Match keys starting with word
   1 = Match keys starting with word (case insensitive)
   2 = Match keys ending with word
   3 = Match keys ending with word (case insensitive)
   4 = Match keys starting or ending with word
   5 = Match keys starting or ending with word (case insensitive)
   6 = Match keys containing only uppercase letters
   7 = Match keys containing only lowercase letters
   8 = Match keys containing only digits
   9 = Match keys containing only uppercase letters and digits
  10 = Match keys containing only lowercase letters and digits
  11 = Match keys containing only letters
  12 = Match keys starting with repeating characters
  13 = Match keys starting with repeating characters (case insensitive)
  14 = Match keys ending with repeating characters
  15 = Match keys ending with repeating characters (case insensitive)
  16 = Match keys starting or ending with repeating characters
  17 = Match keys starting or ending with repeating characters (case insensitive)
```

## Performance

I tested this on a selection of GPUs, my own and from [Vast.ai](https://vast.ai/). The results are as follows:

| Card                                              |        Rate |
| :------------------------------------------------ | ----------: |
| AMD Ryzen 5 9600X (iGPU)                          |  ~0.69 MH/s |
| AMD Radeon RX 7600                                | ~11.93 MH/s |
| NVIDIA GeForce GTX 1080                           |  ~1.77 MH/s |
| NVIDIA GeForce RTX 5070                           | ~28.11 MH/s |
| NVIDIA GeForce RTX 5090                           | ~87.59 MH/s |
| NVIDIA RTX PRO 6000 Blackwell Workstation Edition | ~98.32 MH/s |

\*_I'm unsure about the accuracy of the result of the NVIDIA GeForce GTX 1080, it is an older card (almost 10 years old at the time of writing) but the result seems lower than expected_

## Similar projects

- The official [Solana CLI](https://solana.com/docs/intro/installation#install-the-solana-cli) offers a `solana-keygen grind` command that allows generating vanity addresses, works on the CPU.
- Wincerchan's [SolvanityCL](https://github.com/WincerChan/SolVanityCL), The main inspiration for this project, supports prefix and suffix options, and has multi-GPU support.

## Acknowledgements

- This project is **heavily** inspired by Wincerchan's [SolvanityCL](https://github.com/WincerChan/SolVanityCL) project and its accompanying blog posts [Generating Solana Vanity Addresses Using OpenCL](https://blog.itswincer.com/posts/solana-vanity-prefix-vs-suffix-probability-en) and [Solana Address Prefix Character Probability Analysis](https://blog.itswincer.com/posts/solana-vanity-prefix-vs-suffix-probability-en)
- The C implementation of base58 was adapted from [chaika2013/base58](https://github.com/chaika2013/base58)
- The C implementation of ed25519 was adapted from [orlp/ed25519](https://github.com/orlp/ed25519)

## Shameless plug

Since you're here, you're probably interested in Solana; if so, check out my other Solana-related projects:

- **[solvanity_rs](https://github.com/benjiewheeler/rust_journey/tree/master/solvanity_rs)**: Rust based vanity address generator with regex support
- **[memobench](https://github.com/benjiewheeler/memobench)**: Tool for benchmarking Solana RPC nodes
- **[yellowbench](https://github.com/benjiewheeler/yellowbench)**: Tool for benchmarking Solana Yellowstone Geyser

You like these projects, consider buying me a coffee :coffee: _(or a pizza :pizza: or maybe some cake :cake:)_ [_`CoffeeFpEteoCSPgHeoj98Sb6LCzoG36PGdRbYwqSvLd`_](https://solscan.io/address/CoffeeFpEteoCSPgHeoj98Sb6LCzoG36PGdRbYwqSvLd)

_or hire me_ ;)

[![Protonmail Badge](https://img.shields.io/static/v1?message=Email&label=ProtonMail&style=flat&logo=protonmail&color=6d4aff&logoColor=white)](mailto:benjiewheeler@protonmail.com)
[![Discord Badge](https://img.shields.io/static/v1?message=Discord&label=benjie_wh&style=flat&logo=discord&color=5865f2&logoColor=5865f2)](https://discordapp.com/users/789556474002014219)
[![Telegram Badge](https://img.shields.io/static/v1?message=Telegram&label=benjie_wh&style=flat&logo=telegram&color=229ED9)](https://t.me/benjie_wh)
[![X Badge](https://img.shields.io/static/v1?message=Twitter&label=benjie_wh&style=flat&logo=x&color=000000)](https://x.com/benjie_wh)

## Disclaimer

**USE WITH CAUTION AND UNDERSTANDING**

This Solana vanity address generator has been created mainly for learning purposes and for personal use. It is made available as open-source for contributing to the wider Solana community. However, it is **not audited** and is **not guaranteed** to be cryptographically secure. Security is provided on a best-effort basis, utilizing sources like `os.urandom`, but no guarantees are made regarding its effectiveness.
