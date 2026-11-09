import struct

# 宛先MAC・送信元MAC・実験用EtherType・50バイトのペイロード
packet = bytes.fromhex(
    "02 00 00 00 00 01 02 00 00 00 00 02 88 b5"
) + bytes(range(50))

with open("input.pcap", "wb") as f:
    f.write(struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
    for _ in range(3):
        f.write(struct.pack("<IIII", 0, 0, len(packet), len(packet)))
        f.write(packet)

print(f"Created input.pcap: 3 packets, {len(packet)} bytes each")
