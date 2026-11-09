# DPDK runtime learning

NetBlocksにDPDK runtimeを追加するための学習用リポジトリです。
DPDK公式skeletonを基に、受信・ヘッダー解析・宛先MAC変更・転送とPCAPによる検証を学びます。
NetBlocksへの組み込みはまだ行っていません。

## 環境

確認環境はWSL2、Ubuntu 22.04、DPDK 21.11.9です。
実NIC、HugePages、root権限を使わず仮想PMDで実行します。

```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libdpdk-dev dpdk-dev \
  libpcap-dev libnuma-dev meson ninja-build python3
pkg-config --modversion libdpdk
```

## ビルド

このディレクトリで実行します。インストール済みDPDKを使用します。

```bash
make
```

独立したMeson設定も用意しています。こちらを使う場合：

```bash
meson setup build-meson
meson compile -C build-meson
```

以下の`./build/basicfwd`を`./build-meson/basicfwd`に置き換えてください。

## PCAPで再現する

```bash
python3 create_pcap.py
./build/basicfwd -l 0 --no-huge --no-pci --no-shconf -m 256 \
  --vdev='net_pcap0,rx_pcap=input.pcap' \
  --vdev='net_pcap1,tx_pcap=output.pcap'
```

入力の64バイトEthernetフレーム3個をポート0で受信し、宛先MACを
`02:00:00:00:00:99`に変更してポート1から出力します。
RX/TX累計が3になるのを確認し、Ctrl+Cで終了します。
実行はbusy pollingのため、待機中もCPUを使用します。
入力・出力PCAPは再実行時に上書きされます。

```bash
python3 check_pcap.py
```

パケット数、各パケットの宛先MAC、それ以外の全バイトが入力と同じかを確認します。
全3件と最終結果がPASSなら成功です。失敗時は終了コード1を返します。
マイクロ秒／ナノ秒、両バイトオーダーのclassic PCAPに対応しています。
比較は記録順です。PCAPNG、切り詰めたパケット、Ethernet以外は対象外です。

## null PMDで動かす

```bash
./build/basicfwd -l 0 --no-huge --no-pci --no-shconf -m 256 \
  --vdev=net_null0 --vdev=net_null1
```

null PMDはダミーパケットを供給し、送信されたパケットを破棄します。
仮想ポートはプロセス内にあり、`ip link`には表示されません。
表示される件数は実NICの通信性能を意味しません。

## 学習したこと

1. testpmdでEAL・mempool・仮想ポート・送受信を確認。
2. skeletonの`main()`、`port_init()`、`lcore_main()`を読む。
3. RX/TX累計を保持し、タイマーカウンターの差分で約1秒ごとに表示。
4. mbufの`pkt_len`（全体）と`data_len`（セグメント）の違いを理解。
5. 先頭のバイト列を長さ制限付きで16進数表示する練習。
6. PCAPから既知のパケットを受信し、転送後のデータと比較。
7. Ethernetヘッダーとバイトオーダー、構造体・ポインタ・`&`を学ぶ。
8. burst内の全パケットの宛先MACを書き換え、全件を検証。

履歴上の各段階を復元したものではなく、現在の最終コードと学習内容をまとめています。

## コードを読む順序と注意点

- `basicfwd.c`: 初期化→ポート設定→burst受信→各パケットの変更→burst送信。
- `create_pcap.py`: Python標準ライブラリのみでテスト入力を作成。
- `check_pcap.py`: 全件の内容を検証。

最初のセグメントにEthernetヘッダーが収まる場合だけ変更します。
短いパケットやセグメント境界をまたぐヘッダーは、そのまま転送します。
送信が受け付けられたmbufはドライバへ管理を移し、未送信mbufだけを解放します。
サンプルは無限ループで、Ctrl+Cによる終了処理の整備は今後の課題です。
デバッグ用ヘッダー表示は各パケットで行うため、性能測定には適しません。

次はNetBlocksの`nb__poll_packet()`と`nb__send_packet()`の契約、
headroomとバッファの所有権を整理し、コピーありのtransportを設計します。

## 出典・ライセンス

`basicfwd.c`と`Makefile`はDPDK v21.11の公式skeletonを基にしています。
元の著作権表示とBSD-3-Clauseライセンスを保持しています（`LICENSE`参照）。
本リポジトリの追加コードもBSD-3-Clauseで提供します。

- https://github.com/DPDK/dpdk/tree/v21.11/examples/skeleton
- https://doc.dpdk.org/guides-21.11/sample_app_ug/skeleton.html
- https://doc.dpdk.org/guides-21.11/nics/pcap_ring.html
