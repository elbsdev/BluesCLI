#!/usr/bin/python
import textutils as txtu
import timeline as tl

import getpass

from configs import cfgs
from chitose import BskyAgent
from urllib.error import HTTPError

def main():
    print('BluesCLI v0.1 - Coded by Elbs <3')

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
        except HTTPError:
            print(txtu.bcolors.red+'Invalid session, you need to re-login.'+txtu.bcolors.end)
            isLoggedIn = False
    
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
            isLoggedIn = True
        except HTTPError:
            print(txtu.bcolors.red+'Login error, please check your credentials and try again.\n'+txtu.bcolors.end)
    
    #command processing
    while (not endProg):
        cmd = input('>')
        cmdSplit = cmd.split('.')

        match cmdSplit[0]:
            case 'quit':
                print('Quitting now, goodbye!')
                endProg = True
            case 'config':
                if (len(cmdSplit) > 1):
                    cfgs.config(cmdSplit[1])
                else:
                    print(txtu.bcolors.red+'No parameters provided, try \'configs.help´\' to get a list of parameters.'+txtu.bcolors.end)
            case 'tl':
                tl.timeline(agent)
            case _:
                print(txtu.bcolors.red+'Invalid command, try help to get a list of commands.'+txtu.bcolors.end)
    
    cfgs.saveConfigs()

if __name__ == '__main__':
    main()