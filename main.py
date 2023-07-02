from practice import SocketClient


if __name__ == "__main__":
    cli = SocketClient()

    my_team = cli.get_my_team()
    cli.logger.info(f"my_team :{my_team}")

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

    update_list, trajectory = cli.get_update_and_trajectory(remove_trajectory=True)
    # update = cli.update_to_json(update_list)
    trajectory = cli.trajectory_to_json(trajectory)
    print(trajectory)
    # f=open("Trajectory_Data1.json", "w", encoding="UTF-8")
    # f.writelines(rec.to_json(trajectory_data))
    # f.close()
