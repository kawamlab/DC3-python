from practice import SocketClient
from dataclasses import dataclass, asdict 
import json
learning = []


if __name__ == "__main__":
    cli = SocketClient()
    cli.dc_recv()
    cli.dc_ok() #dc_okを送信

    cli.is_ready_recv()   #is_readyを読み取るための受信
    myteam = cli.match_setting.team
    cli.logger.info(f"myteam :{myteam}")
    cli.ready_ok() #ready_okを送信

    cli.new_game()
    dc_info = json.dumps(asdict(cli.dc))
    isready_info = json.dumps(asdict(cli.match_setting))
    newgame_info = json.dumps(asdict(cli.newgame))

    # id = cmd(dict_data.get("cmd"), dict_data.get("last_move"), dict_data.get("next_team"))
    # cli.logger.info(f"id : {id.next_team}")
    while True:
        cli.update()
        nextteam = cli.updateinfo.next_team
        learning.append(json.dumps(asdict(cli.updateinfo)))
        # cli.logger.info(f"nextteam : {nextteam}")
        # cli.logger.info(f"learning : {learning}")
        if myteam == nextteam:
            cli.move()
        if cli.updateinfo.state.game_result != None:

            break
    f = open("learning_data1.json", "a", encoding="UTF-8")
    f.writelines(str(learning))
    f.close()