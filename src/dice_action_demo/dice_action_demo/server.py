import random
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from dice_interfaces.action import DiceRoll


class DiceServer(Node):

    def __init__(self):
        super().__init__('dice_server')

        self._callback_group = ReentrantCallbackGroup()

        self._server = ActionServer(
            self,
            DiceRoll,
            'dice_roll',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self._callback_group,
        )

        self.get_logger().info('dice server ready')

    def goal_callback(self, goal_request):
        target = goal_request.target_number
        self.get_logger().info(f'goal request received: target={target}')

        if target < 1 or target > 6:
            self.get_logger().warn(f'reject invalid target={target}')
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('cancel request received')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        target = goal_handle.request.target_number
        attempt = 0
        result = DiceRoll.Result()

        self.get_logger().info(f'start executing goal: target={target}')

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.get_logger().info(f'goal canceled at attempt={attempt}')
                goal_handle.canceled()

                result.success = False
                result.final_number = 0
                result.attempts = attempt
                return result

            attempt += 1
            roll = random.randint(1, 6)

            self.get_logger().info(
                f'attempt={attempt}, roll={roll}, target={target}'
            )

            feedback = DiceRoll.Feedback()
            feedback.current_number = roll
            feedback.attempt = attempt

            if hasattr(feedback, 'message'):
                feedback.message = 'Very close!' if abs(roll - target) == 1 else ''

            goal_handle.publish_feedback(feedback)

            if roll == target:
                self.get_logger().info(f'goal succeeded at attempt={attempt}')
                goal_handle.succeed()

                result.success = True
                result.final_number = roll
                result.attempts = attempt
                return result

            time.sleep(1)

        self.get_logger().warn('shutdown before goal completed')
        goal_handle.abort()
        result.success = False
        result.final_number = 0
        result.attempts = attempt
        return result

    def destroy(self):
        self._server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DiceServer()
    executor = MultiThreadedExecutor()

    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('server interrupted by user')
    finally:
        executor.shutdown()
        node.destroy()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
