print ("")
print (" @ManuelCode sta elaborando le informazioni...")
print ("")
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
import csv
import traceback
import time
import random

api_id = 0000000   #Inserisci il tuo ID API Telegram a 7 cifre.
api_hash = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'   #Inserisci il tuo API Hash a 32 caratteri.
phone = '+63xxxxxxxxxxxxx'   #Inserisci il tuo numero di cellulare con il prefisso internazionale.
client = TelegramClient(phone, api_id, api_hash)
client.connect()
    
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Inserisci il codice che dovrebbe esserti arrivato su telegram: '))
    
chats = []
last_date = None
chunk_size = 200
groups=[]
 
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)
 
for chat in chats:
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue
 
print('Scegli un gruppo da cui prendere i membri:')
i=0
for g in groups:
    print(str(i) + '- ' + g.title)
    i+=1
 
g_index = input("Scegli un numero: ")
target_group=groups[int(g_index)]
 
print('Fetching Members...')
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)
 
print('Salvataggio del file...')
with open("members.csv","w",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter=",",lineterminator="\n")
    writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
    for user in all_participants:
        if user.username:
            username= user.username
        else:
            username= ""
        if user.first_name:
            first_name= user.first_name
        else:
            first_name= ""
        if user.last_name:
            last_name= user.last_name
        else:
            last_name= ""
        name= (first_name + ' ' + last_name).strip()
        writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])      
print('File salvato')

input_file = 'members.csv'
users = []
with open(input_file, encoding='UTF-8') as f:
    rows = csv.reader(f,delimiter=",",lineterminator="\n")
    next(rows, None)
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = int(row[1])
        user['access_hash'] = int(row[2])
        user['name'] = row[3]
        users.append(user)

chats = []
last_date = None
chunk_size = 200
groups=[]

result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue

print('Scegli un gruppo in cui aggiungere gli utenti:')
i=0
for group in groups:
    print(str(i) + '- ' + group.title)
    i+=1

g_index = input("Scegli un numero: ")
target_group=groups[int(g_index)]

target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)

mode = int(input("Inserisci 1 se vuoi aggiungere gli utenti in base all Username. Inserisci 2 se vuoi aggiungerli in base all ID (Consigliato) : "))

delay = 0
delay = input('''Scegli un tempo di attesa tra l'aggiunta di un membro e l'altro (Consigliato: 40): ''')

for user in users:
    try:
        print ("Aggiungendo {}".format(user['id']))
        if mode == 1:
            if user['username'] == "":
                continue
            user_to_add = client.get_input_entity(user['username'])
        elif mode == 2:
            user_to_add = InputPeerUser(user['id'], user['access_hash'])
        else:
            sys.exit("Modalità non valida. Riprova.")
        client(InviteToChannelRequest(target_group_entity,[user_to_add]))
        print("Attendendo " + str(delay) + " secondi per non essere bannato da telegram")
        time.sleep(int(delay))
    except PeerFloodError:
        print("Telegram ha restituito un flood error. Riprova tra un po.")
    except UserPrivacyRestrictedError:
        print("Le impostazioni della privacy dell utente bloccano la aggiunta ai gruppi. Salto questo utente.")
    except:
        traceback.print_exc()
        print("Unexpected Error")
        continue
