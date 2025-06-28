import re
import os

class bcolors:
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[31m'
    yellow = '\033[33m]'
    bold = '\033[1m'
    end = '\033[0m'

def printErr(text):
    print(bcolors.red+text+bcolors.end)

def printEx(text, ex):
    print(bcolors.red+text+' '+bcolors.bold+str(ex)+bcolors.end)

def printWarn(text):
    print(bcolors.yellow+text+bcolors.end)

def noMojis(text): #removes emojis
    rgx = r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001FAFF]|[\U0000FE00-\U0000FEFF]||[\U0001D000-\U0001DFFF]' #two last regexes are for iphone compat
    return re.sub(rgx, '', text)

def formatPostText(text, prefix, level):
    txt = text
    maxSz = os.get_terminal_size()[0]-level-2
    lines = []

    while True:
        txtIdx = maxSz

        if (txtIdx >= len(txt)): 
            txtIdx = len(txt) - 1
        
        if (txtIdx >= maxSz):
            while(txt[txtIdx] != " "): #prevents cutting words in half
                txtIdx -= 1

        line = txt[0:txtIdx+1]
        remTxt = ''

        if (line.count('\n') > 0):
            line = line[0:line.find('\n')]
            remTxt = txt[txt.find('\n')+1:]
        else:
            remTxt = txt[txtIdx+1:]
        
        lines.append(line)
        txt = remTxt

        if (len(txt) == 0): break
    
    for li in lines:
        print(bcolors.green+prefix+bcolors.end+li)