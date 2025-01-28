import requests, tkinter, customtkinter, os, pyperclip, re, httpx
from PIL import Image
from datetime import datetime

h = os.getcwd()
customtkinter.set_appearance_mode('Dark')
bggs = os.path.join(h, "Backend", "cookies.jpg")
CheckerGUI = customtkinter.CTk()

try:
    bg = customtkinter.CTkImage(Image.open(bggs), size=(800, 950))
except FileNotFoundError:
    print(f"Error: The image file '{bggs}' was not found. Please ensure the file exists in the 'Backend' folder.")
    exit()

CheckerGUI.geometry('800x950')
CheckerGUI.title('AK Cookie Checker')
IPlock = ""
ID = ""
new_auth_cookie = ""

bg_pic = customtkinter.CTkLabel(CheckerGUI, text="", image=bg)
bg_pic.place(x=0, y=0)

game_urls = [
    "https://www.roblox.com/games/142823291/Murder-Mystery-2",
    "https://www.roblox.com/games/13772394625/Blade-Ball",
    "https://www.roblox.com/games/2753915549/Blox-Fruits",
    "https://www.roblox.com/games/920587237/Adopt-Me",
    "https://www.roblox.com/games/8737899170/Pet-Simulator-99"
]

def extract_game_id(game_url):
    match = re.search(r'games/(\d+)/', game_url)
    if match:
        return match.group(1)
    return None

def fetch_game_passes(game_id):
    url = f"https://games.roblox.com/v1/games/{game_id}/game-passes"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["data"]
    return None

def check_game_passes():
    game_pass_display.delete(0.0, 'end')
    for game_url in game_urls:
        game_id = extract_game_id(game_url)
        if game_id:
            game_passes = fetch_game_passes(game_id)
            if game_passes:
                game_name = game_url.split("/")[-1].replace("-", " ")
                game_pass_display.insert("end", f"Game: {game_name}\n", "bold")
                for i, pass_data in enumerate(game_passes[:3]):
                    game_pass_display.insert("end", f"  {i+1}. {pass_data['name']}\n")
                    game_pass_display.insert("end", f"     Price: {pass_data.get('price', 'N/A')} Robux\n")
                    game_pass_display.insert("end", f"     Sales: {pass_data.get('sales', 'N/A')}\n")
                game_pass_display.insert("end", "-" * 40 + "\n")
            else:
                game_pass_display.insert("end", f"No game passes found for {game_url.split('/')[-1]}\n")
        else:
            game_pass_display.insert("end", f"Invalid URL: {game_url}\n")

def refreshing():
    global new_auth_cookie

    def generate_csrf_token(auth_cookie):
        try:
            csrf_req = httpx.get("https://www.roblox.com/home", cookies={".ROBLOSECURITY": auth_cookie})
            csrf_txt = csrf_req.text.split("<meta name=\"csrf-token\" data-token=\"")[1].split("\" />")[0]
            return csrf_txt
        except:
            status.configure(text="Invalid Cookie", text_color="#ff3333")
            return None

    def generate_headers(csrf_token, auth_cookie):
        headers = {
            "Content-Type": "application/json",
            "user-agent": "Roblox/WinInet",
            "origin": "https://www.roblox.com",
            "referer": "https://www.roblox.com/my/account",
            "x-csrf-token": csrf_token
        }
        cookies = {".ROBLOSECURITY": auth_cookie}
        return (headers, cookies)

    def refresh_cookie(auth_cookie):
        csrf_token = generate_csrf_token(auth_cookie)
        if not csrf_token:
            return None
        headers, cookies = generate_headers(csrf_token, auth_cookie)
        req = httpx.post("https://auth.roblox.com/v1/authentication-ticket", headers=headers, cookies=cookies, json={})
        auth_ticket = req.headers.get("rbx-authentication-ticket", "Failed to get authentication ticket")
        headers.update({"RBXAuthenticationNegotiation": "1"})
        req1 = httpx.post("https://auth.roblox.com/v1/authentication-ticket/redeem", headers=headers, json={"authenticationTicket": auth_ticket})
        new_auth_cookie = re.search(".ROBLOSECURITY=(.*?);", req1.headers["set-cookie"]).group(1)
        return new_auth_cookie

    auth_cookie = orgcookie.get()
    if not auth_cookie:
        status.configure(text="No cookie entered", text_color="#ff3333")
        return

    new_auth_cookie = refresh_cookie(auth_cookie)
    if not new_auth_cookie:
        status.configure(text="Failed to refresh cookie", text_color="#ff3333")
        return

    try:
        r = requests.get("https://accountsettings.roblox.com/v1/email", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        if "verified" in r:
            status.configure(text="Valid Cookie", text_color="#00ff00")
            emailvalue.configure(text_color="#00ff00", text="Verified")
        else:
            emailvalue.configure(text_color="#ff3333", text="Unverified")
        rx = requests.get("https://users.roblox.com/v1/users/authenticated", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        global ID
        ID = rx["id"]
        rxs = requests.get(f"https://users.roblox.com/v1/users/{ID}", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        usernaMe = rxs["name"]
        creation = rxs["created"]
        creation = creation.split('T')[0]
        Creationvalue.configure(text=creation, text_color="#00ff00")
        usernamevalue.configure(text=usernaMe, text_color="#00ff00")
        rxsr = requests.get("https://economy.roblox.com/v1/user/currency", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        rbx = rxsr["robux"]
        rbx = "{:,}".format(rbx)
        robuxvalue.configure(text=rbx + " R$", text_color="#ffd700")
        rxsrx = requests.get(f"https://premiumfeatures.roblox.com/v1/users/{ID}/validate-membership", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        if bool(rxsrx):
            premiumvalue.configure(text="True", text_color="#00ff00")
        else:
            premiumvalue.configure(text="False", text_color="#ff3333")
        rxsrxs = requests.get(f"https://catalog.roblox.com/v1/users/{ID}/bundles/1?limit=100&nextPageCursor=&sortOrder=Desc", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        headless = [201]
        korblox = [192]
        for item in rxsrxs["data"]:
            y = item["id"]
            if any(check_id == y for check_id in headless):
                headlessvalue.configure(text="True", text_color="#00ff00")
            else:
                headlessvalue.configure(text="False", text_color="#ff3333")
            if any(check_id == y for check_id in korblox):
                korbloxvalue.configure(text="True", text_color="#00ff00")
            else:
                korbloxvalue.configure(text="False", text_color="#ff3333")
        rxsrxsr = requests.get(f"https://inventory.roblox.com/v1/users/{ID}/assets/collectibles?assetType=All&sortOrder=Asc&limit=100", cookies={'.ROBLOSECURITY': new_auth_cookie}).json()
        limiteds.delete(0.0, 'end')
        if rxsrxsr['data'] == []:
            limiteds.insert("end", "No limiteds found", "center")
        else:
            lmteds = rxsrxsr['data']
            total_value = 0
            for stuff in lmteds:
                name = stuff["name"]
                value = stuff["recentAveragePrice"]
                total_value += value
                value = "{:,}".format(value)
                limiteds.insert("end", f"{name}: {value} R$\n", "left")
            limiteds.insert("end", f"\nTotal Value: {'{:,}'.format(total_value)} R$", "left")
    except:
        status.configure(text="Invalid Cookie", text_color="#ff3333")

    check_game_passes()

def copycookie():
    try:
        pyperclip.copy(new_auth_cookie)
        status.configure(text="Cookie Copied!", text_color="#00ff00")
    except:
        status.configure(text="No cookie to copy", text_color="#ff3333")

def copyurl():
    try:
        pyperclip.copy(f"https://www.roblox.com/users/{ID}/profile")
        status.configure(text="URL Copied!", text_color="#00ff00")
    except:
        status.configure(text="No URL to copy", text_color="#ff3333")

title_frame = customtkinter.CTkFrame(CheckerGUI, fg_color="transparent")
title_frame.pack(pady=10)

title = customtkinter.CTkLabel(
    title_frame,
    text="AK Cookie Checker",
    font=("Arial", 30, "bold"),
    text_color="#ffffff"
)
title.pack()

input_frame = customtkinter.CTkFrame(CheckerGUI, fg_color="transparent")
input_frame.pack(pady=10)

orgcookie = tkinter.StringVar()
cookie_entry = customtkinter.CTkEntry(
    input_frame,
    width=600,
    height=40,
    textvariable=orgcookie,
    font=("Roboto", 16),
    placeholder_text="Enter your cookie here...",
    border_color="#570606",
    fg_color="#1a1a1a"
)
cookie_entry.pack(pady=10)

refresh_button = customtkinter.CTkButton(
    input_frame,
    text="Refresh",
    font=("Roboto", 18),
    width=150,
    height=35,
    fg_color="#570606",
    hover_color="#3d0505",
    command=refreshing
)
refresh_button.pack(pady=10)

status = customtkinter.CTkLabel(
    input_frame,
    text="Status: Ready",
    font=("Roboto", 14),
    text_color="#ffffff"
)
status.pack()

main_container = customtkinter.CTkFrame(CheckerGUI, fg_color="transparent")
main_container.pack(expand=True, fill="both", padx=10)

account_frame = customtkinter.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=10)
account_frame.pack(side="left", expand=True, fill="both", padx=5)

account = customtkinter.CTkLabel(
    account_frame,
    text="Account Information",
    font=("Arial", 20, "bold"),
    text_color="#ffffff"
)
account.pack(pady=10)

username = customtkinter.CTkLabel(account_frame, text="Username:", font=("Roboto", 14), text_color="#ffffff")
username.pack(pady=5)
usernamevalue = customtkinter.CTkLabel(account_frame, text="", font=("Roboto", 14))
usernamevalue.pack()

email = customtkinter.CTkLabel(account_frame, text="Email:", font=("Roboto", 14), text_color="#ffffff")
email.pack(pady=5)
emailvalue = customtkinter.CTkLabel(account_frame, text="", font=("Roboto", 14))
emailvalue.pack()

Creation = customtkinter.CTkLabel(account_frame, text="Creation Date:", font=("Roboto", 14), text_color="#ffffff")
Creation.pack(pady=5)
Creationvalue = customtkinter.CTkLabel(account_frame, text="", font=("Roboto", 14))
Creationvalue.pack()

value_frame = customtkinter.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=10)
value_frame.pack(side="left", expand=True, fill="both", padx=5)

Values = customtkinter.CTkLabel(
    value_frame,
    text="Account Value",
    font=("Arial", 20, "bold"),
    text_color="#ffffff"
)
Values.pack(pady=10)

robux = customtkinter.CTkLabel(value_frame, text="Robux:", font=("Roboto", 14), text_color="#ffffff")
robux.pack(pady=5)
robuxvalue = customtkinter.CTkLabel(value_frame, text="", font=("Roboto", 14))
robuxvalue.pack()

premium = customtkinter.CTkLabel(value_frame, text="Premium:", font=("Roboto", 14), text_color="#ffffff")
premium.pack(pady=5)
premiumvalue = customtkinter.CTkLabel(value_frame, text="", font=("Roboto", 14))
premiumvalue.pack()

korblox = customtkinter.CTkLabel(value_frame, text="Korblox:", font=("Roboto", 14), text_color="#ffffff")
korblox.pack(pady=5)
korbloxvalue = customtkinter.CTkLabel(value_frame, text="", font=("Roboto", 14))
korbloxvalue.pack()

headless = customtkinter.CTkLabel(value_frame, text="Headless:", font=("Roboto", 14), text_color="#ffffff")
headless.pack(pady=5)
headlessvalue = customtkinter.CTkLabel(value_frame, text="", font=("Roboto", 14))
headlessvalue.pack()

collectibles_frame = customtkinter.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=10)
collectibles_frame.pack(side="left", expand=True, fill="both", padx=5)

Collectibles = customtkinter.CTkLabel(
    collectibles_frame,
    text="Collectibles",
    font=("Arial", 20, "bold"),
    text_color="#ffffff"
)
Collectibles.pack(pady=10)

limiteds = customtkinter.CTkTextbox(
    collectibles_frame,
    width=250,
    height=200,
    font=("Roboto", 12),
    fg_color="#262626",
    text_color="white",
    corner_radius=5
)
limiteds.pack(pady=10, padx=10, expand=True, fill="both")

game_pass_frame = customtkinter.CTkFrame(CheckerGUI, fg_color="#1a1a1a", corner_radius=10)
game_pass_frame.pack(pady=10, padx=10, fill="both", expand=True)

game_pass_label = customtkinter.CTkLabel(
    game_pass_frame,
    text="Game Pass Checker",
    font=("Arial", 20, "bold"),
    text_color="#ffffff"
)
game_pass_label.pack(pady=10)

game_pass_display = customtkinter.CTkTextbox(
    game_pass_frame,
    width=600,
    height=150,
    font=("Roboto", 12),
    fg_color="#262626",
    text_color="white",
    corner_radius=5
)
game_pass_display.pack(pady=10, padx=10, expand=True, fill="both")

button_frame = customtkinter.CTkFrame(CheckerGUI, fg_color="transparent")
button_frame.pack(pady=10)

copy_url_btn = customtkinter.CTkButton(
    button_frame,
    text="Copy Profile URL",
    font=("Roboto", 16),
    width=150,
    height=35,
    fg_color="#570606",
    hover_color="#3d0505",
    command=copyurl
)
copy_url_btn.pack(side="left", padx=10)

copy_cookie_btn = customtkinter.CTkButton(
    button_frame,
    text="Copy Cookie",
    font=("Roboto", 16),
    width=150,
    height=35,
    fg_color="#570606",
    hover_color="#3d0505",
    command=copycookie
)
copy_cookie_btn.pack(side="left", padx=10)

CheckerGUI.mainloop()