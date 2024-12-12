import bascenev1 as bs

print("hello is called")

def hello():
    print("inside hello")
    bs.broadcastmessage("konnichiwa chibi!", clients=None, transient=True, color = (0,0.5,1))
    return None