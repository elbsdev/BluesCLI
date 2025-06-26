import json
import os.path
import pytz

from imports import textutils as txtu

class cfgs:
    cfg = {
        'showEmojis' : True,
        'postsPerPage' : 4,
        'timezone' : 'America/Sao_Paulo',
        'clearScreen' : True,
        'session' : {
            'did' : '',
            'accessJwt' : '',
            'refreshJwt' : '',
            'active' : True
        }
    }

    tz = None

    descriptions = {
        'showEmojis' : 'Disable emojis for terminals that can\'t display them properly.',
        'postsPerPage' : 'Number of posts shown in each timeline page.',
        'timezone' : 'Your current timezone. Default is São Paulo because i\'m brazilian.',
        'clearScreen' : 'Clears the screen when navigating through timeline pages.'
    }

    def loadConfigs():
        if (os.path.isfile('config.json')):
            with open('config.json', 'r') as f:
                cfgs.cfg = json.loads(f.read())
                cfgs.tz = pytz.timezone(cfgs.cfg['timezone'])

    def saveConfigs():
        with open('config.json', 'w') as f:
            f.write(json.dumps(cfgs.cfg))

    def listConfigs():
        print(txtu.bcolors.blue+'---Configs---'+txtu.bcolors.end)
        for item in cfgs.cfg:
            if (type(cfgs.cfg[item]) != dict):
                print(item+' - '+str(cfgs.cfg[item]))

    def config(param):
        if ('=' in param):
            paramName = param.split('=')[0]
            paramVal = param.split('=')[1]
        else:
            paramName = ''
            paramVal = None
        if (param == 'list'):
            cfgs.listConfigs()
        elif (param == 'desc'):
            for item in cfgs.cfg:
                if (type(cfgs.cfg[item]) != dict):
                    print(item+' - '+cfgs.descriptions[item])
        elif (param == 'help'):
            print(txtu.bcolors.blue+'---Configs help---'+txtu.bcolors.end)
            print('The following parameters are available for use with '+txtu.bcolors.bold+'config'+txtu.bcolors.end+' command:')
            print('desc - Prints a description of each variable.')
            print('list - Lists the configuration variables and their current values.')
            print('help - Show this help text.')
            print('\nTo change a variable, the syntax is: '+txtu.bcolors.bold+'config.variableName=newValue'+txtu.bcolors.end)
            print('Example: '+txtu.bcolors.bold+'config.showEmojis=False'+txtu.bcolors.end+' will set showEmojis to False, disabling emojis.')
        else:
            if (paramName in cfgs.cfg):
                newVal = None
                varType = type(cfgs.cfg[paramName])
                if (varType == str):
                    newVal = paramVal
                    if (paramName == 'timezone'):
                        try:
                            cfgs.tz = pytz.timezone(newVal)
                        except:
                            newVal = None
                            print(txtu.bcolors.red+'Error! Invalid timezone.'+txtu.bcolors.end)
                elif (varType == int):
                    try:
                        newVal = int(paramVal)
                    except:
                        newVal = None
                        print(txtu.bcolors.red+'Error! This variable requires an int value, but the valued informed couldn\'t be parsed.'+txtu.bcolors.end)
                elif (varType == bool):
                    if (paramVal == 'True' or paramVal == 'true' or paramVal == '1'):
                        newVal = True
                    elif (paramVal == 'False' or paramVal == 'false' or paramVal == '0'):
                        newVal = False
                    else:
                        newVal = None
                        print(txtu.bcolors.red+'Error! This variable requires an boolean value, but the valued informed is invalid.'+txtu.bcolors.end)                                
                else:
                    print(txtu.bcolors.red+'Oops! cfg change for this type of variable is not implemented!'+txtu.bcolors.end)
                
                if (newVal != None):
                    cfgs.cfg[paramName] = newVal
                    print(txtu.bcolors.bold+paramName+txtu.bcolors.end+' set to '+txtu.bcolors.bold+paramVal+txtu.bcolors.end)
            else:
                print(txtu.bcolors.red+'Error! No variable named \''+paramName+'\' was found.'+txtu.bcolors.end)
