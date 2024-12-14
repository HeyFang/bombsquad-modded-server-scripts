# ba_meta require api 9
import hello
import babase as ba
import bascenev1 as bs

print("fetchChat is called")

def filter_chat_message(msg: str, client_id: int) -> str | None:
    print(msg, client_id)
    
    match msg:
        
        case "hello":
            hello.hello()

        case "/end":
            hello.end(client_id)

        case _:
            return msg

    return msg

