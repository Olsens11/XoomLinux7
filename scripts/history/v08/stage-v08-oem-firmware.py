from pathlib import Path
from hashlib import sha256
B=Path('/home/xoomdev/xoom-linux-rom')
src=Path('/mnt/c/Users/olsen/XoomLinux/Phase1/fw_bcmdhd-recovery-reference-private.bin')
fw=src.read_bytes()
assert len(fw)==264140 and sha256(fw).hexdigest()=='5d4bdb6c56777e4a1eb27b08600a2782a76b563891dfd18afc163c8462d73834'
br=B/'firmware-reference-v08-OEM-MZ600-private'/'brcm'
br.mkdir(parents=True,exist_ok=True)
(br/'brcmfmac4329-sdio.bin').write_bytes(fw)
board=(B/'firmware-reference-v07/brcm/brcmfmac4329-sdio.txt').read_bytes()
assert len(board)==1550 and sha256(board).hexdigest()=='a8715bb1ebe3c6e69c40781d58207326b71721dea4594acb8d37e935acef76cb'
assert b'macaddr=' not in board and b'ccode=' not in board and b'regrev=' not in board
(br/'brcmfmac4329-sdio.txt').write_bytes(board)
print('OEM FIRMWARE A/B REFERENCE STAGED', len(fw), sha256(fw).hexdigest())
print('Identical MAC-FREE board NVRAM',len(board),sha256(board).hexdigest())
