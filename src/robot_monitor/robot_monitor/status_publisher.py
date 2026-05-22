import random

import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class StatusPublisher(Node):

    def __init__(self):
        super().__init__('status_publisher')

        self.publisher_ = self.create_publisher(
            String,
            'robot_status',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_status
        )

        self.get_logger().info('Status Publisher Started')

    def publish_status(self):

        battery = random.randint(60, 100)
        temperature = random.randint(30, 50)
        speed = round(random.uniform(0.0, 1.5), 2)

        status = (
            f'Battery={battery}% | '
            f'Temp={temperature}C | '
            f'Speed={speed}m/s'
        )

        msg = String()
        msg.data = status

        self.publisher_.publish(msg)

        self.get_logger().info(f'Published: {status}')


def main(args=None):

    rclpy.init(args=args)

    node = StatusPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
