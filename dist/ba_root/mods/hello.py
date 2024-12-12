import bascenev1 as bs

def hello():
    print("hello.py is running")
    bs.broadcastmessage(
        "Hello World",
        color = (0, 1, 0.5)
        )