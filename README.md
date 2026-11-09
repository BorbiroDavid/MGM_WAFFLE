# MGM_WAFFLE - Autonomous Exploration & Navigation

Ez a repository a csoportos projekt forráskódját és konfigurációit tartalmazza ROS 2 Jazzy környezetben, TurtleBot3 Waffle robot és Gazebo Sim (`ros_gz_sim`) használatával.

## 1. Előfeltételek és Környezet beállítása

A külső függőségek (Nav2, SLAM Toolbox, szimuláció) és a felderítő csomag (`mrtsp_exploration_ros2`) automatikus telepítéséhez futtasd az `install_dependencies.sh` scriptet a Docker konténer termináljában:

```bash
cd ~/ros2_ws/src/MGM_WAFFLE
bash install_dependencies.sh
```

> **Megjegyzés:** Windows alól megosztott (mounted) köteteknél nem szükséges és a Windows fájlrendszer korlátai miatt nem is mindig engedélyezett a `chmod +x` futtatási jog állítása, a fenti `bash install_dependencies.sh` közvetlen interpreter hívás azonnal lefut.

A script elvégzi az alábbiakat:
1. Telepíti a szükséges `apt` csomagokat (`ros-jazzy-navigation2`, `ros-jazzy-slam-toolbox`, `ros-jazzy-ros-gz-sim`, stb.).
2. Klónozza a [mrtsp_exploration_ros2](https://github.com/mertgulerx/mrtsp_exploration_ros2) csomagot a `ros2_ws/src/` mappába a projekt mellé.
3. Futtatja a `rosdep` ellenőrzést az esetleges további csomagfüggőségekhez.

## 2. Fordítás (Build)

Miután a telepítés lefutott, a workspace gyökeréből fordítsd le a csomagokat:

```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 3. Tervezett Architektúra

* **Szimuláció:** `ros_gz_sim` + TurtleBot3 Waffle
* **Térképezés (SLAM):** `slam_toolbox` (online aszinkron mód, valós idejű `/map` készítés)
* **Navigáció:** `navigation2` (Nav2 stack costmap és path planning rétegei)
* **Autonóm felderítés:** `mrtsp_exploration_ros2` (frontier-alapú pontválasztás és célkitűzés)
* **Megjelenítés:** `rviz2` előre konfigurált nézettel
