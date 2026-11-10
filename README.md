## 1. Előfeltételek és Környezet beállítása

### A külső függőségek automatikus telepítéséhez futtasd az `install_dependencies.sh` az albbi parancsokkal Terminátorban:


cd ~/ros2_ws/src/MGM_WAFFLE
install_dependencies.sh


A script elvégzi az alábbiakat:
1. Telepíti a szükséges `apt` csomagokat 
2. Klónozza a [mrtsp_exploration_ros2] csomagot
3. Futtatja a `rosdep` ellenőrzést az esetleges további csomagfüggőségekhez.

## 2. Fordítás (Build)

### Miután a telepítés lefutott, a workspace gyökeréből fordítsd le a csomagokat:

cd ~/Desktop/ros2_ws
colcon build --symlink-install
source install/setup.bash

## 3. Projekt futtatása

### A main.launch.py futtatja mindkét alábbrendelt launch fájlt, melyek külön felelősek a SLAM és a szimuláció elindításáért

ros2 launch mgm_waffle main.launch.py

### Emellett, ha szeretnéd manuálisan mozgatni a robotot, akkor egy másik terminálban az alábbi sor futattásával megteheted:

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
