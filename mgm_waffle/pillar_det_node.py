import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from rclpy.time import Time

from geometry_msgs.msg import PointStamped
from sensor_msgs.msg import LaserScan, Image, CameraInfo
from tf2_ros import Buffer, TransformListener, TransformException
from tf2_geometry_msgs import do_transform_point
from custom_topics.msg import Pillar, PillarArray

from topics.Custom_topics import RED, GREEN, GRAY, UNKNOWN
from .detection import detect_pillars


class PillarDetector(Node):
    def __init__(self):
        super().__init__('pillar_det_node')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        qos = QoSProfile(depth=1,
                         reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.publisher = self.create_publisher(PillarArray, '/pillars', qos)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, qos_profile_sensor_data)
        self.create_subscription(CameraInfo, '/camera/camera_info', self.info_callback,
                                 qos_profile_sensor_data)

        self.pillars = []
        self.camera_frame = ''
        self.fx = self.fy = self.cx = self.cy = None

    def info_callback(self, msg):
        if msg.k[0] > 0 and msg.k[4] > 0:
            self.fx, self.fy = msg.k[0], msg.k[4]
            self.cx, self.cy = msg.k[2], msg.k[5]
            self.camera_frame = msg.header.frame_id

    def scan_callback(self, msg):
        try:
            transform = self.tf_buffer.lookup_transform(
                'map', msg.header.frame_id, Time.from_msg(msg.header.stamp))
        except TransformException:
            return

        for x, y in detect_pillars(msg):
            point = PointStamped()
            point.header = msg.header
            point.point.x = x
            point.point.y = y
            point_map = do_transform_point(point, transform).point

            closest = None
            distance = 0.25
            for pillar in self.pillars:
                d = math.hypot(pillar['x'] - point_map.x, pillar['y'] - point_map.y)
                if d < distance:
                    closest = pillar
                    distance = d

            if closest is None:
                self.pillars.append({'x': point_map.x, 'y': point_map.y, 'color': UNKNOWN})
            else:
                closest['x'] = 0.7 * closest['x'] + 0.3 * point_map.x
                closest['y'] = 0.7 * closest['y'] + 0.3 * point_map.y

        self.publish_pillars()

    def image_callback(self, msg):
        if self.fx is None or not self.camera_frame:
            return
        if msg.encoding.lower() not in ('rgb8', 'bgr8', 'rgba8', 'bgra8'):
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                self.camera_frame, 'map', Time.from_msg(msg.header.stamp))
        except TransformException:
            return

        changed = False
        for pillar in self.pillars:
            point = PointStamped()
            point.header.frame_id = 'map'
            point.header.stamp = msg.header.stamp
            point.point.x = pillar['x']
            point.point.y = pillar['y']
            point.point.z = 0.25
            p = do_transform_point(point, transform).point

            if p.z <= 0:
                continue
            u = round(self.fx * p.x / p.z + self.cx)
            v = round(self.fy * p.y / p.z + self.cy)
            color = self.pixel_color(msg, u, v)

            if color is not None:
                # A felismerheto szines oszlop felulirhatja a szurke becslest.
                if pillar['color'] in (UNKNOWN, GRAY) or color in (RED, GREEN):
                    if pillar['color'] != color:
                        pillar['color'] = color
                        changed = True

        if changed:
            self.publish_pillars()

    @staticmethod
    def pixel_color(msg, u, v):
        if u < 4 or v < 4 or u + 4 >= msg.width or v + 4 >= msg.height:
            return None

        encoding = msg.encoding.lower()
        channels = 4 if 'a8' in encoding else 3
        bgr = encoding.startswith('bgr') or encoding.startswith('bgra')
        red = green = gray = 0

        for y in range(v - 4, v + 5):
            for x in range(u - 4, u + 5):
                i = y * msg.step + x * channels
                if bgr:
                    b, g, r = msg.data[i], msg.data[i + 1], msg.data[i + 2]
                else:
                    r, g, b = msg.data[i], msg.data[i + 1], msg.data[i + 2]

                if r > 70 and r > 1.6 * g and r > 1.6 * b:
                    red += 1
                elif g > 70 and g > 1.6 * r and g > 1.6 * b:
                    green += 1
                elif 35 <= (r + g + b) / 3 <= 220 and max(r, g, b) - min(r, g, b) < 30:
                    gray += 1

        if red >= 13 and red > green:
            return RED
        if green >= 13 and green > red:
            return GREEN
        if gray >= 45:
            return GRAY
        return None

    def publish_pillars(self):
        result = PillarArray()
        result.header.frame_id = 'map'
        result.header.stamp = self.get_clock().now().to_msg()

        for p in self.pillars:
            pillar = Pillar()
            pillar.position.x = p['x']
            pillar.position.y = p['y']
            pillar.color = p['color']
            result.pillars.append(pillar)

        self.publisher.publish(result)


def main(args=None):
    rclpy.init(args=args)
    node = PillarDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
