# ba_meta require api 9
import hello
import babase as ba
import bascenev1 as bs

# our imports:
import fetchChat

# ba_meta export plugin
class modsImpoterPlugin(ba.Plugin):
    def on_app_running(self) -> None:
        print("modsImporterPlugin is called")