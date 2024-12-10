sudo apt install git build-essential
git clone https://github.com/GNS3/ubridge.git
cd ubridge
make
sudo make install

cd ../
rm -rf ubridge