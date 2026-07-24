from src.controller.telescope import Telescope

def test_telescope_reaches_target():
    telescope = Telescope(slew_rate=10.0)
    telescope.move_to(30, 120)

    for _ in range(500):
        telescope.update(dt=0.1)
        print(f"[UPDATE] Alt={telescope.alt:.2f},Az={telescope.az:.2f}")

        if telescope.is_target_reached():
            print("[STATE] Target reached")
            break

    print("DONE")
    assert abs(telescope.alt - 30) < 0.1
    assert abs(telescope.az - 120) < 0.1
    
if __name__ == "__main__":
    test_telescope_reaches_target()
