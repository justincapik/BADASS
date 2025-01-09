sudo apt update
sudo apt install -y busybox-static libpcap-dev xterm pipx python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebsockets python3-pyqt5.qtsvg qemu-kvm qemu-utils libvirt-clients libvirt-daemon-system virtinst software-properties-common ca-certificates curl gnupg2 
pipx install gns3-server==2.2.52
pipx install gns3-gui==2.2.52
pipx inject gns3-gui gns3-server PyQt5

sudo apt install cmake libpcap-dev libelf-dev git
git clone https://github.com/GNS3/dynamips.git ~/installs/dynamips
cd ~/installs/dynamips
mkdir build
cd build
cmake ..
make
sudo make install


#setup gns3-server api (disable http://localhost:3080 authentification)
sed -i 's/^auth = True/auth = False/' "$(echo $HOME)/.config/GNS3/2.2/gns3_server.conf"

echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.zshrc
echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc
