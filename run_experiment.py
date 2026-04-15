from src.orchestrator.run_experiment import Orchestrator

if __name__ == "__main__":

    tasks = ["coin_collector", "light_switch_controller", "door_unlocker", "package_delivery", "patrolling_guard_alert", "buyer_seller_negotiation", "edit_light_switch_add_turn_off", "edit_door_unlock_then_lock", "edit_coin_collector_collect_three", "edit_box_pickup_then_place", "edit_traffic_light_add_yellow_phase", "edit_courier_deliver_then_return", "edit_sender_receiver_add_ack", "edit_patrol_two_points_then_report"]

    orchestrator = Orchestrator()

    for task in tasks:
        orchestrator.run_experiment(task)

