project('dpdk-runtime-learning', 'c',
  default_options: ['c_std=gnu11', 'warning_level=2'])
dpdk = dependency('libdpdk', method: 'pkg-config')
executable('basicfwd', 'basicfwd.c', dependencies: dpdk,
  c_args: ['-DALLOW_EXPERIMENTAL_API'])
