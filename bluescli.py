#!/usr/bin/python
from imports import textutils as txtu
from imports import timeline as tl
from imports.configs import cfgs

import getpass

from chitose import BskyAgent
from urllib.error import HTTPError

def main():
    print('BluesCLI v0.3 - Coded by Elbs <3')

    isLoggedIn = False
    endProg = False
    agent = BskyAgent(service='https://bsky.social')
    cfgs.loadConfigs()

    if (cfgs.cfg['session']['accessJwt'] != ''):
        try:
            agent.session['accessJwt'] = cfgs.cfg['session']['accessJwt']
            agent.session['refreshJwt'] = cfgs.cfg['session']['refreshJwt']
            agent.session['active'] = cfgs.cfg['session']['active']
            agent.session['did'] = cfgs.cfg['session']['did']
            agent.get_timeline(limit=1)
            isLoggedIn = True
        except HTTPError as e:
            if (e.code == 400):
                txtu.printErr('Invalid session, you need to login.')
                isLoggedIn = False
            else:
                txtu.printErr('Connection error, status code: '+str(e.code))
                exit()
    
    while (not isLoggedIn):
        print('Please, provide your user credentials, your password will be hidden.')
        username = input('Handle (without @): ')
        password = getpass.getpass()
        try:
            agent.login(identifier=username, password=password)
            cfgs.cfg['session']['accessJwt'] = agent.session['accessJwt']
            cfgs.cfg['session']['refreshJwt'] = agent.session['refreshJwt']
            cfgs.cfg['session']['active'] = agent.session['active']
            cfgs.cfg['session']['did'] = agent.session['did']
            cfgs.saveConfigs()
            isLoggedIn = True
        except HTTPError as e:
            if (e.code == 401):
                txtu.printErr('Server returned 401. Identifier or password invalid.')
            else:
                txtu.printErr('Unhandled status code when loggin in: '+str(e.code))
                exit()
    
    #command processing
    while (not endProg):
        cmd = input('>')
        cmdSplit = cmd.split('.')

        if (cmdSplit[0] == 'quit'):
            print('Quitting now, goodbye!')
            endProg = True
        
        elif (cmdSplit[0] == 'config'):
            if (len(cmdSplit) > 1):
                cfgs.config(cmdSplit[1])
            else:
                cfgs.config('help')
        
        elif (cmdSplit[0] == 'tl'):
            tl.timeline(agent)
        
        elif (cmdSplit[0] == 'help'):
            print(txtu.bcolors.blue+'---Help---'+txtu.bcolors.end)
            print('config  -  change configuration variables.')
            print('help  -  this help text.')
            print('tl  -  enter timeline.')

        else:
            printErr('Invalid command, use the \'help\' command to get a list of commands.')
            
    cfgs.saveConfigs()

if __name__ == '__main__':
    main()