# ba_meta require api 9
import hello
import babase as ba
import bascenev1 as bs

print("hey eggu!")

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print("egg!") #doesnt work
    print(msg, client_id)

    return msg

