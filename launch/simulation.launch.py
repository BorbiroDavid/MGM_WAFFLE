#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_mgm_waffle = get_package_share_directory('mgm_waffle')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_gz_client = LaunchConfiguration('use_gz_client', default='false')
    use_rviz = LaunchConfiguration('use_rviz', default='true')

    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')
    z_pose = LaunchConfiguration('z_pose', default='0.01')

    default_world = os.path.join(pkg_mgm_waffle, 'world', 'hf.world')
    world = LaunchConfiguration('world', default=default_world)

    default_rviz_config = os.path.join(pkg_mgm_waffle, 'rviz', 'waffle.rviz')
    rviz_config = LaunchConfiguration('rviz_config', default=default_rviz_config)

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true', description='Use simulation clock'
    )
    declare_use_gz_client_cmd = DeclareLaunchArgument(
        'use_gz_client', default_value='false', description='Start Gazebo UI client'
    )
    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz', default_value='true', description='Start RViz2'
    )
    declare_x_pose_cmd = DeclareLaunchArgument(
        'x_pose', default_value='-2.0', description='Robot initial x pose'
    )
    declare_y_pose_cmd = DeclareLaunchArgument(
        'y_pose', default_value='-0.5', description='Robot initial y pose'
    )
    declare_world_cmd = DeclareLaunchArgument(
        'world', default_value=default_world, description='World file path'
    )
    declare_rviz_config_cmd = DeclareLaunchArgument(
        'rviz_config', default_value=default_rviz_config, description='RViz config file path'
    )

    # Gazebo backend
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v2 ', world], 'on_exit_shutdown': 'true'}.items()
    )

    # Gazebo UI
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-g -v2 ', 'on_exit_shutdown': 'true'}.items(),
        condition=IfCondition(use_gz_client)
    )

    # Robot state publisher (URDF -> TF)
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # Robot spawn
    model_path = os.path.join(pkg_mgm_waffle, 'models', 'waffle_kamera_nelkul.sdf')
    spawn_turtlebot_cmd = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'waffle',
            '-file', model_path,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose
        ],
        output='screen'
    )

    # Gazebo-ROS bridge
    bridge_config_path = os.path.join(pkg_mgm_waffle, 'params', 'bridge.yaml')
    bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_config_path}'],
        output='screen'
    )

    # RViz2
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(use_rviz)
    )

    set_tb3_model = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle')
    set_env_resources = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.join(pkg_tb3_gazebo, 'models')
    )
    set_env_local = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', os.path.join(pkg_mgm_waffle, 'models')
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_gz_client_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_x_pose_cmd)
    ld.add_action(declare_y_pose_cmd)
    ld.add_action(declare_world_cmd)
    ld.add_action(declare_rviz_config_cmd)

    ld.add_action(set_tb3_model)
    ld.add_action(set_env_resources)
    ld.add_action(set_env_local)
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_turtlebot_cmd)
    ld.add_action(bridge_cmd)
    ld.add_action(rviz_cmd)

    return ld
