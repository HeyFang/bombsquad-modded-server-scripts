# ba_meta require api 9
import hello
import babase as ba
import bascenev1 as bs

print("fetchChat is called")

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)
    if msg == "hello":
        hello.hello()

    return msg

