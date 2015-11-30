"""

  Filename: DatabaseManager.py
  Created by: DecodedLogic (04Nov15)
  Designed to successfully manage our accounts.

"""

import os, yaml

class Account:
    
    def __init__(self, username):
        self.username = username
        self.avatars = []
        
    def addAvatar(self, avatarFile):
        self.avatars.append(avatarFile)

def loadEntries():
    stream = os.open(databasePath, 'r+')
    docs = yaml.load_all(stream)
    accounts = []
    toons = []
    for doc in docs:
        if doc.get("class") == "DistributedToon":
            toons.append(doc)
        else:
            accounts.append(doc)
    print "Accounts: %s \nToons: %s" % (str(len(accounts), len(toons)))


print "Starting Database Manager by DecodedLogic. \nPlease wait..."

databasePath = os.path.join(os.path.dirname(__file__), "astrondb")
loadEntries()