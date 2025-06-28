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
        'clearScreen' : 'Clears the screen when navigating through timeline pages.',
    }

    def loadConfigs():
        if (os.path.isfile('config.json')):
            tmpCfg = None
            with open('config.json', 'r') as f:
                try:
                    tmpCfg = json.loads(f.read())
                except:
                    txtu.printWarn('An error ocurred when loading the config file, the file will be ignored.')
                    tmpCfg = None

            if (tmpCfg != None):
                for item in tmpCfg:
                    if (item in cfgs.cfg):
                        cfgs.cfg[item] = tmpCfg[item]
                    else:
                        txtu.printWarn(item+' is not a valid config entry, ignoring it.')
            
            #load the timezone
            cfgs.tz = pytz.timezone(cfgs.cfg['timezone'])
            

    def saveConfigs():
        with open('config.json', 'w') as f:
            f.write(json.dumps(cfgs.cfg))

    def listConfigs():
        print(txtu.bcolors.blue+'---Configs---'+txtu.bcolors.end)
        for item in cfgs.cfg:
            if (type(cfgs.cfg[item]) != dict):
                print(item+' - '+str(cfgs.cfg[item]))

    def listConfigsDescs():
        for item in cfgs.cfg:
            if (type(cfgs.cfg[item]) != dict):
                print(item+' - '+cfgs.descriptions[item])

    #TODO: remove the spaghetti code from the ifs and elifs, put them in dedicated functions so the code below doesnt look so polluted
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
            cfgs.listConfigsDescs()
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
                            txtu.printErr('Invalid timezone.')
                elif (varType == int):
                    try:
                        newVal = int(paramVal)
                    except Exception as e:
                        newVal = None
                        txtu.printEx('The value informed couldn\'t be parsed as an integer.  ', e)
                elif (varType == bool):
                    if (paramVal == 'True' or paramVal == 'true' or paramVal == '1'):
                        newVal = True
                    elif (paramVal == 'False' or paramVal == 'false' or paramVal == '0'):
                        newVal = False
                    else:
                        newVal = None
                        txtu.printErr('This variable requires a boolean value. Valid values: True,true,1 or False,false,0')
                else:
                    txtu.printWarn('Type '+str(varType)+' change not implemented yet.') #This message shoudn't be shown, its there just in case
                
                if (newVal != None):
                    cfgs.cfg[paramName] = newVal #If everything was OK, the new value is set
                    print(txtu.bcolors.bold+paramName+txtu.bcolors.end+' set to '+txtu.bcolors.bold+paramVal+txtu.bcolors.end)
            else:
                txtu.printErr('Error, no variable named \''+paramName+'\' was found.')
