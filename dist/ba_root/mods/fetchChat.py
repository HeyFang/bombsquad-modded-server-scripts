import bascenev1 as bs
import hello

def filter_chat_message(msg: str, client_id: int):

    try:
        if msg == "hello":
            hello.hello()
            return None
    except:
        pass
    return msg