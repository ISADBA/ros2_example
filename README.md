# 编译
cd ~/ros2_ws
rm -rf build install log
colcon build --symlink-install
source install/setup.bash


