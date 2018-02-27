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
key = list('abcdefg')
clientid = list('56789')
chars = '1234567890-=qwertyuiopasdfghjklzxcvbnm,.//]!@#$%^&*())'
lenchars = len(chars)




with open('commandConnected', 'w') as f:
    for i in range(5):
        f.write("joinServer %d\n" % (i))
        f.write("joinClient %d %d\n" % (i + 5, i))

    for _ in range(command_Nums):
        length = random.randint(600,1000)
        k = key[random.randint(0, 6)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]

        f.write('put ' + clientid[random.randint(0,4)] + ' ' + k + ' ' + c + '\n')

    f.write("stablize\n")

    for i in range(5):
        f.write("printStore %d\n" % (i))
        
    f.write("#\n")