DPDK公式skeletonを基に、受信・ヘッダー解析・宛先MAC変更・転送を行うリポジトリ

環境:WSL2, Ubuntu 22.04, DPDK 21.11.9

```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libdpdk-dev dpdk-dev \
  libpcap-dev libnuma-dev meson ninja-build python3
pkg-config --modversion libdpdk
```

ビルド
```bash
# インストール済みDPDKを使用
# build output: ./build/basicfwd
make 
```

```bash
# Mesonを利用
# build output: ./build-meson/basicfwd
meson setup build-meson
meson compile -C build-meson
```

PCAPの利用方法
```bash
python3 create_pcap.py
./build/basicfwd -l 0 --no-huge --no-pci --no-shconf -m 256 \
  --vdev='net_pcap0,rx_pcap=input.pcap' \
  --vdev='net_pcap1,tx_pcap=output.pcap'
```

```bash
python3 check_pcap.py
```

null PMDで動かす方法

```bash
./build/basicfwd -l 0 --no-huge --no-pci --no-shconf -m 256 \
  --vdev=net_null0 --vdev=net_null1 # null PMDはダミーパケットを供給、送信されたパケットを破棄
```

出典・ライセンス

`basicfwd.c`と`Makefile`はDPDK v21.11の公式skeletonを基にしています
元の著作権表示とBSD-3-Clauseライセンスを保持しています（`LICENSE`参照）

- https://github.com/DPDK/dpdk/tree/v21.11/examples/skeleton
- https://doc.dpdk.org/guides-21.11/sample_app_ug/skeleton.html
- https://doc.dpdk.org/guides-21.11/nics/pcap_ring.html
