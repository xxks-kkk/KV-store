# generation a list of commands
# just use put

import os
import random


commands = ['joinServer' ,
            'killServer'  ,
            'joinClient' ,
            'breakConnection' ,
            'createConnection' ,
            'stablize' ,
            'printStore', 
            'put' ,
            'get' ]

command_Nums = 40
key = list('abcdefghijk')
clientid = list('56789')
chars = '1234567890-=qwertyuiopasdfghjklzxcvbnm,.//]!@#$%^&*())'
lenchars = len(chars)

with open('commandList', 'w') as f:
    for _ in range(command_Nums):
        length = random.randint(600,1000)
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]

        f.write('put ' + clientid[random.randint(0,4)] + ' ' + c + '\n')
