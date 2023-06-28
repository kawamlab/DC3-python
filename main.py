from recursion import Recursion

from practice import SocketClient

learning = []


if __name__ == "__main__":
    cli = SocketClient()
    rec = Recursion()
    cli.dc_recv()
    cli.dc_ok()  # dc_okを送信

    cli.is_ready_recv()  # is_readyを読み取るための受信
    my_team = cli.match_setting.team
    cli.logger.info(f"my_team :{my_team}")
    cli.ready_ok()  # ready_okを送信

    cli.get_new_game()

    # id = cmd(dict_data.get("cmd"), dict_data.get("last_move"), dict_data.get("next_team"))
    # cli.logger.info(f"id : {id.next_team}")
    while True:
        cli.update()
        next_team = cli.update_info.next_team
        # cli.logger.info(f"next_team : {next_team}")
        # cli.logger.info(f"learning : {learning}")
        cli.logger.info(my_team == next_team)
        if my_team == next_team:
            cli.move()
        else:
            continue
        if cli.update_info.state.game_result.winner is not None:
            cli.logger.info(f"game_result : {cli.update_info.state.game_result}")
            break
    # f = open("learning_data2.json", "a", encoding="UTF-8")
    # f.writelines(str(learning))
    # f.close()
