import textutils as txtu


import math
import pytz
import os
import json

from configs import cfgs
from dateutil import parser
from datetime import datetime
from datetime import timezone
from chitose.app.bsky.feed.post import Post
from chitose.app.bsky.feed.post import ReplyRef
from chitose.com.atproto.repo.strong_ref import StrongRef

def listPage(feedJson, startIndex, postsPerPage, mode):
    cnt = 0
    cntBreak = startIndex+postsPerPage
    for post in feedJson['feed']:
        printPost = False
        postData = post['post']
        authorHandle = postData['author']['handle']
        authorName = postData['author']['displayName']
        record = postData['record']
        parsedDate = parser.parse(record['createdAt'])
        correctDate = parsedDate.astimezone(cfgs.tz)
        dateStr = str(correctDate.hour)+':'+str(correctDate.minute)+' - '+str(correctDate.day)+'/'+str(correctDate.month)+'/'+str(correctDate.year)
        text = record['text']
        likes = postData['likeCount']
        reblogs = postData['repostCount']
        quotes = postData['quoteCount']
        replies = postData['replyCount']

        if (not cfgs.cfg['showEmojis']):
            authorName = txtu.noMojis(authorName)
            text = txtu.noMojis(text)
        
        gChrs = ['║', '╟', '╠', '═', '─']

        if (mode == 0): #timeline mode
            if (text != '' and cnt >= startIndex):
                recType = '(post)'
                if ('reply' in record): recType = '(reply)'
                printPost = True
            cnt += 1

        elif (mode == 1): #thread mode
            print('not impl')
        
        if (printPost):
            gChrsClr = [txtu.bcolors.green+gChrs[0]+txtu.bcolors.end, txtu.bcolors.green+gChrs[1]+txtu.bcolors.end, txtu.bcolors.green+gChrs[2]+txtu.bcolors.end, txtu.bcolors.green+gChrs[3]+txtu.bcolors.end, txtu.bcolors.green+gChrs[4]+txtu.bcolors.end]
            print(gChrsClr[0]+'#'+str(cnt-1)+' '+recType)
            print(gChrsClr[0]+authorName)
            print(gChrsClr[0]+'@'+authorHandle)
            print(gChrsClr[0]+dateStr)
            print(gChrsClr[1]+gChrsClr[4]*len(dateStr))
            txtu.formatPostText(text)
            print(gChrsClr[0]+txtu.bcolors.blue+'   ♡: '+str(likes)+'   ⥦: '+str(reblogs+quotes)+'   ↳: '+str(replies)+txtu.bcolors.end)
            print(gChrsClr[2]+gChrsClr[3]*(os.get_terminal_size()[0]-len(gChrs[2])-1))
            printPost = False
        
        if (cnt == cntBreak):
                break

        


def timeline(agent):
    print(txtu.bcolors.blue+'---Timeline---'+txtu.bcolors.end)
    page = 1
    maxPages = 1
    refresh = True
    feedJson = None

    while True:
        if (refresh == True):
            tl = agent.get_timeline(limit=50)
            feedJson = json.loads(tl)
            page = 1
            maxPages = math.ceil(len(feedJson['feed'])/cfgs.cfg['postsPerPage'])
            startIdx = cfgs.cfg['postsPerPage']*(page-1)
            listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'], 0)
            print('Showing page '+str(page)+'/'+str(maxPages))
            refresh = False
        
        cmdIn = input('tl>')
        cmd = cmdIn.split('.')[0]
        param = cmdIn[cmdIn.find('.')+1:]

        match cmd:
            case 'r':
                refresh = True
            case 'rcl':
                os.system('clear')
                refresh = True
            case 'back':
                break
            case 'like':
                try:
                    postNum = int(param)
                    try:
                        postToLike = feedJson['feed'][postNum]
                        agent.like(postToLike['post']['uri'], postToLike['post']['cid'])
                    except Exception as e:
                        print(repr(e))
                        print(str(e))
                        print(txtu.bcolors.red+'Error! Check the post number provided.'+txtu.bcolors.end)
                except Exception as e:
                    print(txtu.bcolors.red+'The parameter provided is not a number.'+txtu.bcolors.end)
            case 'reply':
                try:
                    postNum = int(param)
                    try:
                        postToReply = feedJson['feed'][postNum]
                        parentPost = StrongRef(uri=postToReply['post']['uri'], cid=postToReply['post']['cid'])
                        replyText = input('Reply>')
                        if (not 'reply' in postToReply['post']['record']):
                            rootPost = parentPost
                        else:
                            rootPost = StrongRef(uri=postToReply['post']['record']['reply']['root']['uri'], cid=postToReply['post']['record']['reply']['root']['cid'])
                        
                        replyRef = ReplyRef(root=rootPost, parent=parentPost)
                        record = Post(text=replyText, created_at=datetime.now(timezone.utc).isoformat(), reply=replyRef)
                        agent.post(record=record)
                    except Exception as e:
                        print(txtu.bcolors.red+'Error! Error sending reply. '+txtu.bcolors.end+str(e))
                except:
                    print(txtu.bcolors.red+'The parameter provided is not a number.'+txtu.bcolors.end)
            case 'post':
                record = Post(text=param, created_at=datetime.now(timezone.utc).isoformat())
                agent.post(record=record)
            case 'np': #Next timeline page
                if (page < maxPages):
                    page += 1
                    startIdx = cfgs.cfg['postsPerPage']*(page-1)
                    listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'], 0)
                    print('Showing page '+str(page)+'/'+str(maxPages))
            case 'pp': #Previous timeline page
                if (page > 1):
                    page -= 1
                    startIdx = cfgs.cfg['postsPerPage']*(page-1)
                    listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'], 0)
                    print('Showing page '+str(page)+'/'+str(maxPages))
            case _:
                print(txtu.bcolors.red+'Invalid command, type help for a list of commands.'+txtu.bcolors.end)