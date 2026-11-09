#!/usr/bin/env bash
# ==============================================================================
# MGM_WAFFLE - Függőségtelepítő és környezetbeállító script
# Cél: Rendszerfüggőségek telepítése (Nav2, SLAM Toolbox, RViz2, Gazebo)
#      és külső csomagok (mrtsp_exploration_ros2) letöltése a munkakörnyezetbe.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_SRC_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WS_ROOT_DIR="$(cd "${WS_SRC_DIR}/.." && pwd)"

echo "=========================================================="
echo " MGM_WAFFLE: Függőségek telepítése (ROS 2 Jazzy)"
echo " Munkakönyvtár: ${WS_ROOT_DIR}"
echo " Forráskönyvtár: ${WS_SRC_DIR}"
echo "=========================================================="

# 1. Rendszercsomagok (APT) frissítése és telepítése
echo ""
echo "[1/4] APT csomaglista frissítése és szükséges csomagok telepítése..."
sudo apt update

PACKAGES=(
    ros-jazzy-navigation2
    ros-jazzy-nav2-bringup
    ros-jazzy-slam-toolbox
    ros-jazzy-rviz2
    ros-jazzy-ros-gz
    ros-jazzy-ros-gz-sim
    ros-jazzy-turtlebot3-gazebo
    ros-jazzy-turtlebot3-msgs
    python3-pip
    git
)

echo "Csomagok telepítése: ${PACKAGES[*]}"
sudo apt install -y "${PACKAGES[@]}"

# 2. Külső forráskódú csomagok letöltése
# mrtsp_exploration_ros2: Frontier-alapú autonóm felderítés Nav2 támogatással
echo ""
echo "[2/4] Külső csomagok ellenőrzése és klónozása..."

MRTSP_DIR="${WS_SRC_DIR}/mrtsp_exploration_ros2"
if [ ! -d "${MRTSP_DIR}" ]; then
    echo "-> mrtsp_exploration_ros2 klónozása ide: ${MRTSP_DIR}..."
    git clone https://github.com/mertgulerx/mrtsp_exploration_ros2.git "${MRTSP_DIR}"
else
    echo "-> mrtsp_exploration_ros2 már létezik (${MRTSP_DIR}), frissítés lekérése..."
    git -C "${MRTSP_DIR}" pull || true
fi

# 3. Rosdep függőségek ellenőrzése és telepítése
echo ""
echo "[3/4] Rosdep függőségek feloldása a workspace-ben..."
if command -v rosdep &> /dev/null; then
    rosdep update || true
    rosdep install --from-paths "${WS_SRC_DIR}" --ignore-src -r -y || true
else
    echo "Figyelem: a rosdep nincs telepítve vagy inicializálva, ez a lépés kimarad."
fi

# 4. Kész, útmutató a fordításhoz
echo ""
echo "=========================================================="
echo " [4/4] Telepítés sikeresen befejeződött!"
echo " A workspace fordításához futtasd az alábbi parancsokat:"
echo ""
echo "   cd ${WS_ROOT_DIR}"
echo "   colcon build --symlink-install"
echo "   source install/setup.bash"
echo "=========================================================="
