# ba_meta require api 9
import hello
import babase as ba
import bascenev1 as bs

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)
    print("egg!") #doesnt work

# ba_meta export plugin
class FangPlugin(ba.Plugin):
    def on_app_running(self) -> None:
        ba.screenmessage("ba.msg")
        print("ba.msg") #works
        bs.broadcastmessage("broadcast")
        print("bs.broad") #works