## 1. Előfeltételek és Környezet beállítása

### A külső függőségek automatikus telepítéséhez futtasd az `install_dependencies.sh` az alábbi parancsokkal Terminátorban:

```bash
cd ~/Desktop/ros2_ws/src/MGM_WAFFLE
bash install_dependencies.sh
```

A script elvégzi az alábbiakat:
1. Telepíti a szükséges `apt` csomagokat 
2. Klónozza a [mrtsp_exploration_ros2] csomagot
3. Futtatja a `rosdep` ellenőrzést az esetleges további csomagfüggőségekhez.

Ha nem fut le:
1. Nyisd meg a fájlt VS Code-ban:
```bash
code install_dependencies.sh
```
2. Nézd meg a VS Code jobb alsó sarkában az állapotsort.
3. Ha ott CRLF felirat látható, kattints rá, és válaszd ki a felugró menüből az LF lehetőséget.
4. Mentsd el a fájlt (Ctrl + S) és futtasd újra a `bash install_dependencies.sh` parancsot.

Ha még mindig nem fut le, akkor az alábbi parancsokat futtasd le:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/Desktop/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 2. Fordítás (Build)

### Miután a telepítés lefutott, a workspace gyökeréből fordítsd le a csomagokat:

```bash
cd ~/Desktop/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### FONTOS: Ha már futtatad egyszer a teljes buildet, de újra akarsz buildelni, akkor célszerű az alábbi verziót használni!

```bash
colcon build --symlink-install --packages-select mgm_waffle
```

## 3. Projekt futtatása

### A main.launch.py futtatja mindkét alábbrendelt launch fájlt, melyek külön felelősek a SLAM és a szimuláció elindításáért

```bash
ros2 launch mgm_waffle main.launch.py
```


### Emellett, ha szeretnéd manuálisan mozgatni a robotot, akkor egy másik terminálban az alábbi sor futattásával megteheted:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```