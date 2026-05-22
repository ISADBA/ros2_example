import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from dice_interfaces.action import DiceRoll


class DiceClient(Node):

    def __init__(self):
        super().__init__('dice_client')

        self._client = ActionClient(self, DiceRoll, 'dice_roll')

        self.goal_handle = None
        self.feedback_count = 0
        self.should_shutdown = False
        self.cancel_sent = False

        self.get_logger().info("🚀 DiceClient initialized")

    # -----------------------
    # Send Goal
    # -----------------------
    def send_goal(self, target):

        self.get_logger().info(f"📤 Waiting for server... target={target}")

        self._client.wait_for_server()

        goal = DiceRoll.Goal()
        goal.target_number = target

        self.get_logger().info("📤 Sending goal...")

        send_future = self._client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        send_future.add_done_callback(self.goal_response)

    # -----------------------
    # Goal Response
    # -----------------------
    def goal_response(self, future):

        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().error("❌ Goal rejected")
            self.should_shutdown = True
            return

        self.get_logger().info("✅ Goal accepted")

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    # -----------------------
    # Feedback
    # -----------------------
    def feedback_callback(self, msg):

        f = msg.feedback
        self.feedback_count += 1

        self.get_logger().info(
            f"📡 feedback #{self.feedback_count} "
            f"attempt={f.attempt} roll={f.current_number} msg={f.message}"
        )

        if f.message == "Very close!":
            self.get_logger().info("🔥 encouragement triggered")

        # -----------------------
        # CANCEL LOGIC
        # -----------------------
        
        if self.feedback_count >= 5 and not self.cancel_sent:

            if self.goal_handle is not None:
                self.cancel_sent = True
                self.get_logger().warn("🛑 Sending cancel request...")
                cancel_future = self.goal_handle.cancel_goal_async()
                cancel_future.add_done_callback(self.cancel_response)

    # -----------------------
    # Cancel Response
    # -----------------------
    def cancel_response(self, future):

        cancel_result = future.result()

        if len(cancel_result.goals_canceling) > 0:
            self.get_logger().warn("⚠️ Cancel accepted by server")
        else:
            self.get_logger().warn("⚠️ Cancel rejected")

    # -----------------------
    # Result
    # -----------------------
    def result_callback(self, future):

        result = future.result().result

        self.get_logger().info(
            f"🎯 FINAL RESULT: success={result.success}, "
            f"final={result.final_number}, attempts={result.attempts}"
        )

        # ❗ 不直接 shutdown
        self.should_shutdown = True


# -----------------------
# Main (SAFE SPIN LOOP)
# -----------------------
def main():

    rclpy.init()

    node = DiceClient()

    # CLI 参数支持
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 6

    node.send_goal(target)

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)

            if node.should_shutdown:
                break

    except KeyboardInterrupt:
        node.get_logger().info("Interrupted by user")

    finally:
        node.destroy_node()

        # ❗ 防止重复 shutdown crash
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
