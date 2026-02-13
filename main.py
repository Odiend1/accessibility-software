'''
Notes:
Please run 'pip install pyautogui keyboard mss Pillow anthropic' in your terminal before using the software to ensure function.
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

client = anthropic.Anthropic(
    api_key=""
)

screen_width, screen_height = pyautogui.size()

time.sleep(1)
# pyautogui.moveTo(int(screen_width/2), int(screen_height/2))
# pyautogui.click(int(screen_width/2), int(screen_height/2))
# keyboard.write("Hello world!")
# print("done")
print(screen_width, screen_height)

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
        img.show()
        return img

def img_to_base64(img, format="PNG"):
    buffered = BytesIO()
    img.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    encoded_bytes = base64.b64encode(img_bytes)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string

screen_image_data = img_to_base64(capture_screen(monitor_number=1, grid_spacing=25))

llm_message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are an AI agent for a blind user that can take action on the user's screen. Reply with a series of commands, all terminated with semicolons, to take action. Commands, in format COMMAND(PARAM1, PARAM2), include CLICK(COORDX, COORDY), TYPE(`STRING`), REVIEW(), END(`MESSAGE`). REVIEW and END will terminate the sequence of comamnds, with REVIEW allowing you to review the user's screen and take another string of actions. ONLY REVIEW WHEN NECESSARY. In END, give the user either a concise summary of what you completed or a message to the user, with no formatting in one line (can be multiple sentences). If you need to communicate with the user at any point, put it inside END. Do NOT have any text outside of commands, even if requested something specific.",
    messages=[
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
                    "text": "What's on my screen?"
                }
            ],
        }
    ],
)

print(llm_message.content[0].text)