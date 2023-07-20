import json
import pathlib

from dc3client import SocketClient

if __name__ == "__main__":
    cli = SocketClient(rate_limit=2.0)

    log_dir = pathlib.Path("logs")

    remove_trajectory = True

    my_team = cli.get_my_team()
    cli.logger.info(f"my_team :{my_team}")

    dc = cli.get_dc()
    dc_message = cli.convert_dc(dc)
    is_ready = cli.get_is_ready()
    is_ready_message = cli.convert_is_ready(is_ready)

    # id = cmd(dict_data.get("cmd"), dict_data.get("last_move"), dict_data.get("next_team"))
    # cli.logger.info(f"id : {id.next_team}")
    while True:
        cli.update()
        match_data = cli.get_match_data()

        if (winner := cli.get_winner()) is not None:
            # game end
            if my_team == winner:
                cli.logger.info("WIN")
            else:
                cli.logger.info("LOSE")
            break

        next_team = cli.get_next_team()

        if my_team == next_team:
            cli.move()
        else:
            continue

    move_info = cli.get_move_info()
    update_list, trajectory_list = cli.get_update_and_trajectory(remove_trajectory)

    update = cli.convert_update(update_list[0], remove_trajectory)

    with open("data_x.json", "w", encoding="UTF-8") as f:
        json.dump(update, f, indent=4)
