import json
import numpy as np
import pathlib
# team0を自分のチームとして、team1を相手のチームとして扱う


class ReadFile:

    def read_file(self, f, i):
        dataset = {}
        my_team_speed_x = []
        my_team_speed_y = []
        my_team_angle = []
        your_team_speed_x = []
        your_team_speed_y = []
        your_team_angle = []
        my_team_position_x = []
        my_team_position_y = []
        my_team_position_angle = []
        your_team_position_x = []
        your_team_position_y = []
        your_team_position_angle = []
        my_team_scores = []
        your_team_scores = []
        shot = []
        free_fuard_zone_foul = []
        end = []

        with open(f, "r") as f:
            lines = f.readlines()

        lines = [line.strip() for line in lines]

        for line in lines:
            data = json.loads(line)
            log_data = data["log"]

            if log_data["cmd"] == "update":
                me_position = log_data["state"]["stones"]["team0"]
                you_position = log_data["state"]["stones"]["team1"]
                me_score = log_data["state"]["scores"]["team0"]
                you_score = log_data["state"]["scores"]["team1"]
                my_team_position_x.append(self.PositionX(me_position))
                my_team_position_y.append(self.PositionY(me_position))
                my_team_position_angle.append(self.Angle(me_position))
                your_team_position_x.append(self.PositionX(me_position))
                your_team_position_y.append(self.PositionY(you_position))
                your_team_position_angle.append(self.Angle(you_position))
                my_team_scores.append(self.Score(me_score))
                your_team_scores.append(self.Score(you_score))
                shot.append(log_data["state"]["shot"])

                if log_data["last_move"] is None:
                    free_fuard_zone_foul.append(False)
                else:
                    free_fuard_zone_foul.append(log_data["last_move"]["free_guard_zone_foul"])

                end.append(log_data["state"]["end"])

                if log_data["cmd"] == "move":
                    if log_data["team"] == "team0":
                        my_team_speed_x.append(log_data["move"]["velocity"]["x"])
                        my_team_speed_y.append(log_data["move"]["velocity"]["y"])
                        my_team_angle.append(log_data["move"]["rotation"])
                    elif log_data["team"] == "team1":
                        your_team_speed_x.append(log_data["move"]["velocity"]["x"])
                        your_team_speed_y.append(log_data["move"]["velocity"]["y"])
                        your_team_angle.append(log_data["move"]["rotation"])

            dataset["my_team_position_y"] = my_team_position_y
            dataset["my_team_position_angle"] = my_team_position_angle
            dataset["your_team_position_x"] = your_team_position_x
            dataset["your_team_position_y"] = your_team_position_y
            dataset["my_team_position_x"] = my_team_position_x
            dataset["your_team_position_angle"] = your_team_position_angle
            dataset["my_team_speed_x"] = my_team_position_x
            dataset["my_team_speed_y"] = my_team_position_y
            dataset["my_team_angle"] = my_team_position_angle
            dataset["your_team_speed_x"] = your_team_position_x
            dataset["your_team_speed_y"] = your_team_position_y
            dataset["your_team_angle"] = your_team_position_angle
            dataset["my_team_scores"] = my_team_scores
            dataset["your_team_scores"] = your_team_scores
            dataset["shot"] = shot
            dataset["free_fuard_zone_foul"] = free_fuard_zone_foul
            dataset["end"] = end

        file_name = "dataset" + str(i) + ".json"
        dataset_path = pathlib.Path(__file__).parent.joinpath("dataset")
        with open(dataset_path.joinpath(dataset_path, file_name), "a") as f:
            json.dump(dataset, f, indent=4)


    def PositionX(self, position) -> list:
        pos_x = []
        for i in range(len(position)):
            if position[i] is None:
                pos_x.append(np.nan)
            else:
                pos_x.append(position[i]["position"]["x"])
        return pos_x

    def PositionY(self, position) -> list:
        pos_y = []
        for i in range(len(position)):
            if position[i] is None:
                pos_y.append(np.nan)
            else:
                pos_y.append(position[i]["position"]["y"])
        return pos_y

    def Angle(self, position) -> list:
        angle = []
        for i in range(len(position)):
            if position[i] is None:
                angle.append(np.nan)
            else:
                angle.append(position[i]["angle"])
        return angle

    def Score(self, score) -> list:
        scores = []
        for i in range(len(score)):
            if score[i] is None:
                scores.append(np.nan)
            else:
                scores.append(score[i])
        return scores


if __name__ == '__main__':
    read_file = ReadFile()
    upper_dir = pathlib.Path(__file__).parent
    data_dir = upper_dir.joinpath("data")
    contents = list(data_dir.glob("**/*.dcl2"))
    for content in contents:
        read_file.read_file(content, contents.index(content))

    
