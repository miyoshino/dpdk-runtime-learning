import argparse
import struct
import sys


def read_packets(path):
    packets = []
    with open(path, 'rb') as f:
        header = f.read(24)
        if len(header) != 24:
            raise ValueError(f'{path}: PCAPヘッダーが途中で切れています')
        endian = {
            b'\xd4\xc3\xb2\xa1': '<',
            b'\xa1\xb2\xc3\xd4': '>',
            b'\x4d\x3c\xb2\xa1': '<',
            b'\xa1\xb2\x3c\x4d': '>',
        }.get(header[:4])
        if endian is None:
            raise ValueError(f'{path}: 未対応の形式です（classic PCAPが必要です）')
        _, major, minor, _, _, snaplen, network = struct.unpack(endian + 'IHHIIII', header)
        if (major, minor) != (2, 4) or network != 1:
            raise ValueError(f'{path}: EthernetのPCAP 2.4が必要です')
        while True:
            record = f.read(16)
            if not record:
                break
            if len(record) != 16:
                raise ValueError(f'{path}: パケット記録ヘッダーが途中で切れています')
            _, _, size, original_size = struct.unpack(endian + 'IIII', record)
            if size > snaplen or size != original_size:
                raise ValueError(f'{path}: 切り詰められた、または不正なパケットです')
            packet = f.read(size)
            if len(packet) != size:
                raise ValueError(f'{path}: パケットデータが途中で切れています')
            packets.append(packet)
    return packets


def main():
    # ファイル名指定
    parser = argparse.ArgumentParser(description='全パケットの宛先MAC変更と、それ以外の一致を確認します')
    parser.add_argument('input', nargs='?', default='input.pcap')
    parser.add_argument('output', nargs='?', default='output.pcap')

    # パケットの読み込みと比較
    args = parser.parse_args()
    src = read_packets(args.input)
    dst = read_packets(args.output)
    print(f'入力: {len(src)} packets')
    print(f'出力: {len(dst)} packets')
    ok = bool(src) and len(src) == len(dst)
    if not src:
        print('FAIL: 入力パケットがありません')
    if len(src) != len(dst):
        print('FAIL: パケット数が一致しません')
    expected_mac = bytes.fromhex('02 00 00 00 00 99')
    for i, (before, after) in enumerate(zip(src, dst), 1):
        # 今回の課題では、Ethernetヘッダーを持つパケットを確認します。
        valid = len(before) >= 14 and len(after) >= 14
        mac_ok = valid and after[:6] == expected_mac
        rest_ok = valid and before[6:] == after[6:]
        passed = mac_ok and rest_ok
        ok = ok and passed
        print(f'Packet {i}: {"PASS" if passed else "FAIL"}, '
              f'length={len(before)} -> {len(after)}, '
              f'DST={after[:6].hex(":")}, '
              f'宛先MAC={mac_ok}, その他一致={rest_ok}')
    print('結果:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
