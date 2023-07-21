# このファイルの中身を試合が終わったあとにすぐ走らせるかどうかで悩んでます
import json
import os
import pathlib
import sys

import numpy as np


class ServerLog:
    def __init__(self):
        self.dataset = {}
        self.team1_speed_x = []
        self.team1_speed_y = []
        self.team1_angle = []
        self.team2_speed_x = []
        self.team2_speed_y = []
        self.team2_angle = []
        self.team1_score = []
        self.team2_score = []
        self.shot = []
        self.free_fuard_zone_foul = []
        self.end = []

    def load(self, logfile_path: pathlib.Path):
        # # このファイルのあるディレクトリをパスに追加
        # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        # # 現在のスクリプトファイルのディレクトリを取得
        # current_directory = os.path.dirname(os.path.abspath(__file__))
        # target_directory = "dataset"
        # directory_path = os.path.join(current_directory, target_directory)
        # file_list = os.listdir(directory_path)

        if logfile_path.suffix != ".dcl2":
            raise ValueError(f"Invalid suffix: {logfile_path.suffix}")

        with open(logfile_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("#"):
                    continue
                d = json.loads(line)
                self.parse_server_log(d)

        self.dataset["team1_speed_x"] = self.team1_speed_x
        self.dataset["team1_speed_y"] = self.team1_speed_y
        self.dataset["team1_angle"] = self.team1_angle
        self.dataset["team2_speed_x"] = self.team2_speed_x
        self.dataset["team2_speed_y"] = self.team2_speed_y
        self.dataset["team2_angle"] = self.team2_angle
        self.dataset["team1_score"] = self.team1_score
        self.dataset["team2_score"] = self.team2_score
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

        # ここに本来はモデルを保存するけど今は練習
        # with open("dataset.pickle", "wb") as f:
        #     pickle.dump(self.dataset, f)
        #     f.close()

    def parse_server_log(self, data: dict):
        me_scores = []
        you_scores = []
        team1_position = data["state"]["stones"]["team0"]
        team2_position = data["state"]["stones"]["team1"]
        me_score = data["state"]["scores"]["team0"]
        you_score = data["state"]["scores"]["team1"]

        for k in range(len(me_score)):
            me_scores.append(data["state"]["scores"]["team0"][k])
        for m in range(len(you_score)):
            you_scores.append(data["state"]["scores"]["team1"][m])
        self.team1_speed_x.append(
            [np.nan if p["position"]["x"] is None else p["position"]["x"] for p in team1_position]
        )
        self.team1_speed_y.append(
            [np.nan if p["position"]["y"] is None else p["position"]["y"] for p in team1_position]
        )
        self.team1_angle.append([np.nan if p["angle"] is None else p["angle"] for p in team1_position])
        self.team2_speed_x.append(
            [np.nan if p["position"]["x"] is None else p["position"]["x"] for p in team2_position]
        )
        self.team2_speed_y.append(
            [np.nan if p["position"]["y"] is None else p["position"]["y"] for p in team1_position]
        )
        self.team2_angle.append([np.nan if p["angle"] is None else p["angle"] for p in team2_position])
        self.team1_score.append([np.nan if s is None else s for s in team1_position])
        self.team2_score.append([np.nan if s is None else s for s in team2_position])
        self.shot.append(data["state"]["shot"])
        self.free_fuard_zone_foul.append(data["last_move"]["free_guard_zone_foul"])
        self.end.append(data["state"]["end"])


if __name__ == "__main__":
    server_log = ServerLog()
    log_path = pathlib.Path("data/logs/20230702T124801_3de3b46c-1325-4709-9378-6f0cc07f2128/game.dcl2")
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        exit(1)
    server_log.load(log_path)
