import json
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogData:
    version: list
    tag: str
    data_id: int
    date_time: datetime
    thread_id: int
    log_data: str


class log_output():
# ログの出力名を設定（1）

    def log(self) -> None:
        # url = 'localhost:10000'
        # res = requests.get(url)
        logger = logging.getLogger('Log')           #logger名loggerを取得
        sh = logging.StreamHandler()                #コンソール出力を行うハンドラを作成
        logger.addHandler(sh)                       #loggerにハンドラを登録
        logging.basicConfig(level = logging.info)   #ログレベルの設定

output = log_output()                                #インスタンスの作成
output.log                                          #ログの出力
 
# ログをコンソール出力するための設定（2）





