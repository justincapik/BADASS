apk add iproute2
alias ip=/sbin/ip

ip link add br0 type bridge
ip link set dev br0 up
ip addr add 10.1.1.3/24 dev eth0
ip link add name vxlan20 type vxlan id 20 dev eth0 group 239.1.1.1 dstport 4789
ip addr add 20.1.1.3/24 dev vxlan10
brctl addif br0 eth1
brctl addif br0 vxlan20
ip link set dev vxlan20 up

ip -d link show vxlan20

bridge fdb show
