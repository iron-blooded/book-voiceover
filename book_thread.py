import requests
import multiprocessing
import time
import configparser
import base64
import json
configF = configparser.ConfigParser()
try:
    configF.read("config.ini")
    nameBook=str(configF['book']['nameBook'])
except:
    print('Создан config.ini')
    f = open('config.ini','w')
    f.write('''[book]
token='aaaaaaaaaaaa'
; Ваш токен, который вы можете получить отправив в google tts любой запрос.
speed=0.8
; Скорость, с которой будет читать tts.
directory=Солярис
; Название каталога, в который будут итоговые записи.
filename=synthesize-text-audio-
; Название итогового аудиофайла. Учтите, что в конце будет стоять порядковый номер.
threads=2
; Количество потоков. Если вы поставите слишком много, скрипт изменит на максимально комфортное вашему процессору. Да и учитывайте, что google может не одобрить большое количество запросов.
nameBook=text.txt
; Название книги, из которая будет озвучиваться. Только *.txt.
start=0
; Указывает, с какого порядкового номера скрипту начинать озвучивать. Полезно, например, в случае если вы на середине книги осознали, что ударение на каком то слове неправильное.
audioEncoding=LINEAR16
; Указывает, в какой кодировке сервис будет возвращать озвучку. Идеальный для меня - LINEAR16. В нем отстутствуют какие либо артефакты звучания. Но если для вас размер итогового файла критичен, можете поставить mp3.
name=ru-RU-Wavenet-D
; Указывает, кто должен озвучивать книгу. На сайте https://cloud.google.com/text-to-speech/ можете посмотреть, кто вам больше всего заходит.
glossary=TTS.lexx
; Указывает название словаря, из которого будут парситься исправления ударений.
split="\\n"
; Указывает, по каким знакам разбивать текст''')
    f.close()
    configF.read("config.ini")
    nameBook=str(configF['book']['nameBook'])
f = open(nameBook)
text = f.read()
f.close()
data = ('{"input":{"text":"'+text+'"},"voice":{"languageCode":"ru-RU","name":"ru-RU-Wavenet-D"},"audioConfig":{"audioEncoding":"LINEAR16","pitch":0,"speakingRate":0.8}}').encode('utf-8')
try:
    f = open(str(configF['book']['glossary']))
    config = f.read()
    f.close()
except:
    print('Отсутствует словарь!')
    config=''
config=config.replace('"','')
config=config.split('=')
zabiv=1
text=text.replace('"',";").replace('.'," .").replace(' . . .',' ...')
print("начинается замена")
while zabiv+1 < len(config):
    text=text.replace(str(config[zabiv].split('\n')[1]), str(config[zabiv+1].split('\n')[0]))
    zabiv=zabiv+1
print("заменено успешно")
splitt=configF['book']['split'].replace('"','')
if splitt != splitt.replace('\\n',''):
    splitt=splitt.replace('\\n','\n')
text = text.split(splitt)
i=0
text2=text[i]
def compil(i,textjs):
    global configF
    direct = str(configF['book']['directory'])
    filename = str(configF['book']['filename'])
    audio_content=textjs
    try:
        f = open(direct+'/'+filename+str(i)+'.mp3','wb')
    except:
        import os
        os.mkdir(direct)
        f = open(direct+'/'+filename+str(i)+'.mp3','wb')
    f.write(base64.b64decode(audio_content))
    f.close()

def razbivN(text):
    i=0
    ii=0
    ioi=[0]
    text2=''
    while (len(text)-1) > i:
        try:
            text2=''
            while len(text2+splitt+str(text[i]))<4899:
                if text2 != str(text[i]):
                    text2=text2+splitt+str(text[i])
                i=i+1
            ioi.append(i)
        except:
            i=i
        ii+=1
    return(ii,ioi)
def razbiv(lii,text):
    i=lii
    text2=''
    try:
        while len(text2+splitt+str(text[i]))<4899:
            if text2 != str(text[i]):
                text2=text2+splitt+str(text[i])
            i=i+1
    except:
        print('усе')
    text2=text2.replace(splitt,'',1)
    return(text2)

def sendText(text2,data,i):
    global configF
    token=str(configF['book']['token']).replace("'",'')
    speed=str(configF['book']['speed'])
    headers = {
    'authority': 'cxl-services.appspot.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="92"',
    'dnt': '1',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0',
    'content-type': 'text/plain;charset=UTF-8',
    'accept': '*/*',
    'origin': 'https://www.gstatic.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.gstatic.com/',
    'accept-language': 'ru-RU,ru;q=0.9',
    }
    params = (
    ('url', 'https://texttospeech.googleapis.com/v1beta1/text:synthesize'),
    ('token', token),
    )
    error=1
    while error!=0:
        data = ('{"input":{"text":"'+str(text2)+'"},"voice":{"languageCode":"ru-RU","name":"'+str(configF['book']['name'])+'"},"audioConfig":{"audioEncoding":"'+str(configF['book']['audioEncoding'])+'","pitch":0,"speakingRate":'+speed+'}}').encode('utf-8')
        response = requests.post('https://cxl-services.appspot.com/proxy', headers=headers, params=params, data=data)
        response=response.text.encode().decode()
        error=0
        if response != '' and response !=' Service Unavailable' and response != 'Service Unavailable' and response != 'Unauthorized':
            try:
                response=json.loads(response)["audioContent"]
            except:
                print('Ошибка!')
                print(response)
            error=0
        else:
            print('Произошло что то не то. Скорее всего у вас устарел токен.')
            print(response)
            time.sleep(60)
            error+=1
        if len(response)<200:
            print(response)
            print(len(str(text2)))
            error+=1
        else:
            print('успешно '+str(i))
            compil(i,response)
            return(i,text2)
def osnov(text,trii,lli):
    text2=razbiv(lli[trii],text)
    sendTex = sendText(text2,data,trii)
    i=sendTex[0]
    text2=sendTex[1]
    return(i)
if __name__ == '__main__':
    ii=razbivN(text)
    lli=ii[1]
    ii=int(ii[0])
    trii=int(configF['book']['start'])
    boolThreads=int(configF['book']['threads'])
    try:
        if boolThreads > int(multiprocessing.cpu_count()):
            #boolThreads = int(multiprocessing.cpu_count())
            print('вы выставили слишком большое кол-во потоков. Уменьшите до '+str(multiprocessing.cpu_count()))
        while trii < ii:
            if len(multiprocessing.active_children()) < boolThreads:
                print(str(trii)+'('+str((trii*100)//ii)+'%)')
                my_thread = multiprocessing.Process(target=osnov, args=(text,trii,lli,))
                my_thread.start()
                trii+=1
                time.sleep(1)
    except:
        print("что то в потоках выбило ошибку, используется вариант без мультипроцессинга")
        while trii < ii:
            print(str(trii)+'('+str((trii*100)//ii)+'%)')
            osnov(text,trii,lli)
            trii+=1
            time.sleep(1)
print('Конец')
