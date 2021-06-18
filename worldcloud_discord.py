import ijson,re,os,json,datetime,matplotlib.pyplot as plt, pandas as pd
from collections import OrderedDict

path='G:\\Disborg\\exported'
os.chdir(path)
channels=()
userids={}
delete_char=('"',"`","\n","\r","\\")
def delete_lastline(file):
    count = 0
    with open(file,'r+b', buffering=0) as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            char = f.read(1)
            if char != b'\n' and f.tell() == end:
                print("No change: file does not end with a newline")
                exit(1)
            if char == b'\n':
                count += 1
            if count == 2:
                f.truncate()
                return
            f.seek(-1, os.SEEK_CUR)

def get_key(val):
  for key, value in userids.items():
    if val in value:
      return key
def user_messages():
    days = pd.date_range(start='', end='')
    active_days=[]
    if not os.path.exists("./user_json"):
        os.mkdir("user_json")
    for user in userids:
        if os.path.exists("./user_json/"+user+".json"):
            os.remove("./user_json/"+user+".json")
    for channel in channels:
      with open(channel+".json", 'rb') as file:
        parser = ijson.parse(file)
        for prefix, event, value in parser:
            if prefix == "messages.item.timestamp":
                message_time=value.split("T")[0]
                print(message_time)
            if prefix == "messages.item.content":
                for char in delete_char:
                    value = value.replace(char, "")
                message_content=value
            if prefix == "messages.item.author.id" and value in userids.values():
                with open("./user_json/"+get_key(value)+".json", 'a', encoding="utf-8") as json_file:
                    if os.stat("./user_json/"+get_key(value)+".json").st_size == 0:
                        json_file.write('{\n  "messages": [\n')
                    txxt = '    {\n      "message_time": "' + str(message_time) + '",\n      "channel": "' + channel + '",\n      "message_content": "' + message_content + '"\n	},\n'
                    json_file.write(txxt)
            if channel== channels[-1] and prefix == "messageCount":
                for user in userids:
                    delete_lastline("./user_json/" + user + ".json")
                    with open("./user_json/" + user + ".json", 'a', encoding="utf-8") as json_file:
                        json_file.write("	}\n  ]\n}")

def plot_activity():
    active_days=[]
    msg_per_day=[]
    with open("./user_json/FiveSpot.json", 'rb') as file:
        parser = ijson.parse(file)
        for prefix, event, value in parser:
            if prefix == "messages.item.message_time":
                if value not in active_days:
                    new_date=value
                    active_days.append(new_date)
                    msg_per_day.append(1)
                else:
                    msg_per_day[active_days.index(value)]+=1
        z=[x for _, x in sorted(zip(active_days, msg_per_day))]
        active_days.sort(key=lambda date: datetime.datetime.strptime(date, '%Y-%m-%d'))
        idx = pd.date_range(active_days[0], active_days[-1])
        res = {active_days[i]: z[i] for i in range(len(active_days))}
        s = pd.Series(res)
        s.index = pd.DatetimeIndex(s.index)
        s = s.reindex(idx, fill_value=0)
        s=s.resample("w").mean()
        s.to_csv("fuckthis.csv")
        print(s)
        x_dates = [datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in active_days]
        y_values = msg_per_day
        plt.plot(s,linestyle='solid',marker='None')
        plt.show()



from PIL import Image
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import codecs
def word_map():
    for user in list(userids.keys()):
        with codecs.open("./user_json/"+user+".json", 'rb',encoding='utf-8',errors='replace') as file:
            parser = ijson.parse(file)
            for prefix, event, value in parser:
                if prefix == "messages.item.message_content":
                    with open("server"+".txt", 'a', encoding='utf-8') as msg_txt:
                        try:
                            msg_txt.write(value+"\n")
                        except:
                            print("problem with this text:")
                            print(value)
                            pass
        text = codecs.open("server"+".txt", encoding='utf-8',errors='ignore').read()
        image_mask = np.array(Image.open("./Avatars/"+"server"+".png"))
        #stopwords = set(STOPWORDS)
        # #stopwords.add("said")
        wc = WordCloud(background_color="white", max_words=1000, mask=image_mask,
                       contour_width=3, contour_color='black',min_font_size=6)
        wc.generate(text)
        wc.to_file(user+"_cld.png")

'''
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(image_mask, cmap=plt.cm.gray, interpolation='bilinear')
    plt.axis("off")
    plt.show()'''

#user_messages()
#plot_activity()
word_map()
