import socket
import sys
from thread import *

messagecount = 0

def set_Up_Base ():
	base = {}

	user_1 = {'password' : '0723', 'subscribers' : [], 'unread_messages': []}
	user_2 = {'password' : '0345', 'subscribers' : [], 'unread_messages': []}
	user_3 = {'password' : '5545', 'subscribers' : [], 'unread_messages': []}
	user_4 = {'password' : '2338', 'subscribers' : [], 'unread_messages': []}

	base['teghveer'] = user_1
	base['keerat'] = user_2
	base['preet'] = user_3
	base['ahsees'] = user_4
	
	return base

def password_Check (conn):
	
	username = conn.recv(1024)
	passwrd = conn.recv(1024)

	if main_Base.has_key(username):
		profile = main_Base[username]
		
		if profile['password'] == passwrd:
			conn.send('true')
			online_users[username] = conn
			return username

		else:
			conn.send('false')
			return 'failed'

	else:
		conn.send('false')
		return 'failed'

def update_Hashtag (message, hashtag):
	
	if hashtag_Base.has_key(hashtag):
		hashtag_Base[hashtag].append(message)
	else:
		hashtag_Base[hashtag] = []
		hashtag_Base[hashtag].append(message)


def send(subs, conn, message):
	for sub in subs:
		if online_users.has_key(sub):
			online_users[sub].send('0101' + message)
		else:
			main_Base[sub]['unread_messages'].append(message)

def admin():
	global messagecount
	
	while (1):
		command = raw_input("Admin command: ")
		
		if command == "messagecount":
			print "\nNumber of messages received: " , messagecount
		
		elif command == "usercount":
			print "\nNumber of users currently logged on: ", len(online_users)
		
		elif command == "storedcount":
			total_unread = 0
			for user in main_Base:
				total_unread = len(main_Base[user]['unread_messages']) + total_unread
			print "\nTotal number of unread messages: " , total_unread
		
		elif command == "newuser":
			new_username = raw_input("\nusername to add: ")
			new_pass = raw_input("\npassword to add: ")
			user_new = {'password' : new_pass, 'subscribers' : [], 'unread_messages': []}			 
			main_Base[new_username] = user_new
			print "\nUser successfully added"
		else:
			"\nCommand does not exist!"		



def run_Twitter (conn):
	
	global messagecount

	start_new_thread (admin, ())
	state = 1
	uname = ''
	while(1):

		if state == 1:
			uname = password_Check(conn)
			if uname != 'failed':
				state = 2
			

		elif state == 2:
			response = conn.recv(4096)
			
			if response == 'request':
				conn.send(str(len(main_Base[uname]['unread_messages'])))
				state = 3
				
		# this is like the waiting state
		elif state == 3:
			
			selection = conn.recv(4096, socket.MSG_PEEK)
			if selection[:4] != '0101':
				selection = conn.recv(4096)
			
				if  selection == 'a':
					state = 4
				elif selection == 'b':
					state = 5
				elif selection == 'c':
					state = 6
				elif selection == 'd':
					state = 7
				elif selection == 'e':
					del online_users[uname]
					conn.close()
					break
				else:
					state = 3

		elif state == 4:
			
			choice = conn.recv(4096)
			if choice == "a":
				if len(main_Base[uname]['unread_messages']) == 0:
					conn.send("nothing")
				else:
					off_mess = ""
					for mess in main_Base[uname]['unread_messages']:
						off_mess = off_mess + mess + "\n\n"				
					conn.send(off_mess)
					main_Base[uname]['unread_messages'] = []
				conn.recv(4096)
				state = 3

			elif choice == "b":
				conn.send("proceed")
				username_mess = conn.recv(4096)
				
				off_mess = ""
				new_list = []
				for mess in main_Base[uname]['unread_messages']:
					if username_mess == mess[0:len(username_mess)]:
						off_mess = off_mess + mess + "\n\n"
					else:
						new_list.append(mess)
				main_Base[uname]['unread_messages'] = new_list

				if len(off_mess) == 0:
					conn.send("nomessages")
				else:
					conn.send(off_mess)
				conn.recv(4096)
				state = 3

			elif choice == "c":
				state = 3
			
			else:
				state = 3
				
			
		
		elif state == 5:
			choice = conn.recv(4096)
			conn.send("proceed")
			
			if choice == 'a':
				new_sub = conn.recv(4096)
				
				if main_Base[uname]['subscribers'].count(new_sub) != 0:
					conn.send("exists")
				
				elif new_sub == uname:
					conn.send("yourself")				

				elif main_Base.has_key(new_sub):
					main_Base[uname]['subscribers'].append(new_sub)
					conn.send("valid")
				else:
					conn.send("invalid")

			elif choice == 'b':
				if conn.recv(4096) == "ready":
					if len(main_Base[uname]['subscribers']) != 0:
						all_users = main_Base[uname]['subscribers']
						mess_users = ""
						for user in all_users:
							mess_users = mess_users + user + "\n"
						conn.send(mess_users)
						delete_user = conn.recv(4096)
						
						if main_Base[uname]['subscribers'].count(delete_user)!= 0:
							
							main_Base[uname]['subscribers'].remove(delete_user)
							conn.send("success")
						else:
							conn.send("nosuccess")

					else:
						conn.send("nosubs")
						conn.recv(4096) 
			state = 3	

		elif state == 6:
			
			message = conn.recv(4096)
			conn.send('goahead')
			hashtag = conn.recv(4096)
					
			if message == "00000":
				state = 3
				conn.send('goahead')

			elif message == "11111":
				state = 6
				conn.send('goahead')
			
			else:
				messagecount = messagecount + 1
				subs = main_Base[uname]['subscribers']
				message = uname + ": " + message + " " + hashtag
				send(subs, conn, message)
				update_Hashtag(message, hashtag)
				state = 3
				conn.send('goahead')
		
		elif state == 7:
			hash_request = conn.recv(4096)

			if hash_request == "a":
				conn.send("read_a")

			elif hashtag_Base.has_key(hash_request):
				hash_messages = hashtag_Base[hash_request]
				
				all_hash_mess = "Results for " + hash_request + "\n"
				if len(hash_messages) >= 10:
					limit = 10
				else:
					limit = len(hash_messages)
				for i in range (0, limit):
					all_hash_mess = all_hash_mess + hash_messages[i] + "\n"
				conn.send(all_hash_mess)

			else:
				conn.send("doesntexist")

			conn.recv(4096)
			state = 3


global online_users
online_users = {}

global hashtag_Base
hashtag_Base = {}

global main_Base 
main_Base = set_Up_Base()


HOST = ""
PORT = 5553

all_Clients = []

s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind ((HOST,PORT))

except socket.error, msg:
	print 'Bind failed . Error Code : ' + str(msg[0]) + 'Message: ' + msg[1]
	sys.exit()

s.listen(10)

while 1:
	#wait to accept a connection
	conn, addr = s.accept()
	
	# starting a new thread here
	start_new_thread (run_Twitter, (conn,))

s.close()
