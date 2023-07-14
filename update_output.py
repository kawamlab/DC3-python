# このファイルの中身を試合が終わったあとにすぐ走らせるかどうかで悩んでます
import sys
import os
import json
import numpy as np

class Making():
    def __init__(self):
        self.dataset = {}
        self.my_team_speed_x = []
        self.my_team_speed_y = []
        self.my_team_angle = []
        self.your_team_speed_x = []
        self.your_team_speed_y = []
        self.your_team_angle = []
        self.my_team_score = []
        self.your_team_score = []
        self.shot = []
        self.free_fuard_zone_foul = []
        self.end = []

    def MakeDataSet(self):
        # このファイルのあるディレクトリをパスに追加
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        # 現在のスクリプトファイルのディレクトリを取得
        current_directory = os.path.dirname(os.path.abspath(__file__))
        target_directory = "dataset"
        directory_path = os.path.join(current_directory, target_directory)
        file_list = os.listdir(directory_path)
        for file_name in file_list:
            with open(directory_path + "/" + file_name, "r") as f:
                self.Containment(f)

            self.dataset["my_team_speed_x"] = self.my_team_speed_x
            self.dataset["my_team_speed_y"] = self.my_team_speed_y
            self.dataset["my_team_angle"] = self.my_team_angle
            self.dataset["your_team_speed_x"] = self.your_team_speed_x
            self.dataset["your_team_speed_y"] = self.your_team_speed_y
            self.dataset["your_team_angle"] = self.your_team_angle
            self.dataset["my_team_score"] = self.my_team_score
            self.dataset["your_team_score"] = self.your_team_score
            self.dataset["shot"] = self.shot
            self.dataset["free_fuard_zone_foul"] = self.free_fuard_zone_foul
            self.dataset["end"] = self.end

            f = open("dataset.json", "a")
            f.writelines(json.dumps(self.dataset, indent=4))
            f.close()

        # g = open("dataset.json", "r")
        # a = json.load(g)
        # print(f"a: {a}")
        # g.close()

        # for i in range(len(self.dataset)):
        #     f.writelines(json.dumps(self.dataset[i], indent=4))
        # f.close()

        #ここに本来はモデルを保存するけど今は練習
        # with open("dataset.pickle", "wb") as f:
        #     pickle.dump(self.dataset, f)
        #     f.close()

    def Containment(self, f):
        d = json.load(f)
        me_scores = []
        you_scores = []
        me_position = d["state"]["stones"]["team0"]
        you_position = d["state"]["stones"]["team1"]
        me_score = d["state"]["scores"]["team0"]
        you_score = d["state"]["scores"]["team1"]     

        for k in range(len(me_score)):
            me_scores.append(d["state"]["scores"]["team0"][k])
        for m in range(len(you_score)):
            you_scores.append(d["state"]["scores"]["team1"][m])
        self.my_team_speed_x.append(self.PositionX(me_position))
        self.my_team_speed_y.append(self.PositionY(me_position))
        self.my_team_angle.append(self.Angle(me_position))
        self.your_team_speed_x.append(self.PositionX(you_position))
        self.your_team_speed_y.append(self.PositionY(you_position))
        self.your_team_angle.append(self.Angle(you_position))
        self.my_team_score.append(self.Score(me_scores))
        self.your_team_score.append(self.Score(you_scores))
        self.shot.append(d["state"]["shot"])
        self.free_fuard_zone_foul.append(d["last_move"]["free_guard_zone_foul"])
        self.end.append(d["state"]["end"])

    def PositionX(self, position) -> list:
        pos_x = []
        for i in range(len(position)):
            if position[i]["position"]["x"] is None:
                pos_x.append(np.nan)
            else:
                pos_x.append(position[i]["position"]["x"])
        return pos_x

    def PositionY(self, position) -> list:
        pos_y = []
        for i in range(len(position)):
            if position[i]["position"]["y"] is None:
                pos_y.append(np.nan)
            else:
                pos_y.append(position[i]["position"]["y"])
        return pos_y
    
    def Angle(self, position) -> list:
        angle = []
        for i in range(len(position)):
            if position[i]["angle"] is None:
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