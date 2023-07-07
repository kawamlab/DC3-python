from practice import SocketClient
import json


if __name__ == "__main__":
    cli = SocketClient()
    remove_trajectory = True

    my_team = cli.get_my_team()
    cli.logger.info(f"my_team :{my_team}")
    dc = cli.match_data.server_dc
    dc_message = cli.dc_convert(dc)
    is_ready = cli.match_data.is_ready
    is_ready_message = cli.is_ready_convert(is_ready)

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

    move_info_x = cli.move_info_x
    move_info_y = cli.move_info_y
    move_info_angle = cli.move_info_angle
    update_list, trajectory_list = cli.get_update_and_trajectory(remove_trajectory)
    # update = cli.update_to_json(update_list)
    # trajectory = cli.trajectory_to_json(trajectory_list)
    # print(f"trajectory : {trajectory_list[0]}")
    update = cli.update_convert(update_list[1], remove_trajectory)
    # trajectory = cli.trajectory_convert(trajectory_list[0])
    f=open("data_x.json", "w", encoding="UTF-8")
    # f.writelines(json.dumps(dc_message, indent=0))
    # f.writelines(json.dumps(is_ready_message, indent=0))
    f.writelines(json.dumps(move_info_x, indent=0))
    f.writelines(json.dumps(move_info_y, indent=0))
    f.writelines(json.dumps(move_info_angle, indent=0))
    # f.writelines(json.dumps(update, indent=0))
    # f.writelines(json.dumps(trajectory, indent=4))
    f.close()
