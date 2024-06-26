from prompt_toolkit import PromptSession
# from prompt_toolkit.history import FileHistory
# from os.path import expanduser
# MUST HAVE OPENAI_API_KEY envinroment variable set, check README
from openai import OpenAI
import os
import json
import datetime

# user_prompt_session = PromptSession(history = FileHistory(expanduser('/.gpt_history')))
user_prompt_session = PromptSession()

client = OpenAI()

LOGGING = True
LOG_PATH = './.gptcli.log'
END_OF_MESSAGE = '@'
CANCEL_MESSAGE = '#'
VIEW_MENU = '%'
CHAT_FILE_EXTENSION = '.chat'
MODELS = [
    'gpt-4',
    'gpt-4o',
    'gpt-4-turbo',
    'gpt-3.5-turbo',
]

model = MODELS[1]
messages = [ 
    {
        'role': 'system',
        'content': 'You are a helpful and knowledgable assistant named ChatGPT.',
    },
]

# Title-inate
# -----------
# (adds a line of hyphens under text)
def t_inate(s):
    return s + "\n" + ('-' * len(s))

def get_int(prompt, l, h):
    while True:
        print(prompt, end='')
        try:
            n = int(input())
            if n < l or n > h:
                raise ValueError
            return n
        except ValueError:
            print(f"Invalid selection, expected integer between {l} and {h}. Try Again.")

def print_messages():
    global messages
    for m in messages:
        print(f"{t_inate(m['role'].capitalize() + ':')}\n{m['content']}\n")

def append_and_log_message(message):
    global LOG_PATH
    global messages
    messages.append(message)
    if not LOGGING:
        return
    log_entry = {
        'timestamp': str(datetime.datetime.now()),
        'message': message,
    }
    with open(LOG_PATH, 'a+', encoding='utf-8') as f:
        json.dump(log_entry, f, indent=4)


def get_user_message(user_name='user'):
    global END_OF_MESSAGE
    global CANCEL_MESSAGE
    global VIEW_MENU
    user_resp = ""
    print(
        t_inate(user_name.capitalize() + ':') + '\n'
        f"    EOM        -  \"{END_OF_MESSAGE}\"\n"
        f"    Cancel     -  \"{CANCEL_MESSAGE}\"\n"
        f"    View Menu  -  \"{VIEW_MENU}\" or empty message"
    )
    line = user_prompt_session.prompt()
    if not line or line[-1] == VIEW_MENU:
        return user_resp
    while not (line and line[-1] == END_OF_MESSAGE):
        if line and line[-1] == CANCEL_MESSAGE:
            return CANCEL_MESSAGE
        user_resp += line + "\n"
        line = user_prompt_session.prompt()
    return user_resp

def menu_save_chat():
    global messages
    global CHAT_FILE_EXTENSION
    # Get chat_name
    while True:
        chat_name = input("Enter chat name (no symbols other than \"_\"): ")
        if chat_name.isidentifier():
            break
        print("Invalid name, try again.")

    chat_name += CHAT_FILE_EXTENSION

    # Check if chat already exists (and is being overwritten)
    if os.path.isfile(chat_name):
        print("Warning: This chat already exists, would you like to override it? (y/n)")
        resp = input()
        if not resp:
            # No response, exit without doing anything
            return 1
        if resp[0] != 'y':
            # Response not 'y', exit without doing anything
            return 1

    # Write message to chat
    with open(chat_name, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=4)

    return 0

def menu_load_chat():
    global messages
    global CHAT_FILE_EXTENSION
    chat_table = []
    i = 0
    for f_name in os.listdir():
        if f_name.endswith(CHAT_FILE_EXTENSION):
            chat_table.append(f_name)
    if not chat_table:
        print("There are no saved chats to load.")
        return 0

    print(t_inate("Saved chats:"))
    for i, f_name in enumerate(chat_table):
        print(f" {i+1}. {f_name[:-len(CHAT_FILE_EXTENSION)]}")
    resp = get_int(f"Select a chat (1 - {len(chat_table)}) (0 to cancel): ", 0, len(chat_table))
    if not resp:
        return 1

    with open(chat_table[resp - 1], 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print_messages()
    return 0

def menu_change_model():
    global model
    global MODELS
    print(t_inate("Available models:"))
    # Used to indicate current model
    active_str = ""
    for i, m in enumerate(MODELS):
        if model == m:
            active_str = " *  "
        else:
            active_str = "    "
        print(f"{active_str}{i+1}. {m}")
    resp = get_int(f"Select model (1 - {len(MODELS)}): ", 1, len(MODELS))
    model = MODELS[resp - 1]
    print(f"Changed model to: {model}")
    return 0


def menu_change_system_prompt():
    global messages
    print(t_inate("Current Status Prompt:"))
    # TODO: Handle failed assertion
    assert messages[0]['role'] == 'system'
    print(messages[0]['content'])
    print("\nEnter the new system prompt (empty to cancel):")
    resp = input()
    if not resp:
        return 1
    messages[0]['content'] = resp
    print("Updated system prompt")
    return 0


def menu_cancel():
    return 0

def menu_exit():
    return -1

# Table of function pointers (to the above functions)
menu = [
    ("Save chat", menu_save_chat),
    ("Load chat", menu_load_chat),
    ("Change model", menu_change_model),
    ("Change system prompt", menu_change_system_prompt),
    ("Cancel", menu_cancel),
    ("Exit", menu_exit),
]



def handle_menu():
    global menu
    # Print table options
    print(t_inate("Options:"))
    for i, m in enumerate(menu):
        print(f"    {i+1}. {m[0]}")

    choice = get_int(f"Select menu option (1 - {len(menu)}): ", 1, len(menu))
    # Calling menu function pointers
    status = menu[choice-1][1]()
    if status > 0:
        print("!\n")
    return status


if __name__ == "__main__":
    # Print system prompt
    print(f"{t_inate('System prompt:')}\n{messages[0]['content']}\n")

    while True:
        # Main prompt
        user_msg = get_user_message()
        if user_msg == CANCEL_MESSAGE:
            continue
        if not user_msg:
            # not user_msg means empty
            if handle_menu() == -1:
                # Exit condition (see menu_exit())
                break
            continue
    
        # Add users message to chat history
        append_and_log_message({'role': 'user', 'content': user_msg})
    
        # Indicate about to hit API
        print("...\n")
        completion = client.chat.completions.create(model=model, messages=messages)
        # Only 1 choice, only care about message for now
        gpt_resp = completion.choices[0].message
    
        # Add gpts response to chat history
        append_and_log_message({'role': gpt_resp.role, 'content': gpt_resp.content})

        # Print gpts response
        print(f"\n{t_inate(gpt_resp.role.capitalize() + ':')}\n{gpt_resp.content}\n")
