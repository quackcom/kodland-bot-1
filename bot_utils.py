import random

possible_messages_activity = [
    "Playing with passwords",
    "Being useful",
    "Hello",
    "Generating passwords",
    "Helping users",
    "Monitoring messages",
    "Checking Zippy.py"
]

possible_messages_benvenuto = [
    "Ciao!",
    "Benvenuto!",
    "Ehilà!"
]

possible_messages_arrivederci = [
    "Ciao!",
    "Arrivederci!",
    "Ci si vede!"
]

def onlineMessageCycle():
    return random.choice(possible_messages_activity)

def gen_pass(pass_length):
    elements = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890+-/*!&$#?=@<>"
    password = ""

    for i in range(pass_length):
        password += random.choice(elements)

    return password