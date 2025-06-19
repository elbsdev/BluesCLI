from imports import textutils as txtu
from imports.configs import cfgs

import math
import pytz
import os
import json

from dateutil import parser
from datetime import datetime
from datetime import timezone
from chitose.app.bsky.feed.post import Post
from chitose.app.bsky.feed.post import ReplyRef
from chitose.com.atproto.repo.strong_ref import StrongRef

def printFormatted(postNum, gChrs, recType, authorName, authorHandle, dateStr, text, likes, reblogs, quotes, replies):
    print(gChrs[0]+'#'+str(postNum)+' '+recType)
    print(gChrs[0]+authorName)
    print(gChrs[0]+'@'+authorHandle)
    print(gChrs[0]+dateStr)
    print(gChrs[1]+gChrs[4]*len(dateStr))
    txtu.formatPostText(text)
    print(gChrs[0]+txtu.bcolors.blue+'   ♡: '+str(likes)+'   ⥦: '+str(reblogs+quotes)+'   ↳: '+str(replies)+txtu.bcolors.end)
    print(gChrs[2]+gChrs[3]*(os.get_terminal_size()[0]-len(gChrs[2])-1))

def listThread(threadJson):
    op = threadJson['thread']['post']
    gChrs = ['║', '╟', '╠', '═', '─']
    gChrsClr = [txtu.bcolors.green+gChrs[0]+txtu.bcolors.end, txtu.bcolors.green+gChrs[1]+txtu.bcolors.end, txtu.bcolors.green+gChrs[2]+txtu.bcolors.end, txtu.bcolors.green+gChrs[3]+txtu.bcolors.end, txtu.bcolors.green+gChrs[4]+txtu.bcolors.end]
    parsedDate = parser.parse(op['record']['createdAt'])
    correctDate = parsedDate.astimezone(cfgs.tz)
    dateStr = str(correctDate.hour)+':'+str(correctDate.minute)+' - '+str(correctDate.day)+'/'+str(correctDate.month)+'/'+str(correctDate.year)
    #Print the original post
    printFormatted(0, gChrsClr, '(OP)', op['author']['displayName'], op['author']['handle'], dateStr, op['record']['text'], op['likeCount'], op['repostCount'], op['quoteCount'], op['replyCount'])
    #Print the replies


def listPage(feedJson, startIndex, postsPerPage):
    cnt = 0
    cntBreak = startIndex+postsPerPage
    for post in feedJson['feed']:
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

        if (text != '' and cnt >= startIndex):
            recType = '(post)'
            if ('reply' in record): recType = '(reply)'
            gChrsClr = [txtu.bcolors.green+gChrs[0]+txtu.bcolors.end, txtu.bcolors.green+gChrs[1]+txtu.bcolors.end, txtu.bcolors.green+gChrs[2]+txtu.bcolors.end, txtu.bcolors.green+gChrs[3]+txtu.bcolors.end, txtu.bcolors.green+gChrs[4]+txtu.bcolors.end]
            printFormatted(cnt, gChrsClr, recType, authorName, authorHandle, dateStr, text, likes, reblogs, quotes, replies)

        cnt += 1

        
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
            listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'])
            print('Showing page '+str(page)+'/'+str(maxPages))
            refresh = False
        
        cmdIn = input('tl>')
        cmd = cmdIn.split('.')[0]
        param = cmdIn[cmdIn.find('.')+1:]
        
        if (cmd == 'r'):
            refresh = True
        
        elif (cmd == 'rcl'):
            os.system('clear')
            refresh = True
        
        elif (cmd == 'back'):
            break
        
        elif (cmd == 'like'):
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
        
        elif (cmd == 'reply'):
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
        
        elif (cmd == 'thread'):
            try:
                postNum = int(param)
                try:
                    postToView = feedJson['feed'][postNum]
                    uri = ''
                    if (not 'reply' in postToView['post']['record']):
                        uri = postToView['post']['uri']
                    else:
                        uri = postToView['post']['record']['reply']['root']['uri']
                    
                    thread = agent.get_post_thread(uri=uri)
                    threadJson = json.loads(thread)
                    
                except Exception as e:
                    print(txtu.bcolors.red+'Error! Posts couldn\'t be loaded.')
            except:
                print(txtu.bcolors.red+'The parameter provided is not a number.'+txtu.bcolors.end)
        
        elif (cmd == 'post'):
            record = Post(text=param, created_at=datetime.now(timezone.utc).isoformat())
            agent.post(record=record)
        
        elif (cmd == 'np'): #Next timeline page
            if (page < maxPages):
                page += 1
                startIdx = cfgs.cfg['postsPerPage']*(page-1)
                listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'])
                print('Showing page '+str(page)+'/'+str(maxPages))
        
        elif (cmd == 'pp'): #Previous timeline page
            if (page > 1):
                page -= 1
                startIdx = cfgs.cfg['postsPerPage']*(page-1)
                listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'])
                print('Showing page '+str(page)+'/'+str(maxPages))
        
        elif (cmd == 'help'):
            print(txtu.bcolors.blue+'---Timeline commands---'+txtu.bcolors.end)
            print('back  -  Go back to the main prompt.')
            print('r  -  Refresh your timeline.')
            print('rcl  -  Clear the screen and refresh your timeline.')
            print(txtu.bcolors.blue+'--Post interaction--'+txtu.bcolors.end)
            print('like  -  Like a post. Usage: like.<post number>')
            print('reply  -  Reply a post. Usage: reply.<post number>')
            print('post  -  Create a post. Usage: post.Your text here!')
            print('thread  -  Display a thread, containing the original post and all of it\'s replies. Usage: thread.<post number>')
            print(txtu.bcolors.blue+'--Pages--'+txtu.bcolors.end)
            print('np  -  Go to the next page.')
            print('pp  -  Return to the previous page.')
        
        else:
            print(txtu.bcolors.red+'Invalid command, type help for a list of commands.'+txtu.bcolors.end)
        ''' 
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
            case 'thread':
                try:
                    postNum = int(param)
                    try:
                        postToView = feedJson['feed'][postNum]
                        uri = ''
                        if (not 'reply' in postToView['post']['record']):
                            uri = postToView['post']['uri']
                        else:
                            uri = postToView['post']['record']['reply']['root']['uri']
                        
                        thread = agent.get_post_thread(uri=uri)
                        threadJson = json.loads(thread)
                        
                    except Exception as e:
                        print(txtu.bcolors.red+'Error! Posts couldn\'t be loaded.')
                except:
                    print(txtu.bcolors.red+'The parameter provided is not a number.'+txtu.bcolors.end)
            case 'post':
                record = Post(text=param, created_at=datetime.now(timezone.utc).isoformat())
                agent.post(record=record)
            case 'np': #Next timeline page
                if (page < maxPages):
                    page += 1
                    startIdx = cfgs.cfg['postsPerPage']*(page-1)
                    listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'])
                    print('Showing page '+str(page)+'/'+str(maxPages))
            case 'pp': #Previous timeline page
                if (page > 1):
                    page -= 1
                    startIdx = cfgs.cfg['postsPerPage']*(page-1)
                    listPage(feedJson, startIdx, cfgs.cfg['postsPerPage'])
                    print('Showing page '+str(page)+'/'+str(maxPages))
            case 'help':
                print(txtu.bcolors.blue+'---Timeline commands---'+txtu.bcolors.end)
                print('back  -  Go back to the main prompt.')
                print('r  -  Refresh your timeline.')
                print('rcl  -  Clear the screen and refresh your timeline.')
                print(txtu.bcolors.blue+'--Post interaction--'+txtu.bcolors.end)
                print('like  -  Like a post. Usage: like.<post number>')
                print('reply  -  Reply a post. Usage: reply.<post number>')
                print('post  -  Create a post. Usage: post.Your text here!')
                print('thread  -  Display a thread, containing the original post and all of it\'s replies. Usage: thread.<post number>')
                print(txtu.bcolors.blue+'--Pages--'+txtu.bcolors.end)
                print('np  -  Go to the next page.')
                print('pp  -  Return to the previous page.')
            case _:
                print(txtu.bcolors.red+'Invalid command, type help for a list of commands.'+txtu.bcolors.end)
        '''