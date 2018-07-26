import requests
import json
import re
 
url = 'https://www.renrendai.com/loan-1.html'
data = requests.get(url)
data.encoding = "utf-8"
data = data.text

anchor1 = data.find("var info")
anchor2 = data.find("var detail", anchor1+1)
info = data[anchor1+12:anchor2-3]
print(info)
print("\n[info]: " + str(type(info)) + "\n")

info_new = info.replace("\\u0022", '"').replace("\\u005C", '').replace("\\u002D", "-")
print(info_new)
print("\n[info_new]: " + str(type(info_new)) + "\n")

#info_json = json.dumps(info_new)
info_json = json.loads(info_new)
print(info_json)
print("\n[info_json]: " + str(type(info_json)) + "\n")
print(info_json["borrowStatus"])
