#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_mgm_waffle = get_package_share_directory('mgm_waffle')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_gz_client = LaunchConfiguration('use_gz_client', default='false')
    use_rviz = LaunchConfiguration('use_rviz', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

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
        'x_pose', default_value='-2.0', description='Initial robot X pose'
    )
    declare_y_pose_cmd = DeclareLaunchArgument(
        'y_pose', default_value='-0.5', description='Initial robot Y pose'
    )

    simulation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_mgm_waffle, 'launch', 'simulation.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_gz_client': use_gz_client,
            'use_rviz': use_rviz,
            'x_pose': x_pose,
            'y_pose': y_pose
        }.items()
    )

    slam_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_mgm_waffle, 'launch', 'slam.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_gz_client_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_x_pose_cmd)
    ld.add_action(declare_y_pose_cmd)

    ld.add_action(simulation_cmd)
    ld.add_action(slam_cmd)

    return ld
