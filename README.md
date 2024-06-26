# gptcli
This is a very basic console that wraps a small portion of OpenAI's API
You need your own OpenAI API key to use this program. You'll also need to set it as an
environment variable with the following command (for linux, goodluck if you're using windows):
```
 $ export OPENAI_API_KEY=<your api key>
```
[For more information take a look at the API documentation](https://platform.openai.com/docs/quickstart?context=python)

## TODO
- Implement [multimodal support](https://platform.openai.com/docs/guides/vision) for gpt-4o (allow user to attach/receive images)

## Usage
There are two primary input types, the default chat/prompt input and the menu. When you first
launch the program, the default system prompt will be printed. From there you can either send
a message to openai, or open the menu.

### Sending Messages
In order to conclude a message, you must enter the `END_OF_MESSAGE` character (by default `@`)
on a line by itself. For example:
```
User:
-----
    EOM        -  "@"
    Cancel     -  "#"
    View Menu  -  "%" or empty message
Could you please elaborate on the proverb "A foolish man will ignore the mundane actions of a
canine, however the wise man will ask 'what the dog doin?'"
@
```
From there `...` will be printed to indicate that the message is being sent, and then the 
response from openai will be printed. You will then be prompted to send a message or open the
menu once again.

### Option Menu
If you enter no message, or enter only a single *special* character ("`@`", "`#`", or "`%`")
then the menu will open. Where there are 6 options at the moment...

#### Saving Chats
Saving a chat involves dumping a json struct of all the messages sent between openai and the
user into a file in the current working directory `./[chat_name].chat]`.

#### Loading Chats
When loading a chat, the current working directory will be searched for files ending with the
`.chat` extension. Once the user selects a chat to load, it will be printed to the screen
followed by the main prompt.

