import hashlib
import time
from typing import Tuple, List, Optional

class KairosEntanglementCipher:
    """
    Kairos Entanglement Cipher (KEC) - Time-entangled hybrid chaotic cipher.
    Sophisticated prototype. Not for production use without further analysis!
    """
    
    def __init__(self, master_key: bytes, block_size: int = 16):
        self.master_key = master_key
        self.block_size = block_size
        self.base_rounds = 16
    
    def _get_high_precision_timestamp(self) -> bytes:
        ts = time.time_ns()
        fractional = int((time.perf_counter_ns() % 1000000) * 1e6)
        return ts.to_bytes(8, 'big') + fractional.to_bytes(8, 'big')
    
    def _temporal_seed(self, timestamp: bytes, nonce: Optional[bytes] = None) -> bytes:
        data = self.master_key + timestamp
        if nonce:
            data += nonce
        return hashlib.sha512(data).digest()
    
    def _lorenz_chaotic_sequence(self, seed: bytes, length: int, dt: float = 0.01) -> List[float]:
        s = int.from_bytes(seed[:8], 'big') / (2**64)
        x = 0.1 + s * 0.8
        y = 0.2 + (int.from_bytes(seed[8:16], 'big') / (2**64)) * 0.8
        z = 20.0 + (int.from_bytes(seed[16:24], 'big') / (2**64)) * 10.0
        
        sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
        sequence = []
        for _ in range(length):
            dx = sigma * (y - x) * dt
            dy = (x * (rho - z) - y) * dt
            dz = (x * y - beta * z) * dt
            x += dx; y += dy; z += dz
            sequence.append(x % 1.0)
        return sequence
    
    def _generate_dynamic_sbox(self, chaotic_seq: List[float]) -> List[int]:
        sbox = list(range(256))
        for i in range(256):
            idx = int(chaotic_seq[i % len(chaotic_seq)] * 256) % 256
            sbox[i], sbox[idx] = sbox[idx], sbox[i]
        return sbox
    
    def _generate_permutation(self, chaotic_seq: List[float], size: int) -> List[int]:
        perm = list(range(size))
        for i in range(size):
            idx = int(chaotic_seq[i % len(chaotic_seq)] * size) % size
            perm[i], perm[idx] = perm[idx], perm[i]
        return perm
    
    def _chaotic_round_key(self, chaotic_seq: List[float], round_num: int, key_len: int = 16) -> bytes:
        start = (round_num * key_len) % len(chaotic_seq)
        vals = [int(chaotic_seq[(start + i) % len(chaotic_seq)] * 256) for i in range(key_len)]
        return bytes(vals)
    
    def encrypt(self, plaintext: bytes, nonce: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        timestamp = self._get_high_precision_timestamp()
        seed = self._temporal_seed(timestamp, nonce)
        
        seq_len = max(1024, len(plaintext) * 4)
        chaotic_seq = self._lorenz_chaotic_sequence(seed, seq_len)
        
        t_mod = int.from_bytes(timestamp[:4], 'big') % 8
        rounds = self.base_rounds + t_mod
        
        padded = self._pkcs7_pad(plaintext)
        blocks = [padded[i:i+self.block_size] for i in range(0, len(padded), self.block_size)]
        
        ciphertext_blocks = []
        for block in blocks:
            state = list(block)
            # Initial whitening
            rk0 = self._chaotic_round_key(chaotic_seq, 0)
            state = [(state[i] ^ rk0[i % len(rk0)]) for i in range(len(state))]
            
            sbox = self._generate_dynamic_sbox(chaotic_seq)
            perm = self._generate_permutation(chaotic_seq, self.block_size)
            
            for r in range(rounds):
                state = [sbox[b] for b in state]  # Sub
                for i in range(len(state)):       # Diffusion
                    state[i] = (state[i] + int(chaotic_seq[(r * len(state) + i) % len(chaotic_seq)] * 256)) % 256
                state = [state[perm[i]] for i in range(len(state))]  # Perm
                rk = self._chaotic_round_key(chaotic_seq, r + 1)
                state = [(state[i] ^ rk[i % len(rk)]) for i in range(len(state))]  # Key add
                
                # Temporal entanglement
                ts_slice = int.from_bytes(timestamp[(r % len(timestamp)):(r % len(timestamp))+2], 'big') % 256
                state[0] = (state[0] ^ ts_slice) % 256
            
            ciphertext_blocks.append(bytes(state))
        
        ciphertext = b''.join(ciphertext_blocks)
        header = self._auth_timestamp(timestamp)
        return ciphertext, header + timestamp
    
    def decrypt(self, ciphertext: bytes, timestamp_header: bytes, nonce: Optional[bytes] = None) -> bytes:
        timestamp = timestamp_header[-16:]
        seed = self._temporal_seed(timestamp, nonce)
        
        seq_len = max(1024, len(ciphertext) * 4)
        chaotic_seq = self._lorenz_chaotic_sequence(seed, seq_len)
        
        t_mod = int.from_bytes(timestamp[:4], 'big') % 8
        rounds = self.base_rounds + t_mod
        
        blocks = [ciphertext[i:i+self.block_size] for i in range(0, len(ciphertext), self.block_size)]
        
        plaintext_blocks = []
        for block in blocks:
            state = list(block)
            sbox = self._generate_dynamic_sbox(chaotic_seq)
            perm = self._generate_permutation(chaotic_seq, self.block_size)
            
            for r in range(rounds - 1, -1, -1):
                # Inverse temporal
                ts_slice = int.from_bytes(timestamp[(r % len(timestamp)):(r % len(timestamp))+2], 'big') % 256
                state[0] = (state[0] ^ ts_slice) % 256
                
                rk = self._chaotic_round_key(chaotic_seq, r + 1)
                state = [(state[i] ^ rk[i % len(rk)]) for i in range(len(state))]
                
                inv_perm = [0] * len(perm)
                for i, p in enumerate(perm):
                    inv_perm[p] = i
                state = [state[inv_perm[i]] for i in range(len(state))]
                
                for i in range(len(state)):
                    state[i] = (state[i] - int(chaotic_seq[(r * len(state) + i) % len(chaotic_seq)] * 256)) % 256
                
                inv_sbox = [0] * 256
                for i, v in enumerate(sbox):
                    inv_sbox[v] = i
                state = [inv_sbox[b] for b in state]
            
            # Inverse whitening
            rk0 = self._chaotic_round_key(chaotic_seq, 0)
            state = [(state[i] ^ rk0[i % len(rk0)]) for i in range(len(state))]
            
            plaintext_blocks.append(bytes(state))
        
        return self._pkcs7_unpad(b''.join(plaintext_blocks))
    
    def _pkcs7_pad(self, data: bytes) -> bytes:
        padding_len = self.block_size - (len(data) % self.block_size) or self.block_size
        return data + bytes([padding_len] * padding_len)
    
    def _pkcs7_unpad(self, data: bytes) -> bytes:
        padding_len = data[-1]
        if padding_len > len(data) or padding_len == 0:
            raise ValueError("Invalid padding")
        return data[:-padding_len]
    
    def _auth_timestamp(self, timestamp: bytes) -> bytes:
        return hashlib.sha256(self.master_key + timestamp).digest()[:8]

# === Demo ===
if __name__ == "__main__":
    key = b"supersecretkey123supersecretkey123"
    cipher = KairosEntanglementCipher(key)
    
    message = b"Testing the Kairos Entanglement Cipher - Time makes each encryption unique!" * 3
    print("Original:", message[:80])
    
    ct, header = cipher.encrypt(message)
    print(f"Ciphertext length: {len(ct)} bytes | Rounds influenced by time")
    
    decrypted = cipher.decrypt(ct, header)
    print("Decryption successful:", decrypted == message)