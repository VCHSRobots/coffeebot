Install the sweep-sdk python package from [https://github.com/scanse/sweep-sdk]
```bash
git clone --depth=1 https://github.com/scanse/sweep-sdk
cd sweep-sdk/
cd libsweep/
sudo apt-get install cmake

cat << EOF > build.sh
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
sudo cmake --build . --target install
sudo ldconfig
EOF

sh build.sh
cd ../sweeppy/
python3 setup.py install
cd ../..
python3 test.py
```
