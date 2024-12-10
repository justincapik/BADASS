sudo apt update
sudo apt install -y pipx python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebsockets python3-pyqt5.qtsvg qemu-kvm qemu-utils libvirt-clients libvirt-daemon-system virtinst software-properties-common ca-certificates curl gnupg2 
pipx install gns3-server
pipx install gns3-gui
pipx inject gns3-gui gns3-server PyQt5