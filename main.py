from recursion import Recursion
from dataclasses import is_dataclass
from practice import SocketClient


learning = []
trajectory_data = []
update_data = []
obj_dict = {}


if __name__ == "__main__":
    cli = SocketClient()
    rec = Recursion()
    dc = cli.dc_recv()
    re = True

    cli.dc_ok()  # dc_okを送信

    is_ready = cli.is_ready_recv()  # is_readyを読み取るための受信

    my_team = cli.match_setting.team
    cli.logger.info(f"my_team :{my_team}")
    cli.ready_ok()  # ready_okを送信

    new_game = cli.get_new_game()
    update_data.append(dc)
    update_data.append(is_ready)
    update_data.append(new_game)

    # id = cmd(dict_data.get("cmd"), dict_data.get("last_move"), dict_data.get("next_team"))
    # cli.logger.info(f"id : {id.next_team}")
    while True:
        update = cli.update()
        # cli.logger.info(f"update_data : {update_data[0]}")
        update_data.append(update[0])
        trajectory_data.append(update[1])
        next_team = cli.update_info.next_team
        if cli.update_info.state.game_result.winner is not None:
            if my_team == cli.update_info.state.game_result.winner:
                cli.logger.info("WIN")
            else:
                cli.logger.info("LOSE")
            break
        if my_team == next_team:
            cli.move()
        else:
            continue

    rec.to_json(update_data[1], re)
    # f=open("Trajectory_Data1.json", "w", encoding="UTF-8")
    # f.writelines(rec.to_json(trajectory_data))
    # f.close()
