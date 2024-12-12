# ba_meta require api 9
import hello
import babase as ba
import bascenev1 as bs

# our imports:
import fetchChat

# ba_meta export plugin
class modsImpoterPlugin(ba.Plugin):
    def on_app_running(self) -> None:
        ba.screenmessage("ba.msg")
        print("ba.msg")
        bs.broadcastmessage("broadcast")
        print("bs.broad")