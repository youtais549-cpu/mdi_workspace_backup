mkdir lammps_test
cd lammps_test
code .
lmp-in in.lj
/usr/bin/python3 /home/yamazaki_yuta/reserach/test
lmp -in in.lj
cd /home/yamazaki_yuta/.vscode-server/lammps_test
lmp -in in.lj
cd /home/yamazaki_yuta/reserach
lmp -help | grep REAXFF
sudo apt update
sudo apt install build-essential cmake git libfftw3-dev
cd /home/yamazaki_yuta
git clone -b stable https://github.com/lammps/lammps.git lammps_src
cd lammps_src
# ビルド用のフォルダを作成
mkdir build
cd build
cmake -D PKG_REAXFF=yes -D PKG_MOLECULE=yes -D PKG_RIGID=yes ../cmake
cd /home/yamazaki_yuta
sudo apt update
sudo apt install libopenmpi-dev
cd /home/yamazaki_yuta/lammps_src/build
# 現在のフォルダ（build）にいることを確認して実行
rm -rf *
cmake -D PKG_REAXFF=yes -D PKG_MOLECULE=yes -D PKG_RIGID=yes ../cmake
make -j4
sudo make install
lmp -help | grep REAXFF
cd ~/lammps_src/build
# フォルダ内を空にする（非常に重要です！）
rm -rf *
cmake -D PKG_REAXFF=yes -D PKG_MOLECULE=yes -D PKG_RIGID=yes ../cmake
make -j4
make install
./lmp -help | grep REAXFF
find ~/lammps_src -name "ffield.reax"
cd /home/yamazaki_yuta
成
mkdir research_simulations
cd research_simulation
mkdir lammps_simulation
cd lammps_simulation
cd /home/yamazaki_yuta/research_simulations
cd /home/yamazaki_yuta/lammps_build
cd research_simulations
cd /home/yamazaki_yuta/research_simulations
cp ~/lammps_src/examples/reaxff/ffield.reax ~/research_simulations/
# Atomskを使ってSiO2(Quartz)のデータを生成するコマンド例
atomsk --create quartz 4.91 5.40 alpha_quartz.xsf
# これをLAMMPS形式に変換する
atomsk alpha_quartz.xsf lammps
# Windowsのユーザー名が「yamazaki」の場合の例
mv /mnt/c/Users/yamazaki yuta/Downloads/atomsk-linux-64-bit ~/research_simulations/atomsk
mv /mnt/c/Users/yamazaki\ yuta/Downloads/atomsk_b0.13.1_Linux-amd64.tar.gz ~/research_simulations/atomsk
file atomsk
# 今ある atomsk という名前のファイルを atomsk.tar.gz に変更します
mv atomsk atomsk.tar.gz
tar -xvf atomsk.tar.gz
ls
cd /home/yamazaki_yuta/research_simulations/atomsk.tar.gz
/home/yamazaki_yuta/research_simulations/atomsz
cd /home/yamazaki_yuta/research_simulations/atomsk
./atomsk
./atomsk.tar.gz
cd atomsk_b0.13.1_Linux-amd64
ls
chmod +x atomsk
./atomsk
pwd
cd ..
ls
./atomsk_b0.13.1_Linux-amd64/atomsk --create quartz 4.91 5.40 sio2.cfg
./atomsk_b0.13.1_Linux-amd64/atomsk sio2.cfg lammps
rm -f sio2.cfg sio2.lmp
./atomsk_b0.13.1_Linux-amd64/atomsk --create quartz 4.91 5.40 sio2.cfg
~/lammps_src/build/lmp -in in.sio2
head -n 5 ffield.reax
cd /home/yamazaki_yuta
sudo apt update
sudo apt install build-essential libx11-dev libxt-dev libxmu-dev libxi-dev freeglut3-dev
# ホームディレクトリにCoという作業用フォルダを作成し、その中に必要な構造を作る
mkdir -p ~/Co/linuxLib
mkdir -p ~/Co/linuxBin
mkdir -p ~/Co/Include
mkdir -p ~/Co/Man
# ホームディレクトリにCoという作業用フォルダを作成し、その中に必要な構造を作る
mkdir -p ~/Co/linuxLib
mkdir -p ~/Co/linuxBin
mkdir -p ~/Co/Include
mkdir -p ~/Co/Man
# 環境変数をbash用に設定
export hosttype="linux"
export SYS="linux"
export LIB_PATH="$HOME/Co/${hosttype}Lib"
export BIN_PATH="$HOME/Co/${hosttype}Bin"
export INC_PATH="$HOME/Co/Include"
export MAN_PATH="$HOME/Co/Man"
# パスが正しく設定されたか確認（必要なら）
echo $LIB_PATH
sudo apt update
sudo apt install lammps
lmp-help
lmp help
lammps-help
make yes-REAXFF
make mpi
sudo apt install make
make yes-REAXFF
cd /home/yamazaki_yuta/Src-20101019
# 環境変数をbash用に設定
export hosttype="linux"
export SYS="linux"
export LIB_PATH="$HOME/Co/${hosttype}Lib"
export BIN_PATH="$HOME/Co/${hosttype}Bin"
export INC_PATH="$HOME/Co/Include"
export MAN_PATH="$HOME/Co/Man"
# パスが正しく設定されたか確認（必要なら）
echo $LIB_PATH
# 例：最初のいくつかのディレクトリでビルドを実行
cd Timer
make
cd ../IO
make
cd ../Scalar
make
# ... この要領で順番にコンパイルしていきます
make
ls IO/IO.h
cd Timer && make && cp *.h ../../Co/Include/ && cp *.o ../../Co/linuxLib/ && cd ..
cd ..
cd Timer && make && cp *.h ../../Co/Include/ && cp *.o ../../Co/linuxLib/ && cd ..
cd IO && make && cp *.h ../../Co/Include/ && cp *.o ../../Co/linuxLib/ && cd ..
cd ..
sudo apt update
sudo apt install libreadline-dev
cd IO && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd Scalar && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd ..
cd Scalar && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd ..
sudo apt update
sudo apt install libgsl-dev
cd ~/Src-20101019
cd Scalar && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd VecMat && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd ..
cd VecMat && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd ..
cd VecMat && make && cp *.h ../Co/Include/ && cp *.o ../Co/linuxLib/ && cd ..
cd ..
# VecMat は既に make が通っているようなので、コピーだけ修正して実行し、次に進みます
cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd /home/yamazaki_yuta/Src-20101019/VecMat
# VecMat は既に make が通っているようなので、コピーだけ修正して実行し、次に進みます
cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd VecMat2 && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd VecMat3 && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd Min && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd Atoms && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd AX && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd ..
sudo apt update
sudo apt install libxpm-dev
cd AX && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd ..
sudo apt install libpng-dev
cd AX && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
sudo apt install libjpeg-dev
cd ..
cd AX && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd ..
cd AX && make && cp *.h $HOME/Co/Include/ && cp *.o $HOME/Co/linuxLib/ && cd ..
cd A && make && cd ..
cd ..
sudo apt install zlib1g-dev
cd ~/Src-20101019/A && make
cd ..
cd ~/Src-20101019/A && make
cd ..
cd ~/Src-20101019/A
make CFLAGS+="-DZ_BEST_COMPRESSION=9"
rm *.o
make
cd ..
cd ~/Src-20101019/A
rm *.o
make
ls -l A
cd ..
cd ~/Src-20101019/A
rm *.o
make
ls -l A
cd ..
cd ~/Src-20101019/A
rm *.o
make
ls -l A
cd ..
sudo apt update
sudo apt install liblapack-dev libblas-dev
cd ~/Src-20101019/A
rm *.o
make
ls -l A
cd /home/yamazaki_yuta/reserach
gcc exampleLJ.c
./a.out
gcc exampleLJ.c -o simulation test -lm
gcc exampleLJ.c -lm
./
./a.out
set xlabel 'time[ps]'
set xlabel 'time[ps]' set ylabel 'energy[eV]' plot [][-20:10]'LJ.dat' u 1:2 w l t 'KE' ,\ 'LJ.dat' u 1:3 w l t 'PE',\ 'LJ.dat' u 1:4 w l t 'hamiltonian'
tar -xvf vmd-2.0.1a1.bin.LINUXAMD64.tar.gz  # ダウンロードしたファイルを解凍
cd vmd-2.0.1a1.bin.LINUXAMD64               # ディレクトリへ移動
tar -xvf vmd-2.0.1a1.bin.LINUXAMD64.tar.gz
cd ..
tar -xvf vmd-2.0.1a1.bin.LINUXAMD64.tar.gz
cd vmd-2.0.1a1.bin.LINUXAMD64
cd /home/yamazaki_yuta/vmd-2.0.1a1
./configure
cd src
sudo make install
vmd
lmp -in in.lj
vmd
cd /home/yamazaki_yuta/Atomeye
ls -l A
./A /home/yamazaki_yuta/reserach/LJ.xyz
./A Lj.xyz
file ./A
rm A
cd ~/Atomeye/A
ls -F
./A
rm A
nake
make
ls -l A
rm *.o
make
ls -l A
# ライブラリ用フォルダを作成
mkdir -p ~/Co/Lib
# 今ある .o ファイルをすべてそこに移動
cp ~/Co/linuxLib/*.o ~/Co/Lib/
cd ~/Co/Lib
# 以下のコマンドを順番に実行してライブラリファイルを作ります
ar rcs libAX.a AX.o
ar rcs libAtoms.a Atoms.o
ar rcs libVecMat3.a VecMat3.o
ar rcs libVecMat.a VecMat.o
ar rcs libIO.a IO.o
ar rcs libScalar.a Scalar.o
ar rcs libTimer.a Timer.o
cd ~/Atomeye/A
rm *.o
make
# 1. 念のため Lib フォルダへ移動
mkdir -p ~/Co/Lib
cd ~/Co/Lib
# 2. まだ足りないファイルを linuxLib から持ってくる
cp ~/Co/linuxLib/VecMat3.o .
cp ~/Co/linuxLib/VecMat.o .
cp ~/Co/linuxLib/IO.o .
cp ~/Co/linuxLib/Scalar.o .
# 3. 念のため、これまで作った他の .o も持ってくる（重複してもOKです）
cp ~/Co/linuxLib/*.o .
# まとめてライブラリを作成します
ar rcs libAX.a AX.o
ar rcs libAtoms.a Atoms.o
ar rcs libVecMat3.a VecMat3.o
ar rcs libVecMat.a VecMat.o
ar rcs libIO.a IO.o
ar rcs libScalar.a Scalar.o
ar rcs libTimer.a Timer.o
ar rcs libMin.a Min.o
cd ~/Atomeye/A
rm *.o
make
# ライブラリ用フォルダを準備
mkdir -p ~/Co/Lib
cd ~/Co/Lib
# linuxLibにある部品をすべてLibに持ってくる（これが抜けていました）
cp ~/Co/linuxLib/*.o .
# 部品を使ってライブラリファイル（.a）を作成
ar rcs libAX.a AX.o
ar rcs libAtoms.a Atoms.o
ar rcs libVecMat3.a VecMat3.o
ar rcs libVecMat.a VecMat.o
ar rcs libIO.a IO.o
ar rcs libScalar.a Scalar.o
ar rcs libTimer.a Timer.o
ar rcs libMin.a Min.o
# 確認：これらが表示されたら成功です！
ls -l lib*.a
cd ~/Atomeye/A
rm *.o
make
# 必要なディレクトリへ移動して再ビルド
cd ~/Src-20101019/VecMat && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Src-20101019/VecMat3 && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Src-20101019/IO && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Src-20101019/Scalar && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Atomeye/VecMat && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Atomeye/VecMat3 && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Atomeye/IO && make && cp *.o ~/Co/linuxLib/ && cd ..
cd ~/Atomeye/Scalar && make && cp *.o ~/Co/linuxLib/ && cd ..
# ライブラリ用フォルダを準備
mkdir -p ~/Co/Lib
cd ~/Co/Lib
# すべての部品をLibフォルダにコピー（上書き確認は y でOK）
cp ~/Co/linuxLib/*.o .
# ライブラリファイルを作成
ar rcs libAX.a AX.o
ar rcs libAtoms.a Atoms.o
ar rcs libVecMat3.a VecMat3.o
ar rcs libVecMat.a VecMat.o
ar rcs libIO.a IO.o
ar rcs libScalar.a Scalar.o
ar rcs libTimer.a Timer.o
ar rcs libMin.a Min.o
cd ~/Atomeye/A
rm *.o
make
cd /home/yamazaki_yuta/reserach
./exampleLJ.c
gcc exampleLJ.c -o exampleLJ -lm
./exampleLJ
vmd
cd ~/mdi_workspace/test_run
tail -f qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammp
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
# ホームディレクトリに移動
cd ~
# 今回の連携用ツールをまとめるフォルダ（例として mdi_workspace）を作成
mkdir mdi_workspace
# そのフォルダの中に移動
cd mdi_workspace
sudo apt update
sudo apt install -y build-essential cmake git mpi-default-dev mpi-default-bin gfortran libfftw3-dev liblapack-dev libblas-dev
cd ~
git clone -b stable https://github.com/lammps/lammps.git
cd lammps
t
# ホームディレクトリ（~）に移動
cd ~
# 今回の作業用フォルダを作成して、その中に移動
mkdir mdi_workspace
cd mdi_workspace
# --- これ以降は mdi_workspace 内部での作業になります ---
# LAMMPSのソースコードをダウンロード
git clone -b stable https://github.com/lammps/lammps.git
# ダウンロードした lammps フォルダに移動
cd lammps
# ビルド（コンパイル）用のディレクトリを作成して移動
mkdir build
cd build
# MDIパッケージとMPIを有効にしてCMakeで設定
cmake../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
# コンパイルの実行（-j 4 はパソコンの4コアを使って高速化する指示です）
make -j 4
cmake../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
Bash
cmake../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
cd ~
sudo apt update
sudo apt install -y build-essential cmake git mpi-default-dev mpi-default-bin gfortran libfftw3-dev liblapack-dev libblas-dev
# ==========================================
# 準備: 作業用フォルダ（mdi_workspace）の作成
# ==========================================
# ホームディレクトリに移動
cd ~
# mdi_workspace フォルダを作成して、その中に移動
mkdir -p mdi_workspace
cd mdi_workspace
# ==========================================
# ステップ3: LAMMPSのダウンロードとコンパイル
# ==========================================
# LAMMPSのソースコードをダウンロード
git clone -b stable https://github.com/lammps/lammps.git
# ダウンロードした lammps フォルダの中へ移動
cd lammps
# ビルド（コンパイル）用のディレクトリを作成して移動
mkdir build
cd build
# MDIパッケージとMPIを有効にしてCMakeで設定
# （※ cmake と../cmake の間に半角スペースがあります）
cmake../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
# コンパイルの実行（数分かかります）
make -j 4
# ==========================================
# ステップ4: Quantum ESPRESSOのダウンロードとコンパイル
# ==========================================
# もう一度 mdi_workspace ディレクトリに戻る
cd ~/mdi_workspace
# Quantum ESPRESSOのソースコードをダウンロード
git clone https://gitlab.com/QEF/q-e.git
# ダウンロードした q-e フォルダに移動
cd q-e
# MDIを有効にして設定を行う
./configure --with-mdi
# MD計算に必要な pw.x モジュールをコンパイル（数分かかります）
make pw -j 4
# テスト用フォルダの作成と移動
mkdir -p ~/mdi_workspace/test_run
cd ~/mdi_workspace/test_run
# SiとCの擬ポテンシャルファイルをダウンロード
wget https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-kjpaw_psl.1.0.0.UPF -O Si.upf
wget https://pseudopotentials.quantum-espresso.org/upf_files/C.pbe-n-kjpaw_psl.1.0.0.UPF -O C.upf
mkdir qe.in
cd ~/mdi_workspace/test_run
code qe.in
code in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/lammps/build
make -j 4
cmake../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
cmake ../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
make -j 4
ls ~/mdi_workspace/lammps/build/lmp
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/lammps/build
cmake ../cmake -D PKG_MDI=yes -D BUILD_MPI=yes
make -j 4
ls -l ~/mdi_workspace/lammps/build/lmp
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
code run.sh
chmod +x run.sh
code run.sh
chmod +x run.sh
cd /home/yamazaki_yuta/mdi_workspace
chmod +x run.sh
cd /home/yamazaki_yuta/mdi_workspace/test_run
chmod +x run.sh
./run.sh
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/lammps/build/lmp -mdi "-role DRIVER -name LAMMPS -method TCP -port 8021 -hostname localhost" -in in.lammps
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
~/mdi_workspace/q-e/bin/pw.x -mdi "-role ENGINE -name QE -method TCP -port 8021 -hostname localhost" -in qe.in > qe.out
cd ~/mdi_workspace/test_run
./run.sh
cd ~/mdi_workspace/test_run
explorer.exe .
cat << 'EOF' >> ~/.bashrc

# Winmostar をターミナルから自由に呼び出す簡単コマンド
wm() {
    if [ -z "$1" ]; then
        /mnt/c/winmos11/winmostar.exe &
    else
        /mnt/c/winmos11/winmostar.exe "$(wslpath -w "$1")" &
    fi
}
EOF

source ~/.bashrc
wim
wm dump.lammpstrj
wm md_animation.xyz
cd /home/yamazaki_yuta/mdi_workspace/test_run
python3 -c "import ase; print('ASE Version:', ase.__version__)" 2>/dev/null || echo "ASE is NOT installed in default python3" && pip3 show ase 2>/dev/null
sudo apt update && sudo apt install -y python3-pip python3-ase && python3 -c "import ase; print('ASE installed successfully! Version:', ase.__version__)"
killall -9 lmp 2>/dev/null; python3 -c "import mdi; print('MDI library is already installed')" 2>/dev/null || echo "MDI library is NOT installed" && pip3 show pymdi 2>/dev/null
sudo pip3 install --break-system-packages pymdi 2>/dev/null || sudo pip3 install pymdi
chmod +x qe_mdi_engine.py run.sh && ./run.sh
./run.sh
rm -f espresso.pwi CRASH && ./run.sh
./run.sh
find /mnt/c/ -maxdepth 3 -iname "*winmostar*" 2>/dev/null
python3 make_xyz.py
cd /home/yamazaki_yuta/mdi_workspace
chmod +x /home/yamazaki_yuta/mdi_workspace/init_project.sh
cd /home/yamazaki_yuta/mdi_workspace
ps aux | grep -i antigravity
cd ~/research_simulations
wm 2H-SiC.cif
cd /home/yamazaki_yuta/research_simulations
wm 2H-SiC_supercell_3x3x2.xyz
cd ~/mdi_workspace/SiC_3x3x2_MD
./run.sh
cd /home/yamazaki_yuta/research_simulations
python3 make_supercell.py
cd /home/yamazaki_yuta
lscpu; free -h
cd /home/yamazaki_yuta/research_simulations
python3 make_supercell.py
cd /home/yamazaki_yuta
ls -la ~/mdi_workspace
cd /home/yamazaki_yuta/mdi_workspace
./init_project.sh SiC_3x3x2_MD
cd /home/yamazaki_yuta/research_simulations
cat << 'EOF' > write_lammps_data.py
from ase.io import read, write

atoms = read('2H-SiC_supercell_3x3x2.cif')

write('2H-SiC_supercell_3x3x2.data', atoms, format='lammps-data')

EOF

python3 write_lammps_data.py
cp 2H-SiC_supercell_3x3x2.data ~/mdi_workspace/SiC_3x3x2_MD/
cat write_lammps_data.py; ls -l 2H-SiC_supercell_3x3x2.data
cd /home/yamazaki_yuta
pkill -f lmp; pkill -f qe_mdi_engine.py; pkill -f run.sh; pkill -f pw.x
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x2_MD
./run.sh && python3 make_xyz.py
find /home/yamazaki_yuta -name "*3x3x10*" -o -name "*.out" -mmin -120
find /home/yamazaki_yuta -name "*.in" -o -name "*.pwi" -o -name "*.scf" -o -name "*.UPF" | grep -v "lammps_src"
cd /home/yamazaki_yuta/mdi_workspace
mkdir -p /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only && cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only && cp /home/yamazaki_yuta/research_simulations/2H-SiC_supercell_3x3x10.xyz . && /home/yamazaki_yuta/research_simulations/atomsk 2H-SiC_supercell_3x3x10.xyz qe
cd /home/yamazaki_yuta/mdi_workspace
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only && cp ../SiC_3x3x2_MD/Si.upf . && cp ../SiC_3x3x2_MD/C.upf . && python3 -c "
from ase.io import read, write
atoms = read('/home/yamazaki_yuta/research_simulations/2H-SiC_supercell_3x3x10.cif')
write('qe.in', atoms, format='espresso-in', pseudopotentials={'Si': 'Si.upf', 'C': 'C.upf'}, kpts=(1,1,1), tstress=True, tprnfor=True, smearing='gaussian', degauss=0.01, ecutwfc=40.0, mixing_beta=0.3, electron_maxstep=200, conv_thr=1e-5, disk_io='minimal')
"
cd /home/yamazaki_yuta
which pw.x
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only
nohup pw.x < qe.in > qe.out &
cd /home/yamazaki_yuta
cat /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only/qe.out
find /home/yamazaki_yuta/mdi_workspace/q-e -name "pw.x" -type f
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only
nohup /home/yamazaki_yuta/mdi_workspace/q-e/PW/src/pw.x -in qe.in > qe.out 2>&1 &
nohup mpirun -np 4 /home/yamazaki_yuta/mdi_workspace/q-e/PW/src/pw.x -in qe.in > qe.out 2>&1 &
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only
cat << 'EOF' > /tmp/add_vacuum.py
import sys



infile = "/home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only/qe.in"



with open(infile, 'r') as f:

    lines = f.readlines()



with open(infile, 'w') as f:

    in_cell = False

    in_atoms = False

    for line in lines:

        if line.startswith("CELL_PARAMETERS"):

            in_cell = True

            f.write(line)

            continue

        elif line.startswith("ATOMIC_POSITIONS"):

            in_cell = False

            in_atoms = True

            f.write(line)

            continue

        elif not line.strip():

            in_cell = False

            in_atoms = False

            f.write(line)

            continue

            

        if in_cell:

            parts = line.split()

            if len(parts) == 3:

                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])

                if abs(z - 50.48) < 1e-4:

                    z += 20.0

                f.write(f"{x:.14f} {y:.14f} {z:.14f}\n")

                continue

                

        if in_atoms:

            parts = line.split()

            if len(parts) >= 4 and parts[0] in ['Si', 'C']:

                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])

                z += 10.0

                f.write(f"{parts[0]} {x:.10f} {y:.10f} {z:.10f}\n")

                continue

                

        f.write(line)



print("qe.in updated successfully!")

EOF

python3 /tmp/add_vacuum.py
python3 -c "
import math
v1 = [9.22800000000000, 0.0, 0.0]
v2 = [-4.61400000000000, 7.99168242612280, 0.0]
v3 = [0.0, 0.0, 70.47999999999999]

len_v1 = math.sqrt(sum(x*x for x in v1))
len_v2 = math.sqrt(sum(x*x for x in v2))
len_v3 = math.sqrt(sum(x*x for x in v3))

vol = v1[0]*v2[1]*v3[2]

print(f'Length a: {len_v1}')
print(f'Length b: {len_v2}')
print(f'Length c: {len_v3}')
print(f'Volume: {vol}')
"
cd /home/yamazaki_yuta/mdi_workspace
cd ~/mdi_workspace && ./init_project.sh SiC_3x3x10_MD
python3 -c "
from ase.io import read, write
import ase

# Read qe.in
atoms = read('/home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_QE_only/qe.in', format='espresso-in')

# Write to LAMMPS data
# specorder is necessary so type 1 is Si, type 2 is C
write('/home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/2H-SiC_supercell_3x3x10_vacuum.data', atoms, format='lammps-data', specorder=['Si', 'C'])
print('Conversion successful!')
"
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD
./run.sh
./run.sh
cd /home/yamazaki_yuta/mdi_workspace
python3 -c "
text = '''
## 10. 実用的なDFT-MD本番計算における設定（リスタート機能とNVT）
- 実際のDFT-MDシミュレーション（例：300Kでの安定化など）では、計算時間の制約により途中でジョブが切れることが多いため、LAMMPS側でリスタート機能と適切な温度制御（NVTアンサンブル）を設定することが必須である。
- **リスタートファイルの保存**: \`restart 10 restart1.rst restart2.rst\` のように、一定ステップごとに2つのファイルを交互に上書き保存し、最新状態を保持する。
- **リスタートからの再開**: スクリプト冒頭の \`read_data\` 等の代わりに \`read_restart restart1.rst\` を読み込むことで、以前の速度・座標・系全体の情報を引き継いで再開できる。
- **NVTアンサンブルでの制御**: \`velocity all create 300.0 12345\` で初期温度を与え、\`fix 2 all nvt temp 300.0 300.0 0.1\` のようにして系全体を一定温度で制御する。
- **トラジェクトリの追記保存**: 中断からの再開時に以前の履歴を消さないよう、\`dump_modify <ID> append yes\` を設定して \`.lammpstrj\` ファイルに座標情報を追記していく構成にすること。
'''
with open('/home/yamazaki_yuta/.gemini/config/skills/lammps_qe_mdi/SKILL.md', 'a') as f:
    f.write(text)
"
python3 -c "
import os

skill_path = '/home/yamazaki_yuta/.gemini/config/skills/lammps_qe_mdi/SKILL.md'
with open(skill_path, 'r') as f:
    content = f.read()

old_block = '''  wget -q http://archive.ubuntu.com/ubuntu/pool/universe/n/ncurses/libtinfo5_6.3-2_amd64.deb
  wget -q http://archive.ubuntu.com/ubuntu/pool/universe/n/ncurses/libncursesw5_6.3-2_amd64.deb
  dpkg -i libtinfo5_6.3-2_amd64.deb libncursesw5_6.3-2_amd64.deb
  apt-get install -y nvhpc-23-11'''

new_block = '''  wget -q http://archive.ubuntu.com/ubuntu/pool/universe/n/ncurses/libtinfo5_6.3-2_amd64.deb
  wget -q http://archive.ubuntu.com/ubuntu/pool/universe/n/ncurses/libncursesw5_6.3-2_amd64.deb
  dpkg -i libtinfo5_6.3-2_amd64.deb libncursesw5_6.3-2_amd64.deb
  curl -s -L https://developer.download.nvidia.com/hpc-sdk/ubuntu/DEB-GPG-KEY-NVIDIA-HPC-SDK | gpg --dearmor -o /usr/share/keyrings/nvidia-hpc-sdk-archive-keyring.gpg
  echo 'deb [signed-by=/usr/share/keyrings/nvidia-hpc-sdk-archive-keyring.gpg] https://developer.download.nvidia.com/hpc-sdk/ubuntu/amd64 /' > /etc/apt/sources.list.d/nvhpc.list
  apt-get update
  apt-get install -y nvhpc-23-11'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(skill_path, 'w') as f:
        f.write(content)
"
echo "All tasks completed successfully."
cd /home/yamazaki_yuta/.gemini/antigravity-ide/brain/d4f1e080-0a19-4d3d-9c99-c469392558a2/scratch
python3 /home/yamazaki_yuta/.gemini/antigravity-ide/brain/d4f1e080-0a19-4d3d-9c99-c469392558a2/scratch/append_skill.py
cd /home/yamazaki_yuta/mdi_workspace
find /home/yamazaki_yuta/mdi_workspace/ -name "*.ipynb"
grep -A 5 -B 5 "colab_transfer.tar.gz" /home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb
cd /home/yamazaki_yuta
cd /home/yamazaki_yuta/mdi_workspace
cat /home/yamazaki_yuta/mdi_workspace/colab_setup_mdi_gpu.ipynb | grep -A 10 "run_colab.sh"
cd /home/yamazaki_yuta
mkdir -p ~/.local/bin && curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared
mkdir -p ~/bin && curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/bin/cloudflared && chmod +x ~/bin/cloudflared
cd /home/yamazaki_yuta/mdi_workspace
./package_for_colab.sh
bash ./package_for_colab.sh
python3 -c "import shutil; shutil.make_archive('colab_transfer', 'zip', '/home/yamazaki_yuta/mdi_workspace', 'SiC_3x3x10_MD')"
python3 -m zipfile -l colab_transfer.zip | head -n 10
cd /home/yamazaki_yuta
mount | grep drvfs; ls -l /mnt
ls -ld /mnt/c/Users/*/Google* /mnt/c/Users/*/*Drive* 2>/dev/null
cd /home/yamazaki_yuta/mdi_workspace
python3 -c "import shutil; shutil.make_archive('colab_transfer', 'zip', '/home/yamazaki_yuta/mdi_workspace', 'SiC_3x3x10_MD')"
cd /home/yamazaki_yuta
cd /home/yamazaki_yuta/mdi_workspace
python3 -c "import shutil; shutil.make_archive('colab_transfer', 'zip', '/home/yamazaki_yuta/mdi_workspace', 'SiC_3x3x10_MD')"
cd /home/yamazaki_yuta
timeout 5 ls -l /mnt/g/MyDrive/SiC_MD_backup /mnt/g/マイドライブ/SiC_MD_backup 2>/dev/null
tail -n 50 /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
grep -A 1 "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj | tail -n 10; echo "---"; grep -c "iteration #  1 " /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
grep -c "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
grep "ITEM: TIMESTEP" -A 1 /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
tail -n 30 /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
grep "!" /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
grep -B 2 -A 5 "iteration #  1 " /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
ls -l /mnt/g/マイドライブ/SiC_MD_backup/
grep -A 1 "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
ps aux | grep lmp; echo "---"; head -n 10 /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
ps aux | grep mpi
grep -c "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
tail -n 20 /mnt/g/マイドライブ/SiC_MD_backup/qe_engine.log
grep -A 1 "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj | grep -c "^9"
while true; do if grep -A 1 "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj | egrep -q "^10\r?$"; then echo "NEW TIMESTEP 10 FOUND"; exit 0; fi; sleep 60; done
grep -A 1 "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
while true; do count=$(grep -c "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj); if [ "$count" -gt 13 ]; then echo "NEW BLOCK FOUND! Total count: $count"; exit 0; fi; sleep 60; done
stat -c "%y" /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
stat -c "%y" /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo; tail -n 20 /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
stat -c "%y" /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo; grep -c "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
ls -lh /mnt/g/マイドライブ/SiC_MD_backup/
tail -n 30 /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
tail -n 20 /mnt/g/マイドライブ/SiC_MD_backup/qe_engine.log
tail -n 20 /mnt/g/マイドライブ/SiC_MD_backup/log.lammps
stat -c "%y" /mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo
grep -A 1 "ITEM: TIMESTEP" /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
tail -n 10 "/mnt/g/マイドライブ/SiC_MD_backup/qe_engine.log" "/mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo"
cat "/mnt/g/マイドライブ/SiC_MD_backup/log.lammps"
tail -n 20 "/mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo" "/mnt/g/マイドライブ/SiC_MD_backup/log.lammps"
tail -n 20 "/mnt/g/マイドライブ/SiC_MD_backup/espresso.pwo"
bash ~/setup_nas_sync.sh
python3 /home/yamazaki_yuta/.gemini/antigravity-ide/brain/f676fcb6-b5bb-4a07-af52-0552e412ee12/scratch/append_ssh_config.py
tail -n 370 /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD
chmod +x monitor.sh && ./monitor.sh
./monitor.sh
./monitor.sh
./monitor.sh
./monitor.sh
cd /home/yamazaki_yuta
which colab
sshpass -p "mypassword" ssh -o StrictHostKeyChecking=no root@milton-sur-social-bones.trycloudflare.com "ls -la /content"
sudo apt-get install sshpass -y
cp /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/in.lammps "/mnt/g/マイドライブ/SiC_MD_backup/in.lammps"
python3 run_ssh.py
pip install pexpect
python3 run_ssh.py
which cloudflared
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x cloudflared-linux-amd64 && mkdir -p ~/bin && mv cloudflared-linux-amd64 ~/bin/cloudflared && mkdir -p ~/.ssh && echo -e "\nHost *.trycloudflare.com\n    HostName %h\n    User root\n    Port 22\n    ProxyCommand ~/bin/cloudflared access ssh --hostname %h\n    StrictHostKeyChecking no" > ~/.ssh/config
python3 run_ssh.py
python3 run_ssh.py dresses-took-major-counties.trycloudflare.com
~/bin/cloudflared access ssh --hostname dresses-took-major-counties.trycloudflare.com
cat << 'EOF' > /mnt/g/マイドライブ/SiC_MD_backup/restart_job.py
import os

import subprocess

import time



print("--- 1. Copying files to Colab workspace ---")

os.system("mkdir -p /content/SiC_3x3x10_MD")

os.system("cp -r /content/drive/MyDrive/SiC_MD_backup/* /content/SiC_3x3x10_MD/")



print("--- 2. Installing requirements ---")

os.system("pip install ase pymdi")



print("--- 3. Starting calculation in background ---")

os.chdir("/content/SiC_3x3x10_MD")

os.system("nohup bash run_colab.sh > nohup.out 2>&1 &")



print("--- 4. Starting backup loop in background ---")

backup_cmd = "nohup bash -c 'while true; do cp /content/SiC_3x3x10_MD/*.lammpstrj /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/*.pwo /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; cp /content/SiC_3x3x10_MD/qe_engine.log /content/drive/MyDrive/SiC_MD_backup/ 2>/dev/null; sleep 300; done' > backup_nohup.out 2>&1 &"

os.system(backup_cmd)



print("\nSUCCESS! Calculation and Backup Loop are now running in the background!")

print("You can close this cell. Monitor the progress from the Antigravity app!")

EOF

python3 run_ssh.py dresses-took-major-counties.trycloudflare.com
python3 run_ssh.py adjustment-silk-herald-summary.trycloudflare.com
ls -1 /mnt/g/マイドライブ/SiC_MD_backup/
cp /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/* "/mnt/g/マイドライブ/SiC_MD_backup/"
ls -l /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/dump_min.lammpstrj /mnt/g/マイドライブ/SiC_MD_backup/dump_min.lammpstrj
ls -l /mnt/z/SiC_MD_NAS_Backup/
ls -l /mnt/nas_backup/Yamazaki-tj/SiC_MD_backup/dump_min.lammpstrj /mnt/nas_results/yamazaki/research/SiC_MD_backup/dump_min.lammpstrj
ls -l /mnt/nas_backup/Yamazaki-tj/
ls -l /mnt/nas_backup/Yamazaki-tj/SiC_MD_backup/
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD
./monitor.sh
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-922.log
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "head -n 20 /content/SiC_3x3x10_MD/espresso.pwi"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1690.log
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1747.log
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/SiC_3x3x10_MD/nohup.out"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "grep 'TIMESTEP' /content/SiC_3x3x10_MD/dump_min.lammpstrj | wc -l"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls -la /content/SiC_3x3x10_MD/dump_min.lammpstrj"
ls -la /mnt/nas_results/yamazaki/research/SiC_MD_backup/ | grep dump
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/SiC_3x3x10_MD/in.lammps"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "sed -i 's/read_dump dump_min.lammpstrj 23/#read_dump dump_min.lammpstrj 23/' /content/SiC_3x3x10_MD/in.lammps && sed -i 's/dump_modify 1 append yes/#dump_modify 1 append yes/' /content/SiC_3x3x10_MD/in.lammps && cp /content/SiC_3x3x10_MD/in.lammps /content/drive/MyDrive/SiC_MD_backup/"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/SiC_3x3x10_MD && bash run_colab.sh > nohup.out 2>&1 & sleep 3 && cat nohup.out"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-889.log
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "bash -c 'export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7; export OPAL_PREFIX=\$(find \$NVHPC_HOME/comm_libs -type d -name ompi | head -n 1); export LD_LIBRARY_PATH=\$OPAL_PREFIX/lib:\$NVHPC_HOME/compilers/lib:\$NVHPC_HOME/cuda/lib64:\$LD_LIBRARY_PATH; cd /content/SiC_3x3x10_MD && \$OPAL_PREFIX/bin/mpirun --allow-run-as-root -np 1 /content/bin/pw.x -in espresso.pwi'"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "nvidia-smi"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "lspci | grep -i nvidia"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls /proc/driver/nvidia/gpus || echo 'No GPUs'"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "env LD_LIBRARY_PATH=/usr/lib64-nvidia:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 nvidia-smi"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "objdump -x /content/bin/pw.x | grep RPATH"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "objdump -x /content/bin/pw.x | grep RUNPATH"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "bash -c 'export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7; export OPAL_PREFIX=\$(find \$NVHPC_HOME/comm_libs -type d -name ompi | head -n 1); export PATH=\$OPAL_PREFIX/bin:\$NVHPC_HOME/compilers/bin:\$NVHPC_HOME/cuda/bin:\$PATH; export LD_LIBRARY_PATH=\$OPAL_PREFIX/lib:\$NVHPC_HOME/compilers/lib:\$NVHPC_HOME/cuda/lib64:\$LD_LIBRARY_PATH; export OMPI_ALLOW_RUN_AS_ROOT=1; export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1; cd /content/SiC_3x3x10_MD && /content/bin/pw.x -in espresso.pwi'"
scp -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -P 10174 /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py root@2.tcp.ngrok.io:/content/SiC_3x3x10_MD/
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
ssh colab "sleep 3; head -n 25 /content/SiC_3x3x10_MD/run_final.log"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1668.log
ssh colab "grep TIMESTEP /content/SiC_3x3x10_MD/dump_min.lammpstrj"
ssh colab "ls -l /content/SiC_3x3x10_MD/dump_min.lammpstrj"
ssh colab "ls -l /content/drive/MyDrive/SiC_MD_backup/dump_min.lammpstrj"
df -h; ls -la /mnt
find /mnt/nas_backup /mnt/nas_results -name "dump_min.lammpstrj" -exec ls -l {} +
ls -la /mnt/nas_results/yamazaki/research/SiC_MD_backup/.snapshot 2>/dev/null || ls -la /mnt/nas_results/#recycle 2>/dev/null
ssh colab "sleep 3; head -n 30 /content/SiC_3x3x10_MD/run_final.log"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1737.log
ssh colab "sleep 10; grep -i 'gpu' /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "head -n 20 /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "cat /content/SiC_3x3x10_MD/run_final.log"
ssh colab "grep -i 'gpu' /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "head -n 25 /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "cat /content/SiC_3x3x10_MD/qe_engine.log"
ssh colab "ps -ef | grep pw.x"
ssh colab "cat /content/SiC_3x3x10_MD/qe_mdi_engine.py | grep pw.x"
ssh colab "pkill -f pw.x; pkill -f lmp; pkill -f python3; sed -i \"s|pw_bin = '/content/q-e-qe-7.3/bin/pw.x'|pw_bin = '/content/bin/pw.x'|g\" /content/SiC_3x3x10_MD/qe_mdi_engine.py && cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 &"
ssh colab "sleep 5; cat /content/SiC_3x3x10_MD/run_final.log"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1814.log
ssh colab "cat /content/bin/pw.x"
ssh colab "cat << 'EOF' > /content/bin/pw.x
export NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/23.11
export PATH=\$NVHPC_HOME/compilers/bin:\$NVHPC_HOME/comm_libs/mpi/bin:\$NVHPC_HOME/cuda/bin:\$PATH
export LD_LIBRARY_PATH=\$NVHPC_HOME/compilers/lib:\$NVHPC_HOME/comm_libs/mpi/lib:\$NVHPC_HOME/math_libs/lib64:\$NVHPC_HOME/cuda/lib64:/usr/local/cuda/lib64:/usr/lib64-nvidia:\$LD_LIBRARY_PATH
# HCOLLによるMDIエラーを回避するため、HCOLLを無効化する環境変数をセット
export OMPI_MCA_coll_hcoll_enable=0
export OMPI_MCA_pml=ob1
\$NVHPC_HOME/comm_libs/mpi/bin/mpirun --allow-run-as-root -x LD_LIBRARY_PATH -x PATH -x OMPI_MCA_coll_hcoll_enable -x OMPI_MCA_pml -np 1 /content/bin/pw.x.real \"\$@\"
EOF
chmod +x /content/bin/pw.x && pkill -f pw.x || true; pkill -f lmp || true; pkill -f python3 || true; cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 </dev/null &"
ssh colab "sleep 5; cat /content/SiC_3x3x10_MD/run_final.log"
ssh colab "pkill -f qe_mdi_engine.py || true; cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 </dev/null &"
ssh colab "cat /content/bin/pw.x; ls -la /content/bin/pw.x"
ssh colab 'echo -e "#!/bin/bash\nexport NVHPC_HOME=/opt/nvidia/hpc_sdk/Linux_x86_64/23.11\nexport PATH=\$NVHPC_HOME/compilers/bin:\$NVHPC_HOME/comm_libs/mpi/bin:\$NVHPC_HOME/cuda/bin:\$PATH\nexport LD_LIBRARY_PATH=\$NVHPC_HOME/compilers/lib:\$NVHPC_HOME/comm_libs/mpi/lib:\$NVHPC_HOME/math_libs/lib64:\$NVHPC_HOME/cuda/lib64:/usr/local/cuda/lib64:/usr/lib64-nvidia:\$LD_LIBRARY_PATH\nexport OMPI_MCA_coll_hcoll_enable=0\nexport OMPI_MCA_pml=ob1\n\$NVHPC_HOME/comm_libs/mpi/bin/mpirun --allow-run-as-root -x LD_LIBRARY_PATH -x PATH -x OMPI_MCA_coll_hcoll_enable -x OMPI_MCA_pml -np 1 /content/bin/pw.x.real \"\$@\"" > /content/bin/pw.x' && ssh colab "pkill -f pw.x || true; pkill -f lmp || true; pkill -f qe_mdi_engine || true; cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 </dev/null &"
ssh colab "cat /content/bin/pw.x; ls -la /content/bin/pw.x"
ssh colab "sleep 5; cat /content/SiC_3x3x10_MD/run_final.log"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1845.log
ssh colab "ls -l /content/SiC_3x3x10_MD/run_final.log"
ssh colab "cat << 'EOF' > /content/SiC_3x3x10_MD/start.sh
pkill -f pw.x || true
pkill -f lmp || true
pkill -f python3 || true
cd /content/SiC_3x3x10_MD
nohup bash run_colab.sh > run_final.log 2>&1 &
EOF
chmod +x /content/SiC_3x3x10_MD/start.sh && /content/SiC_3x3x10_MD/start.sh"
ssh colab "sleep 5; ls -la /content/SiC_3x3x10_MD/run_final.log"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1858.log
ssh colab "pkill -f pw.x || true; pkill -f lmp || true; pkill -f qe_mdi_engine || true; cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 </dev/null &"
ssh colab "tmux new-session -d -s md_run 'cd /content/SiC_3x3x10_MD && bash run_colab.sh > run_final.log 2>&1'"
ssh colab "sleep 5; ls -la /content/SiC_3x3x10_MD/run_final.log; tail -n 20 /content/SiC_3x3x10_MD/run_final.log"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1872.log
ssh colab "cat /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "grep -i 'gpu' /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "tail -n 10 /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "cat /content/SiC_3x3x10_MD/run_colab.sh"
ssh colab "grep -i 'iteration #' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 10"
ssh colab "tail -n 15 /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "cat << 'EOF' > /content/SiC_3x3x10_MD/sync_nas.sh
NAS_DIR=\"/mnt/nas_results/yamazaki/research/SiC_MD_backup\"
while true; do
  rsync -avz --update /content/SiC_3x3x10_MD/espresso.pwo \"\$NAS_DIR/\"
  rsync -avz --update /content/SiC_3x3x10_MD/run_final.log \"\$NAS_DIR/\"
  rsync -avz --update /content/SiC_3x3x10_MD/qe_engine.log \"\$NAS_DIR/\"
  rsync -avz --update /content/SiC_3x3x10_MD/dump_min.lammpstrj \"\$NAS_DIR/\"
  rsync -avz --update /content/SiC_3x3x10_MD/SiC_min.data \"\$NAS_DIR/\"
  sleep 300
done
EOF
chmod +x /content/SiC_3x3x10_MD/sync_nas.sh
tmux new-session -d -s md_sync 'bash /content/SiC_3x3x10_MD/sync_nas.sh'"
cat << 'EOF' > /tmp/sync_nas.sh
#!/bin/bash

NAS_DIR="/mnt/nas_results/yamazaki/research/SiC_MD_backup"

while true; do

  rsync -avz --update /content/SiC_3x3x10_MD/espresso.pwo "$NAS_DIR/"

  rsync -avz --update /content/SiC_3x3x10_MD/run_final.log "$NAS_DIR/"

  rsync -avz --update /content/SiC_3x3x10_MD/qe_engine.log "$NAS_DIR/"

  rsync -avz --update /content/SiC_3x3x10_MD/dump_min.lammpstrj "$NAS_DIR/"

  rsync -avz --update /content/SiC_3x3x10_MD/SiC_min.data "$NAS_DIR/"

  sleep 300

done

EOF

scp /tmp/sync_nas.sh colab:/content/SiC_3x3x10_MD/sync_nas.sh
ssh colab "chmod +x /content/SiC_3x3x10_MD/sync_nas.sh && tmux new-session -d -s md_sync 'bash /content/SiC_3x3x10_MD/sync_nas.sh'"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1909.log
ssh colab "tmux kill-session -t md_sync; tmux new-session -d -s md_sync 'bash /content/SiC_3x3x10_MD/sync_nas.sh'"
ls -l /mnt/nas_results/yamazaki/research/SiC_MD_backup/espresso.pwo
tail -n 20 /mnt/nas_results/yamazaki/research/SiC_MD_backup/espresso.pwo
cat << 'EOF' > /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/monitor_scf.sh
#!/bin/bash

echo "Monitoring SCF convergence from Colab..."

echo "Press Ctrl+C to stop."

while true; do

    date '+[%Y-%m-%d %H:%M:%S]' >> scf_convergence.log

    ssh colab "grep -E 'iteration|estimated scf accuracy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 10" >> scf_convergence.log 2>/dev/null

    echo "Updated scf_convergence.log. Waiting 60 seconds..."

    sleep 60

done

EOF

chmod +x /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/monitor_scf.sh
cd /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD
/home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/monitor_scf.sh
cd /home/yamazaki_yuta
chmod +x /home/yamazaki_yuta/monitor_scf.sh && /home/yamazaki_yuta/monitor_scf.sh
ssh colab "echo hello"
cat ~/.ssh/config
which cloudflared
ssh colab "echo hello"
sed -i 's/HostName .*/HostName 8.tcp.ngrok.io/' ~/.ssh/config && sed -i 's/Port .*/Port 17016/' ~/.ssh/config && cat ~/.ssh/config
ssh colab "grep -E 'iteration #|estimated scf' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 10"
ssh -v colab "echo hello"
ssh colab "grep -E 'iteration #|estimated scf|total energy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 20"
ssh -v colab "echo hello"
ssh -v colab "echo hello"
ssh colab "grep -E 'iteration #|estimated scf|total energy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 20"
ssh -v colab "echo hello"
sshpass -p "mypassword" ssh -o StrictHostKeyChecking=no colab "grep -E 'iteration #|estimated scf|total energy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 20"
cat << 'EOF' > /home/yamazaki_yuta/run_ssh.py
import pexpect

import sys

import time



def run_ssh_commands():

    child = pexpect.spawn('ssh colab', encoding='utf-8', timeout=60)

    

    try:

        index = child.expect(['password:', 'Are you sure you want to continue connecting', pexpect.EOF, pexpect.TIMEOUT])

        

        if index == 1:

            child.sendline('yes')

            child.expect('password:')

            child.sendline('mypassword')

        elif index == 0:

            child.sendline('mypassword')

        else:

            print(f"Failed to connect: {child.before}")

            return

            

        child.expect(r'root@.*#')

        

        commands = [

            "grep -E 'iteration #|estimated scf|total energy' /content/SiC_3x3x10_MD/espresso.pwo | tail -n 20"

        ]

        

        for cmd in commands:

            print(f"\nExecuting: {cmd}")

            child.sendline(cmd)

            child.expect(r'root@.*#')

            print(child.before)

            

        child.sendline('exit')

        child.expect(pexpect.EOF)

        

    except Exception as e:

        print(f"An error occurred: {e}")

        print(f"Current output: {child.before}")



if __name__ == '__main__':

    run_ssh_commands()

EOF

python3 /home/yamazaki_yuta/run_ssh.py
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1991.log
cat << 'EOF' > /home/yamazaki_yuta/run_ssh.py
import pexpect

import sys

import time



def run_ssh_commands():

    child = pexpect.spawn('ssh colab', encoding='utf-8', timeout=60)

    

    try:

        index = child.expect(['password:', 'Are you sure you want to continue connecting', pexpect.EOF, pexpect.TIMEOUT])

        

        if index == 1:

            child.sendline('yes')

            child.expect('password:')

            child.sendline('mypassword')

        elif index == 0:

            child.sendline('mypassword')

        else:

            print(f"Failed to connect: {child.before}")

            return

            

        child.expect(r'root@.*#')

        

        commands = [

            "ls -la /content"

        ]

        

        for cmd in commands:

            print(f"\nExecuting: {cmd}")

            child.sendline(cmd)

            child.expect(r'root@.*#')

            print(child.before)

            

        child.sendline('exit')

        child.expect(pexpect.EOF)

        

    except Exception as e:

        print(f"An error occurred: {e}")

        print(f"Current output: {child.before}")



if __name__ == '__main__':

    run_ssh_commands()

EOF

python3 /home/yamazaki_yuta/run_ssh.py
ssh -v colab "echo hello"
cat << 'EOF' > ~/.ssh/config
Host colab

    HostName tiger-web-backed-jeff.trycloudflare.com

    User root

    Port 22

    ProxyCommand /home/yamazaki_yuta/bin/cloudflared access tcp --hostname %h --url localhost:22

    StrictHostKeyChecking no

    UserKnownHostsFile /dev/null

    LogLevel ERROR

EOF

cat ~/.ssh/config
cat << 'EOF' > ~/.ssh/config
Host colab

    HostName tiger-web-backed-jeff.trycloudflare.com

    User root

    Port 22

    ProxyCommand /home/yamazaki_yuta/bin/cloudflared access tcp --hostname %h --url localhost:22

    StrictHostKeyChecking no

    UserKnownHostsFile /dev/null

    LogLevel ERROR

EOF

python3 /home/yamazaki_yuta/run_ssh.py
/home/yamazaki_yuta/bin/cloudflared access ssh --help
cat << 'EOF' > ~/.ssh/config
Host colab

    HostName tiger-web-backed-jeff.trycloudflare.com

    User root

    Port 22

    ProxyCommand /home/yamazaki_yuta/bin/cloudflared access ssh --hostname %h

    StrictHostKeyChecking no

    UserKnownHostsFile /dev/null

    LogLevel ERROR

EOF

python3 /home/yamazaki_yuta/run_ssh.py
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-2044.log
cat /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py
cat << 'EOF' > /home/yamazaki_yuta/run_ssh2.py
import pexpect

import sys

import os

import time



def run_ssh_commands():

    # Start cloudflared in the background listening on port 2222

    os.system("/home/yamazaki_yuta/bin/cloudflared access tcp --hostname tiger-web-backed-jeff.trycloudflare.com --listener 127.0.0.1:2222 > /dev/null 2>&1 &")

    time.sleep(2) # wait for it to start

    

    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -p 2222 root@127.0.0.1', encoding='utf-8', timeout=60)

    

    try:

        index = child.expect(['password:', 'Are you sure you want to continue connecting', pexpect.EOF, pexpect.TIMEOUT])

        

        if index == 1:

            child.sendline('yes')

            child.expect('password:')

            child.sendline('mypassword')

        elif index == 0:

            child.sendline('mypassword')

        else:

            print(f"Failed to connect: {child.before}")

            return

            

        child.expect(r'root@.*#')

        print("Successfully connected!")

        

        commands = [

            "ls -la /content"

        ]

        

        for cmd in commands:

            print(f"\nExecuting: {cmd}")

            child.sendline(cmd)

            child.expect(r'root@.*#')

            print(child.before)

            

        child.sendline('exit')

        child.expect(pexpect.EOF)

        

    except Exception as e:

        print(f"An error occurred: {e}")

        print(f"Current output: {child.before}")

    finally:

        os.system("pkill -f cloudflared")



if __name__ == '__main__':

    run_ssh_commands()

EOF

python3 /home/yamazaki_yuta/run_ssh2.py
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-2054.log
base64 -w 0 /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py > /tmp/qe_engine.b64
grep -i 'dump' /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/logs/transcript.jsonl | tail -n 20
grep -c 'ITEM: TIMESTEP' /home/yamazaki_yuta/mdi_workspace/test_run/dump.lammpstrj
grep -C 5 "21" /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/logs/transcript.jsonl
grep '"type":"USER_INPUT"' /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/logs/transcript_full.jsonl
grep -C 5 "21" /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/logs/transcript_full.jsonl
find /mnt -type f -name "*dump*.lammpstrj" 2>/dev/null
mount | grep mnt
grep -rl "NAS" /home/yamazaki_yuta/.gemini/antigravity-ide/brain/ | grep "transcript.jsonl"
grep -C 2 "21" /home/yamazaki_yuta/.gemini/antigravity-ide/brain/f676fcb6-b5bb-4a07-af52-0552e412ee12/.system_generated/logs/transcript.jsonl
ls -lh /mnt/nas_results/yamazaki/research/SiC_MD_backup/
grep -c "ITEM: TIMESTEP" /mnt/nas_results/yamazaki/research/SiC_MD_backup/dump_min.lammpstrj
tail -n 30 /mnt/nas_results/yamazaki/research/SiC_MD_backup/espresso.pwo /mnt/nas_results/yamazaki/research/SiC_MD_backup/qe_engine.log
tail -n 20 /mnt/nas_results/yamazaki/research/SiC_MD_backup/espresso.pwo
stat /mnt/nas_results/yamazaki/research/SiC_MD_backup/espresso.pwo
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls -la /content/SiC_3x3x10_MD/"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/SiC_3x3x10_MD/nohup.out"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/SiC_3x3x10_MD/run_colab.sh"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/drive/MyDrive/SiC_MD_backup/run_colab.sh"
scp -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -P 10174 /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/run_colab.sh /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py root@2.tcp.ngrok.io:/content/SiC_3x3x10_MD/
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/SiC_3x3x10_MD && bash run_colab.sh > nohup.out 2>&1 & sleep 3 && cat nohup.out"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "top -b -n 1 | grep pw.x"
tail -n 30 /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-869.log
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "/content/bin/pw.x --version"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls -l /opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi/share/openmpi/help-opal-runtime.txt"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "bash -c 'export OPAL_PREFIX=/opt/nvidia/hpc_sdk/Linux_x86_64/24.7/comm_libs/12.5/hpcx/hpcx-2.19/ompi; /content/bin/pw.x --version'"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ldd /usr/bin/pw.x | grep mpi"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ldd /content/bin/lmp | grep nvhpc || echo 'No NVHPC link'"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/SiC_3x3x10_MD && bash run_colab.sh"
scp -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -P 10174 /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/run_colab.sh root@2.tcp.ngrok.io:/content/SiC_3x3x10_MD/
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/SiC_3x3x10_MD && bash run_colab.sh"
scp -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -P 10174 root@2.tcp.ngrok.io:/content/SiC_3x3x10_MD/run_colab.sh /tmp/run_colab.sh && cat /tmp/run_colab.sh
scp -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -P 10174 /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/run_colab.sh root@2.tcp.ngrok.io:/content/SiC_3x3x10_MD/
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/SiC_3x3x10_MD && bash run_colab.sh"
scp -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -P 10174 /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/qe_mdi_engine.py root@2.tcp.ngrok.io:/content/SiC_3x3x10_MD/ && ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/SiC_3x3x10_MD && bash run_colab.sh"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/SiC_3x3x10_MD/espresso.pwo"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls -l /content/SiC_3x3x10_MD/*.upf"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls -l /content/SiC_3x3x10_MD/tmp"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "top -b -n 1 | head -n 20"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "tail -n 10 /content/SiC_3x3x10_MD/test_pw.out"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "tail -n 20 /content/SiC_3x3x10_MD/test_pw_2.out"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ps aux | grep pw.x"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content && wget https://gitlab.com/QEF/q-e/-/archive/qe-7.3/q-e-qe-7.3.tar.gz && tar -xzf q-e-qe-7.3.tar.gz && cd q-e-qe-7.3 && ./configure && make pw -j4"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "tail -n 100 /content/q-e-qe-7.3/make.log || (cd /content/q-e-qe-7.3 && make pw -j4 > make.log 2>&1 ; tail -n 100 make.log)"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "ls -l /content/q-e-qe-7.3/bin/pw.x"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/q-e-qe-7.3 && make pw > make_pw.log 2>&1 ; tail -n 50 make_pw.log"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/q-e-qe-7.3 && ./configure BLAS_LIBS='-lopenblas' LAPACK_LIBS='-lopenblas' FFT_LIBS=' ' && make clean && make pw -j4"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/q-e-qe-7.3 && make pw > make_pw2.log 2>&1 ; tail -n 50 make_pw2.log"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "apt-get update && apt-get install -y libfftw3-dev libopenblas-dev && cd /content/q-e-qe-7.3 && ./configure BLAS_LIBS='-lopenblas' LAPACK_LIBS='-lopenblas' FFT_LIBS='-lfftw3' && make clean && make pw -j4"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cd /content/q-e-qe-7.3 && make pw > make_pw3.log 2>&1 ; tail -n 50 make_pw3.log"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
echo "Waiting for QE compilation to finish"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "cat /content/SiC_3x3x10_MD/run_final.log"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "tail -n 30 /content/SiC_3x3x10_MD/espresso.pwo || echo NO_PWO"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "free -m"
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -p 10174 root@2.tcp.ngrok.io "tail -n 20 /content/SiC_3x3x10_MD/espresso.pwo"
curl -s -H "Authorization: Bearer 3JrzmLdvC9oISWzaKhSfnfQdFRl_3wpQXiFgcsPp4qfh51xYi" -H "Ngrok-Version: 2" https://api.ngrok.com/tunnels
ssh colab nvidia-smi
ssh colab "export LD_LIBRARY_PATH=/usr/lib64-nvidia:\$LD_LIBRARY_PATH && nvidia-smi"
ssh colab "cat /content/SiC_3x3x10_MD/qe_mdi_engine.py | grep mpirun"
ssh colab "sed -i 's/mpirun --allow-run-as-root -np 1 {pw_bin}/{pw_bin}/g' /content/SiC_3x3x10_MD/qe_mdi_engine.py"
ssh colab "tail -n 15 /content/compile_gpu.log"
ssh colab "cat /content/SiC_3x3x10_MD/run_colab.sh"
ssh colab "sed -i '1s/^/export OMPI_MCA_coll_hcoll_enable=0\\nexport OMPI_MCA_pml=ob1\\n/' /content/SiC_3x3x10_MD/run_colab.sh && cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 &"
sleep 1
find /mnt/nas_backup /mnt/nas_results -name "dump_min.lammpstrj" -not -empty -exec ls -la {} +
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1712.log
grep TIMESTEP /mnt/nas_results/yamazaki/research/SiC_MD_backup/dump_min.lammpstrj | wc -l
grep -A 1 TIMESTEP /mnt/nas_results/yamazaki/research/SiC_MD_backup/dump_min.lammpstrj | tail -n 2
ssh colab "tail -n 5 /content/compile_gpu.log"
# Update local in.lammps to read step 21
sed -i 's/read_dump dump_min.lammpstrj 23/read_dump dump_min.lammpstrj 21/' /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/in.lammps
# Copy in.lammps and the recovered dump file to Colab
scp /home/yamazaki_yuta/mdi_workspace/SiC_3x3x10_MD/in.lammps colab:/content/SiC_3x3x10_MD/in.lammps
scp /mnt/nas_results/yamazaki/research/SiC_MD_backup/dump_min.lammpstrj colab:/content/SiC_3x3x10_MD/dump_min.lammpstrj
# Remove the rm command for dump_min.lammpstrj from run_colab.sh so it doesn't get deleted again!
ssh colab "sed -i 's/ dump.lammpstrj / /g' /content/SiC_3x3x10_MD/run_colab.sh"
ssh colab "ls -l /content/SiC_3x3x10_MD/dump_min.lammpstrj"
ssh colab "cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 &"
ssh colab "cat /content/SiC_3x3x10_MD/qe_mdi_engine.py | grep pw_bin"
ssh colab "pkill -f pw.x || true; pkill -f lmp || true; pkill -f python3 || true; sed -i \"s|pw_bin = '/content/q-e-qe-7.3/bin/pw.x'|pw_bin = '/content/bin/pw.x'|g\" /content/SiC_3x3x10_MD/qe_mdi_engine.py && cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 &"
ssh colab "pkill -f pw.x || true; pkill -f lmp || true; pkill -f qe_mdi_engine || true; sed -i \"s|pw_bin = '/content/q-e-qe-7.3/bin/pw.x'|pw_bin = '/content/bin/pw.x'|g\" /content/SiC_3x3x10_MD/qe_mdi_engine.py && cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 &"
ssh colab "sed -i \"s|pw_bin = '/content/q-e-qe-7.3/bin/pw.x'|pw_bin = '/content/bin/pw.x'|g\" /content/SiC_3x3x10_MD/qe_mdi_engine.py"
ssh colab "cd /content/SiC_3x3x10_MD && nohup bash run_colab.sh > run_final.log 2>&1 </dev/null &"
ssh colab "sleep 5; grep -i 'gpu' /content/SiC_3x3x10_MD/espresso.pwo"
cat /home/yamazaki_yuta/.gemini/antigravity-ide/brain/790db786-fbae-4df5-9d47-5a49f5d6e80d/.system_generated/tasks/task-1794.log
ssh colab "head -n 25 /content/SiC_3x3x10_MD/espresso.pwo"
ssh colab "cat /content/SiC_3x3x10_MD/run_final.log"
ssh colab "cat /content/bin/pw.x"
bash ~/setup_nas_sync.sh
ssh colab
# パスワードを聞かれたら mypassword と入力
ssh colab
tail -f run_final.log
cd /content/SiC_3x3x10_MD
tail -f run_final.log
