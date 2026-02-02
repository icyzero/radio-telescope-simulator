from src.controller.telescope import Telescope

def test_command_queue_executes_in_order():
    telescope = Telescope(slew_rate=10.0)
    telescope.move_to(10,10)
    telescope.move_to(20,20)
    telescope.move_to(30,30)

    for _ in range(1000):
        telescope.update(dt=0.1)
        if telescope.command_queue == [] and telescope.state == "IDLE":
            break

    assert abs(telescope.alt - 30) < 0.1
    assert abs(telescope.az - 30) < 0.1
    assert telescope.command_queue == []

if __name__ == "__main__":
    test_command_queue_executes_in_order()