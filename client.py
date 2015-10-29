import socket
import sys
from thread import *

def wait_for_messages(s):
	while (logout):
		message = s.recv(4096, socket.MSG_PEEK)
		
		if message[:4] == '0101':
			message = s.recv(4096)
			message = message[4:]
			print "\n\n" + "New message"
			print message
			print "\n"


def print_menu():
	
	print "\n         Menu     "
	print "(a) See Offline Messages"
	print "(b) Edit Subscriptions"
	print "(c) Post a Message"
	print "(d) Hashtag Search"
	print "(e) Logout"
	selection = raw_input ('\nPlease enter a selection: ')
	return selection


try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

except socket.error, msg:
	print 'Failed to create socket. Error code: ' + str (msg[0])
	sys.exit()

host = '10.0.0.4'
port = 5553


try:
	remote_ip = socket.gethostbyname(host)

except socket.gaierror:
	print 'Hostname could not be resolved. Exiting'
	sys.exit()

#connecting to server
s.connect ((remote_ip, port))

state = 1
global logout
logout = True

while (1):
	
	if state == 1:
		username = raw_input('Please enter your username: ')
		password = raw_input('Please enter your password: ')

		s.send(username)
		s.send(password)

		reply = s.recv(4096)

		if reply == 'true':
			state = 2
		else:
			print '\nAccount not found. Please try again.\n'

	elif state == 2:
		s.send('request')
		num_messages = s.recv(4096)
		print "\nWelcome!!! The number of unread messages you have is: " , num_messages
		start_new_thread(wait_for_messages, (s,))	
		state = 3

	elif state == 3:
		
		selection = print_menu()
		
		if selection == 'a':
			state = 4
			s.send(selection)
		elif selection == 'b':
			state = 5
			s.send(selection)
		elif selection == 'c':
			state = 6
			s.send(selection)
		elif selection == 'd':
			state = 7
			s.send(selection)
		elif selection == 'e':
			print '\nYou have selected to logout. Goodbye'
			s.send(selection)
			logout = False
			s.close()
			sys.exit(0)
		else:
			print '\nInvalid Selection. Please try again!'
			s.send('wrong')

	elif state == 4:
		
		print ("\nPress a to view all offline messages")
		print ("Press b to view messages from a specific subscription")
		print ("Press c to return to the menu")
		choice = raw_input("Command: ")

		s.send(choice)
		if choice == "a":
			if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
				offline_messages = s.recv(4096)
				
				if offline_messages == "nothing":
					print "\nNo offline messages to display\n"
				
				else:
					print "\n" + offline_messages
				s.send("done")
			state = 3
		
		elif choice == "b":
			if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
				s.recv(4096)
				username_mess = raw_input("\n" + "Please enter username whose offline messages who would like to see : ")	
				s.send(username_mess)
				
				if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
					mess = s.recv(4096)
					if mess == "nomessages":
						print "\nNo offline messages to display from this subscription.\n"
					else:
						print "\n" + mess + "\n"
					s.send("done")
			state = 3

		elif choice == "c":
			state = 3

		else:
			print "\nInvalid selection made.\n"
			state = 3
	
	elif state == 5:
		
		choice = raw_input("\nPress a to add a subscription or b to delete a subsciption: ")
		s.send(choice)
		if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
			s.recv(4096)
			
			if choice == 'a':
				username = raw_input("\nEnter the username of the subsciption you wish to add: ")
				s.send(username)
				if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
					answer = s.recv(4096)
					
					if answer == "valid":
						print "\nSubscription successfully added\n"
					
					elif answer == "exists":
						print "\nError! You are already subscribed to this username!\n"

					elif answer == "yourself":
						print "\nError! You cannot subscribe to yourself!\n"
					
					else:
						print "\nError! The username you entered does not exist!\n"
					state = 3

			elif choice == 'b':
				s.send("ready")
				if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
					list_users = s.recv(4096)
				
					if list_users != "nosubs":
						print "\n" + list_users
						s.send(raw_input("\nEnter username of subscribor you would like to delete: "))
						if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
							result = s.recv(4096)
							if result == "success":
								print "\nSubscription successfully deleted!\n"
							else:
								print "\nThe username you entered does not exist!\n"
				
					else:
						print "\nNo subscribers to delete!\n"
						s.send("goingtomenu")

			else:
				print "\nError! You entered an invalid choice.\n"

		state = 3
				
	elif state == 6:
		
		message = raw_input ('\nInput a message of size 140 characters or less (a to cancel or b to try again) :')
		
		if message == "a":
			s.send("00000")
			
			if s.recv(4096 , socket.MSG_PEEK)[:4] != '0101':
				s.recv(4096)
				s.send("00000")

				if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
					s.recv(4096)
					state = 3

		elif message == "b":
			s.send("11111")
			
			if s.recv(4096 , socket.MSG_PEEK)[:4] != '0101':
				s.recv(4096)	
				s.send("11111")
				
				if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
					s.recv(4096)

		else:

			if len(message) <= 140:
				s.send(message)
				
				if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
					s.recv(4096)
					hashtag = raw_input('Input a hashtag: ')
					s.send(hashtag)
					
					if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
						s.recv(4096)
						state = 3

			else:
				print("Error! Message is too long!\n")
				s.send("11111")
			
				if s.recv(4096 , socket.MSG_PEEK)[:4] != '0101':
					s.recv(4096)	
					send("11111")
				
					if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
						s.recv(4096)
				

	elif state == 7:
		
		hash_search = raw_input("\nEnter a hashtag to search for or press a to go to the menu: ")
		s.send(hash_search)
		if s.recv(4096, socket.MSG_PEEK)[:4] != '0101':
			results = s.recv(4096)
			
			if results == "doesntexist":
				print "\nSorry, no messages exist for the specified hashtag."
			elif results != "read_a":
				print "\n" + results

			s.send("done")
			
		state = 3
		


		
	
