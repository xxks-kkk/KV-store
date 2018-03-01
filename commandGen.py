# generation a list of commands
# just use put

import os
import random
import pickle


commands = ['joinServer' ,
            'killServer'  ,
            'joinClient' ,
            'breakConnection' ,
            'createConnection' ,
            'stablize' ,
            'printStore', 
            'put' ,
            'get' ]

command_Nums = 50
key = list('abcdefghijklmnopqrstuvwxyz1234567890')
clientid = list('56789')
chars = '1234567890qwertyuiopasdfghjklzxcvbnm'
lenchars = len(chars)
low = 1600
high = 2000
longerkeys = [i + j  + k for i in key for j in key for k in key]

kv_store = {}

with open('commandComplexTiny.txt', 'w') as f:
    #  use 3 servers at first
    for i in range(3):
        f.write("joinServer %d\n" % (i))
        f.write("joinClient %d %d\n" % (i + 5, i))

    for _ in range(command_Nums  ):
        length = random.randint(low,high)
        k = longerkeys[random.randint(0, len(longerkeys) - 1)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]


        f.write('put ' + clientid[random.randint(0,2)] + ' ' + k + ' ' + c + '\n')

    for i in range(3, 4):
        f.write("joinServer %d\n" % (i))
        f.write("joinClient %d %d\n" % (i + 5, i))

    for _ in range(command_Nums ):
        length = random.randint(low,high)
        k = longerkeys[random.randint(0, len(longerkeys) - 1)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]


        f.write('put ' + clientid[random.randint(0,3)] + ' ' + k + ' ' + c + '\n')

    for i in range(4, 5):
        f.write("joinServer %d\n" % (i))
        f.write("joinClient %d %d\n" % (i + 5, i))

    for _ in range(command_Nums  ):
        length = random.randint(low,high)
        k = longerkeys[random.randint(0, len(longerkeys) - 1)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]


        f.write('put ' + clientid[random.randint(0,4)] + ' ' + k + ' ' + c + '\n')

    f.write('breakConnection 0 2\nbreakConnection 0 3\nbreakConnection 0 4\nbreakConnection 1 3\nbreakConnection 1 4\nbreakConnection 2 4\n')

    for _ in range(command_Nums ):
        length = random.randint(low,high)
        k = longerkeys[random.randint(0, len(longerkeys) - 1)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]


        f.write('put ' + clientid[random.randint(0,4)] + ' ' + k + ' ' + c + '\n')
    f.write('killServer 4\n')

    for _ in range(command_Nums ):
        length = random.randint(low,high)
        k = longerkeys[random.randint(0, len(longerkeys) - 1)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]


        f.write('put ' + clientid[random.randint(0,3)] + ' ' + k + ' ' + c + '\n')

    for i in range(4, 5):
        f.write("joinServer %d\n" % (i))
        f.write("joinClient %d %d\n" % (i + 5, i))

    for _ in range(command_Nums  ):
        length = random.randint(low,high)
        k = longerkeys[random.randint(0, len(longerkeys) - 1)]
        c = ''
        for i in range(length):
            c += chars[random.randint(0, lenchars - 1)]


        f.write('put ' + clientid[random.randint(0,4)] + ' ' + k + ' ' + c + '\n')

    f.write("stabilize\n")

    for i in range(5):
        f.write("printStore %d\n" % (i))
        f.write("killServer %d\n" % (i))
    f.write("#\n")

