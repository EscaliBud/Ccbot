try: 
    from telethon.sessions import StringSession
    from telethon.sync import TelegramClient
except:
    print("You didnt installed telethon. I am installing......")
    import os
    
    os.system("pip install telethon")
    from telethon.sessions import StringSession
    from telethon.sync import TelegramClient

try:
    API_ID = int(input("Tell Me Your Api Id: "))
except ValueError:
    print("Only Integer are allowed")

API_HASH = str(input("Tell Me Your Api Hash: "))


with TelegramClient(StringSession(), api_id= API_ID, api_hash = API_HASH) as client:
    session = client.session.save()
    text = f"""
This is you session hash copy and don't send it to anyone
`{session}`
Api Made By: [𓄂ᴋ͟ʀ͟ᴇͥ͟sͣ͟sͫ͟ᴡ͟ᴇ͟ʟ͟ʟ͟](https://t.me/EscaliBud)
Github: [Infinity Hackers](https://t.me/DartNetc)"""
    client.send_message("me",text)
    print(session)
    print("This is you session string Keep it safe . and one of this is sent to your account's save message")