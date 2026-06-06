# Kairos Entanglement Cipher (KEC)

A "time-entangled" symmetric cipher.

Each encryption is cryptographically unique due to high-precision timestamp integration and chaotic dynamics derived from the exact moment of encryption. This is not the best option by any metric, but it was fun!

Check out my [Medium blog](https://medium.com/@edgarhuemac/cryptographic-experiments-no-1-time-as-cryptography-itself-2da22f1b678a) for more.

---

## Overview

KEC combines:
- High-precision temporal seeding
- Lorenz attractor-based chaotic sequences
- Dynamic S-boxes, permutations, and round keys
- Variable time-influenced rounds
- Temporal entanglement folds

**Status**: Educational prototype / Proof of concept. Not audited or recommended for production use.

---

## Features

- Time as a core cryptographic primitive
- Strong avalanche effect through chaotic sensitivity
- Reversible dynamic substitution-permutation network
- Simple timestamp authentication
- Pure Python 3 implementation (no external dependencies)

---

## Installation

```bash
git clone https://github.com/yourusername/kairos-entanglement-cipher.git
cd kairos-entanglement-cipher
```

No additional packages required.


## Usage

```python
from kairos_entanglement_cipher import KairosEntanglementCipher

key = b"your-256-bit-or-longer-secret-key-here..."
cipher = KairosEntanglementCipher(key)

message = b"Secret message that will be time-bound..."

# Encrypt
ciphertext, header = cipher.encrypt(message)

# Decrypt
decrypted = cipher.decrypt(ciphertext, header)

print(decrypted == message)  # True
```

## Important note

This cipher is a creative experiment exploring time-based entropy and chaotic systems. It has not undergone formal cryptanalysis. Use it for research, learning, artistic, or anything except production-ready purposes.
