import bascenev1 as bs
import hello

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print("fetchChat was imported!")
    print(msg, client_id)
    try:
        if msg == "hello":
            hello.hello()
            return None
    except:
        pass
    return msg