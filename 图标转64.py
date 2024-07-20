import base64

with open("1.png", "rb") as icon_file:
    encoded_string = base64.b64encode(icon_file.read()).decode("utf-8")

with open("icon_base64.txt", "w") as text_file:
    text_file.write(encoded_string)
