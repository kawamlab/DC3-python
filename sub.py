from practice1 import SocketClient1
import time

if __name__ == "__main__":
    cli = SocketClient1()
    a = cli.receive()
    cli.logger.info(f"Receive message : {a}")
    cli.dc_ok()
    b = cli.receive()
    cli.logger.info(f"Receive message : {b}")
    cli.ready()
    c = cli.receive()
    cli.logger.info(f"Receive message : {c}")
    for i in range(10):
        cli.battle()
    # print(json.loads(ready))
    d = cli.receive()
    cli.logger.info(f"Receive message : {d}")