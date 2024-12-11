import bascenev1 as bs

def hello(msg):
    if msg == "hello":
        bs.broadcastmessage(
            "Hello World",
            color = (0, 1, 0.5)
            )