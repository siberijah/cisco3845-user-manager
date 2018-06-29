#!/usr/bin/python2.7

import sys
import random
import re
from pwgen import pwgen
from datetime import datetime
from netmiko import ConnectHandler

platform = 'cisco_ios'
host = 'pptp.example.com'
username = 'root'
password = 'password'
device = ConnectHandler(device_type=platform, ip=host, username=username, password=password)

output = 'script by siberijah 2016'
divider = '\n\t\t' + '#' * 60 + '\n\t\t'

header = ('\nUsage: ' + sys.argv[0] + ' <command> [args...]\n\n' +
          '\t<add> [username]\t\tAdd new user with pregenerated password\n' +
          '\t<add> [username] -p [password]\tAdd new user with custom password\n' +
          '\t<remove> [username]\t\tRemove user\n'
          '\t<users>\t\t\t\tShows users summary\n'
          '\t<info> [username]\t\tInfo about user\n')

if len(sys.argv) < 2:
    print header

elif sys.argv[1] == "users" and len(sys.argv) == 2:
    raw_users = device.send_command('sh run | i privilege 0 password 0')
    users = re.sub(r'[' '\s]', '/', raw_users).split('/')[1::7]
    raw_is_online = device.send_command('sh users | i Vi')
    is_online = re.split('\n', raw_is_online)
    print '\nStart time: ' + str(datetime.now()) + '\n'
    print divider
    for user in sorted(users):
        print ('\t\t' + user)
    print divider
    print ('\t\t' + str(len(users)) + ' user are registered\n\t\t' +
           str(len(is_online)) + ' users are online')
    print divider
    print "\nEnd time: " + str(datetime.now())
    print ''
    device.disconnect()

elif len(sys.argv) < 3:
    print header

elif sys.argv[1] == "add" and len(sys.argv) == 3:
    user_check = device.send_command('sh run | i ' + sys.argv[2] + ' priv') + \
		 device.send_command('sh run | i ' + sys.argv[2] + ' secret')
    print user_check
    if user_check != '':
        print(divider)
        print('\t\tUsername ' + sys.argv[2] + ' is already in use.\n\t\tChoose another one.')
        print(divider)
    else:
        print '\nStart time: ' + str(datetime.now()) + '\n'
        pass_rand = pwgen(8, symbols=False)
        while output != '':
            third_oct = str(random.randrange(0, 3))
            fourth_oct = str(random.randrange(2, 254))
            rand_ip = '10.14.' + third_oct + '.' + fourth_oct
            output = device.send_command('show run | i ' + rand_ip + ' service')
            print('Searching for free ip address.....\n')
        print('Found free IP: ' + rand_ip)
        print('\n\n\t\tWait a moment, configuring a Cisco router.....')
        command = ['username ' + sys.argv[2] + ' privilege 0 password 0 ' + pass_rand,
                   'username ' + sys.argv[2] + ' aaa attribute list ' + sys.argv[2],
                   'aaa attribute list ' + sys.argv[2],
                   'attribute type addr ' + rand_ip + ' service ppp protocol ip']
        new_user = device.send_config_set(command)
        device.send_command_expect('write memory')
        print('\t\tSuccessfully configured!\n')
        print(divider)
        print('\t\tLogin: ' + sys.argv[2] + '\n\t\tPassword: ' + pass_rand + '\n\t\tIP address: ' + rand_ip +
              '\n\t\tServer: pptp.nsu.ru\n\t\tFAQ: http://nsunet.ru/node/100'
              '\n\n\t\tSupport: 8 (383) 363-4141\n\t\t\t support@nsu.ru')
        print(divider)
        print "\nEnd time: " + str(datetime.now())
        print ''
    device.disconnect()

elif sys.argv[1] == "add" and sys.argv[3] == "-p" and len(sys.argv) == 5:
    if  len(sys.argv[4]) < 3 or len(sys.argv[4]) > 16:
	print(divider)
	print('\t\tPassword can be 3 to 15 character long. Choose another one.')
	print(divider)
	exit(0)
    else:
	passwd = sys.argv[4]
    user_check = device.send_command('sh run | i ' + sys.argv[2] + ' priv') + \
                 device.send_command('sh run | i ' + sys.argv[2] + ' secret')
    if user_check != '':
        print(divider)
        print('\t\tUsername ' + sys.argv[2] + ' is already in use.\n\t\tChoose another one.')
        print(divider)
    else:
        print '\nStart time: ' + str(datetime.now()) + '\n'
        while output != '':
            third_oct = str(random.randrange(0, 3))
            fourth_oct = str(random.randrange(2, 254))
            rand_ip = '10.14.' + third_oct + '.' + fourth_oct
            output = device.send_command('show run | i ' + rand_ip + ' service')
            print('Searching for free ip address.....\n')
        print('Found free IP: ' + rand_ip)
        print('\n\n\t\tWait a moment, configuring a Cisco router.....')
        command = ['username ' + sys.argv[2] + ' privilege 0 password 0 ' + passwd,
                   'username ' + sys.argv[2] + ' aaa attribute list ' + sys.argv[2],
                   'aaa attribute list ' + sys.argv[2],
                   'attribute type addr ' + rand_ip + ' service ppp protocol ip']
        new_user = device.send_config_set(command)
        device.send_command_expect('write memory')
        print('\t\tSuccessfully configured!\n')
        print(divider)
        print('\t\tLogin: ' + sys.argv[2] + '\n\t\tPassword: ' + passwd + '\n\t\tIP address: ' + rand_ip +
              '\n\t\tServer: pptp.nsu.ru\n\t\tFAQ: http://nsunet.ru/node/100'
              '\n\n\t\tSupport: 8 (383) 363-4141\n\t\t\t support@nsu.ru')
        print(divider)
        print "\nEnd time: " + str(datetime.now())
        print ''
    device.disconnect()

elif sys.argv[1] == "remove" and len(sys.argv) == 3:
    user_check = device.send_command('sh run | i ' + sys.argv[2] + ' privilege 0 pass')
    admin_check = device.send_command('sh run | i ' + sys.argv[2] + ' secret') + \
		  device.send_command('sh run | i ' + sys.argv[2] + ' privilege 0 secret')
    if admin_check + user_check == '':
        print(divider)
        print('\t\tThere is no ' + sys.argv[2] + ' on router or it was deleted early.')
        print(divider)
    elif admin_check != '':
	print(divider)
	print('\t\tYou are no allowed to remove user ' + sys.argv[2])
	print(divider)
    else:
        print '\nStart time: ' + str(datetime.now()) + '\n'
        print('\n\t\tWait a moment, configuring a Cisco router.....')
        command = ['no username ' + sys.argv[2],
                   'no aaa attribute list ' + sys.argv[2]]
        remove_user = device.send_config_set(command)
        device.send_command_expect('write memory')
        print('\t\tSuccessfully configured!\n')
        print(divider)
        print('\t\tUser ' + sys.argv[2] + ' has been successfully removed.')
        print(divider)
        print "\nEnd time: " + str(datetime.now())
        print ''
    device.disconnect()

elif sys.argv[1] == "info" and len(sys.argv) == 3:
    raw = device.send_command('sh run | s aaa attribute list ' + sys.argv[2]) + \
          device.send_command('sh run | s username ' + sys.argv[2] + ' priv')
    raw_admin = device.send_command('sh run | s username ' + sys.argv[2] + ' secret')
    is_online = device.send_command('sh users | i ' + sys.argv[2])
    if raw != '':
        info = re.sub(r'[' '\s]', '/', raw).split('/')
        print '\nStart time: ' + str(datetime.now()) + '\n'
        print(divider)
        if is_online != '':
            print('\t\tUsername ' + sys.argv[2] + ' is online now\n')
        else:
            print('\t\tUsername ' + sys.argv[2] + ' is offline now\n')
        print('\t\tPassword: ' + info[-1] + '\n\t\tIP address: ' + info[8])
        print(divider)
        print "\nEnd time: " + str(datetime.now())
        print ''
    elif raw_admin != '':
	print(divider)
	print('\t\tYou are not allowed to see info about username ' + sys.argv[2])
	print(divider)
    else:
        print(divider)
        print('\t\t' + sys.argv[2] + ' not found. This username is free to use.')
        print(divider)
    device.disconnect()

else:
    print header
