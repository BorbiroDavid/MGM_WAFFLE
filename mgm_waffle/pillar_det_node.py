#!/usr/bin/env python3
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

# Szükséges ROS 2 üzenetosztályok importálása
from custom_topics.msg import Pillar
from geometry_msgs.msg import Pose

class CustomTopics(Node):
    def __init__(self):
        super().__init__('custom_topics_node')
        # Publisher létrehozása a /pillars topicra az egyedi típussal
        self.pillars_publisher = self.create_publisher( Pillar, '/pillars',10)

        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('CustomTopics node elindult, a /pillars topic kész.')

    def publish_pillars(self, poses_tuple: tuple, colors_tuple: tuple):
        msg = Pillar()
        # A Python tuple adatokat listaként rendeljük az üzenet tömb mezőihez
        msg.poses = list(poses_tuple)
        msg.colors = list(colors_tuple)
        self.pillars_publisher.publish(msg)
        self.get_logger().info(f'Publikálva: {len(msg.poses)} db oszlop a /pillars topicon.')

    def timer_callback(self):
        # Tesztadatok összeállítása
        p1 = Pose()
        p1.position.x, p1.position.y, p1.position.z = 1.45, 0.32, 0.0
        p2 = Pose()
        p2.position.x, p2.position.y, p2.position.z = 2.80, -0.75, 0.0
        teszt_poziciok = (p1, p2)
        teszt_szinek = ('red', 'blue')
        self.publish_pillars(teszt_poziciok, teszt_szinek)

def main(args=None):
    rclpy.init(args=args)
    node = CustomTopics()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
if __name__ == '__main__':
    main()