import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from custom_topics.msg import PillarArray, Gate, GateArray
from topics.Custom_topics import RED, GREEN, GRAY, START, GOAL, INTERMEDIATE


def distance(a, b):
    return math.hypot(a.position.x - b.position.x,
                      a.position.y - b.position.y)


def pair_gray(pillars):
    """A kb. 1 meterre levo szurke oszlopok legjobb parositasa."""
    if len(pillars) % 2:
        return []

    def search(remaining):
        if not remaining:
            return [], 0.0

        a = remaining[0]
        best = None
        for i in range(1, len(remaining)):
            b = remaining[i]
            d = distance(a, b)
            if not 0.7 <= d <= 1.3:
                continue

            rest = search(remaining[1:i] + remaining[i + 1:])
            if rest is None:
                continue

            pairs, cost = rest
            candidate = [(a, b)] + pairs, cost + abs(d - 1.0)
            if best is None or candidate[1] < best[1]:
                best = candidate
        return best

    result = search(pillars)
    return result[0] if result is not None else []


class GateFinder(Node):
    def __init__(self):
        super().__init__('gate_finder')

        qos = QoSProfile(depth=1,
                         reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.publisher = self.create_publisher(GateArray, '/gates', qos)
        self.create_subscription(PillarArray, '/pillars', self.pillars_callback, qos)

    def make_gate(self, a, b, gate_type):
        gate = Gate()
        gate.type = gate_type
        gate.pose.position.x = (a.position.x + b.position.x) / 2
        gate.pose.position.y = (a.position.y + b.position.y) / 2
        angle = math.atan2(b.position.y - a.position.y,
                           b.position.x - a.position.x) + math.pi / 2
        gate.pose.orientation.z = math.sin(angle / 2)
        gate.pose.orientation.w = math.cos(angle / 2)
        return gate

    def pillars_callback(self, msg):
        if msg.header.frame_id != 'map':
            return

        red = [p for p in msg.pillars if p.color == RED]
        green = [p for p in msg.pillars if p.color == GREEN]
        gray = [p for p in msg.pillars if p.color == GRAY]

        result = GateArray()
        result.header = msg.header

        if len(red) == 2 and 0.7 <= distance(*red) <= 1.3:
            result.gates.append(self.make_gate(red[0], red[1], START))
        if len(green) == 2 and 0.7 <= distance(*green) <= 1.3:
            result.gates.append(self.make_gate(green[0], green[1], GOAL))
        for a, b in pair_gray(gray):
            result.gates.append(self.make_gate(a, b, INTERMEDIATE))

        self.publisher.publish(result)


def main(args=None):
    rclpy.init(args=args)
    node = GateFinder()
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
