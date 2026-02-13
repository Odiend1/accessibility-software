'''
Notes:
Please run 'pip install pyautogui keyboard mss Pillow pyttsx3 anthropic' in your terminal before using the software to ensure function.
If needed, please give the program permission to screen record. It is necessary for software function.
'''

import pyautogui # Mouse control library
import keyboard # Keyboard control library
import mss # Screenshot library
import mss.tools
from PIL import Image, ImageDraw, ImageFont
import time
import base64
from io import BytesIO
import anthropic
import tkinter as tk
import platform
import pyttsx3

client = anthropic.Anthropic(
    api_key=""
)

screen_width, screen_height = pyautogui.size()

root = tk.Tk()
root.title("Accessibility Assistant")
root.attributes('-alpha', 0.9)

heading_label = tk.Label(root, text="What would you like to do today?")
heading_label.pack(pady=5)

prompt_entry = tk.Entry(root, width=75)
prompt_entry.pack(padx=5, pady=2)
prompt_entry.focus_set()

def query_agent():
    user_prompt = prompt_entry.get()
    if platform.system() == "Darwin":
        keyboard.press_and_release('cmd+tab')
    else:
        keyboard.press_and_release('alt+tab')
    root.withdraw()

    time.sleep(0.25)

    def capture_screen(monitor_number=1, grid_spacing=50):
        with mss.mss() as sct: # Screen capture tool
            monitor = sct.monitors[monitor_number]
            sct_img = sct.grab(monitor)

            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()

            width, height = img.size

            for x in range(0, width, grid_spacing):
                draw.line([(x, 0), (x, height)], fill="gray", width=1)
                draw.text((x + 2, 5), str(x), fill="gray", font=font)

            for y in range(0, height, grid_spacing):
                draw.line([(0, y), (width, y)], fill="gray", width=1)
                draw.text((5, y + 2), str(y), fill="gray", font=font)

            img.save("screenshot_with_grid.png")
            # img.show()
            return img

    def img_to_base64(img, format="PNG"):
        buffered = BytesIO()
        img.save(buffered, format=format)
        img_bytes = buffered.getvalue()
        encoded_bytes = base64.b64encode(img_bytes)
        encoded_string = encoded_bytes.decode('utf-8')
        return encoded_string

    command_cycles = 0
    past_messages = []

    while command_cycles < 50:
        print("Starting command cycle", command_cycles+1)
        screen_image_data = img_to_base64(capture_screen(monitor_number=1, grid_spacing=25))

        llm_message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="You are an AI agent for a blind user that can take action on the user's screen. YOU MUST REPLY ONLY WITH A SERIES OF COMMANDS, all in one line and each started with TWO exclamation points (!!) and terminated with TWO semicolons each (;;), to take action. You are provided an image of the user's screen with a precise grid with 25px subdivisions. Screen dimensions are " + str(screen_width) + "x" + str(screen_height) + ". Commands, in format !!COMMAND(PARAM1, PARAM2);;, include !!CLICK(COORDX, COORDY);;, !!WRITE(`STRING`);;, !!PRESS(`KEY`);;, !!SCROLLUP();;, !!SCROLLDOWN();;, !!PAUSE(SECONDS);;, !!MESSAGE(`TEXT`);;, !!REVIEW();;, !!END();;. CLICK and WRITE allow you to control the user's screen. PRESS lets you press and release a key or shortcut, with keys separated with a + (use shortcuts over clicks when possible). PAUSE lets you delay actions (short delays between actions recommended). MESSAGE lets you tell the user something or give them feedback during your process. REVIEW is to be used for complex tasks where changes on the screen as expected, as it reprompts you with the user's updated screen after prior actions before terminating the current string of commands. END marks the end of your task and terminates the string of commands, and is recommended for one-step tasks. Anything you send outside of commands will NOT be read to the user. Make sure to have any text you would like the user to see in the MESSAGE command. ONCE AGAIN, text outside of commands will result in the your FAILURE as an agent. Notes: ALWAYS !!PRESS(`win+s`);; or !!PRESS(`cmd+space`);; to search for and open applications on different OSs, instead than clicking on tiny icons (which you WILL miss). If navigating to a website or new page, be sure to REVIEW and PAUSE signfiicantly before continuing to allow for loading times. And, if searching for something, use browser and built-in shortcuts rather than clicking on any searchbar. If you cannot see your target clearly or it is near the very top/bottom of the screen, SCROLLUP AND SCROLL DOWN are small bursts of scrolling, equivalent to `page up` and `page down`. If you are trying to click a button and it didn't work the first time, use !!PRESS(`tab`);; to cycle through elements on screen and press enter. Even if the user has not reprompted you, and the last message was from the assistant, keep providing commands. You will not be prompted if there was nothing to do, and END terminates your cycles. Make sure to click the middle of buttons, not the top left corner. If the screen isn't changing when you click a button, try offsetting your click by a good bit (often to the down and right), as you may be missing slightly.",
            messages= past_messages + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screen_image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ],
                }
            ],
        )

        # if not llm_message or not llm_message.content or len(llm_message.content) == 0: continue
        print(llm_message.content[0].text)
        past_messages.append({"role": "assistant", "content": [{"type": "text", "text": llm_message.content[0].text}]})
        past_messages.append({"role": "user", "content": [{"type": "text", "text": "Continue the task provided given your previous progress."}]})
        commands = llm_message.content[0].text.split(";;")[:-1]
        commands = [command.strip() for command in commands]
        commands[0] = commands[0][commands[0].index("!!"):]

        review = False
        for command in commands:
            time.sleep(0.1)
            if command.startswith("!!CLICK"):
                coords = command[(command.index('(') + 1):command.index(')')].split(',')
                coords = [int(coord) for coord in coords]
                pyautogui.click(coords[0]+50, coords[1]+50)
            elif command.startswith("!!WRITE"):
                text = command[(command.index('(`') + 2):command.index('`)')]
                keyboard.write(text)
            elif command.startswith("!!PRESS"):
                keys = command[(command.index('(`') + 2):command.index('`)')]
                keyboard.press_and_release(keys)
            elif command.startswith("!!SCROLLUP"):
                keyboard.press_and_release('page up')
            elif command.startswith("!!SCROLLDOWN"):
                keyboard.press_and_release('page down')
            elif command.startswith("!!PAUSE"):
                delay = float(command[(command.index('(') + 1):command.index(')')])
                time.sleep(delay)
            elif command.startswith("!!MESSAGE"):
                text = command[(command.index('(`') + 2):command.index('`)')]
                print("Message received:", text)
                pyttsx3.speak(text)
            elif command.startswith("!!REVIEW"):
                review = True
                time.sleep(3)
                break
            elif command.startswith("!!END"):
                break
        
        command_cycles += 1
        if not review:
            break

    root.deiconify()

enter_button = tk.Button(root, text="Enter", command=query_agent)
enter_button.pack(pady=3)

root.mainloop()