from practice import SocketClient
import json
from practice import isready
from practice import update_recv

if __name__ == "__main__":
    cli = SocketClient()
    a = cli.receive()
    cli.logger.info(f"Receive message : {a}")
    cli.dc_ok()
    b = cli.receive()
    cli.logger.info(f"Receive message : {b}")
    cli.ready()
    c = cli.receive()
    cli.logger.info("aaaaa")
    json_data = json.loads(c)
    dict_data = json.loads(json_data)
    cli.logger.info(type(dict_data))
    cli.logger.info(f"Receive message : {c}")
    cli.logger.info(f"dict_data : {dict_data}")
    mydata = update_recv(**dict_data)
    cli.logger.info(f"is_ready : {mydata}")
    for i in range(10):
        cli.battle()
    # print(json.loads(ready))
    d = cli.receive()
    cli.logger.info(f"Receive message : {d}")