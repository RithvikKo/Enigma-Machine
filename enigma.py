# Enigma Machine Simulator

# Enigma Encryption is split into 8 parts:
    # 1.Get character (what they want to encrypt) from user
    # 2. Switch letter around via screen: for example, a -> e, b -> q, etc.
    # 3. Send letter through rotor, a table containing what letters map to what - corresponding letter changes
    # 4. First rotor moves after each letter is sent - the table containing the letters map shifts
    # 5. Repeat with second and third rotor. Second rotor shifts every Nth character, when n is length of encoding/character sequence. 
    #   Thirds shifts in corresponding powers of i, where i is rotarnumber
    # 6. Once reach third rotor, deflect back. Shift letter via second rotor, and back to first
    # 7. Send character back to screen, and switch letter
    # 8. Send letter back to user, now fully encrypted

import random
import copy
import os.path

class EnigmaMachine:

    def __init__(self, name, characters = "abcdefghijklmnopqrstuvwxyz", key = 0, number_rotars = 3):
        # alphabet determines which characters will be encrypted - default is english alphabet
        # key determines unique character matching in wheels - different keys give different machines 
        # and thus different encryptions. Number of Rotars can also be customized for different machine
        # name is unique identifer of machine for later use
        self.characters = list("abcdefghijklmnopqrstuvwxyz") if characters == "" else list(characters)
        self.name = name
        self.key = key
        self.number_rotars = 3 if number_rotars == "" else int(number_rotars)
        self.last_rotations = []

        self.plugboard = {}
        self.reflector = {}
        self.rotary_dials = []
        self.reversed_rotary_dials = []
        self.rotation_mapping = {}
        self.rotation_scheme = [0] * self.number_rotars
        self.initializeMachine()


    # makes enigma machine for user by creating all of the character matchings
    def initializeMachine(self):

        # setting a mapping of characters to position to allow for mapping rotations
        for i in range(0, len(self.characters)):
            self.rotation_mapping[i] = self.characters[i]
            self.rotation_mapping[self.characters[i]] = i

        # setting the random number generator key, unique for each key
        random.seed(self.key)
        # plugboard has to be symmetrical and can allow for repeat matching
        self.makeDial(self.plugboard, True, True)
        # reflector has to be symmetrical and cannot allow for repeat matching
        self.makeDial(self.reflector, True, False)

        # making custom number of rotary dials
        for i in range(self.number_rotars):
            dial = {}
            # configures the letter dials for the machine
            self.makeDial(dial, False, True)
            reversedDial = {dial[i] : i for i in dial}
            self.rotary_dials.append(dial)
            self.reversed_rotary_dials.append(reversedDial)
    
    def printDials(self):
        text = "\n"
        text += "Plugboard:\n"
        text += str(self.plugboard) + "\n\n"
        text += "Dials:\n"
        #print rotary dials
        for i in range(self.number_rotars):
            text += "Dial " + str(i) + ":" + "\n"
            text += str(self.rotary_dials[i]) + "\n\n"
        text += "Reflector:" + "\n"
        text += str(self.reflector) + "\n"
        return text
        
    # function that returns dictionary of letter mapping to others letters (a -> b) (letter a matches to letter b)
    def makeDial(self, dial_name, symmetricalTrue, repeateTrue):
        alphabets = copy.deepcopy(self.characters)
        # letters match to each other both ways (a -> q), (q -> a). q can't match to b
        if(symmetricalTrue):
            while(len(alphabets) !=0):
                # if a can match to a (a -> a)
                if(repeateTrue):
                    firstLetter = random.choice(alphabets)
                    secondLetter = random.choice(alphabets)
                    alphabets.remove(firstLetter)
                    if secondLetter in alphabets: alphabets.remove(secondLetter)
                # if a letter cannot match to itself (a !-> a), instead (a -> b), (b -> a)
                else:
                    firstLetter = alphabets.pop(random.randint(0, len(alphabets) - 1))
                    secondLetter = alphabets.pop(random.randint(0, len(alphabets) - 1))
                dial_name[firstLetter] = secondLetter
                dial_name[secondLetter] = firstLetter
        # if symmetrical matching isn't required (a -> b), (b -> c)
        elif(not symmetricalTrue):
            matching_Alph = copy.deepcopy(alphabets)
            for i in range(len(alphabets)):
                firstLetter = alphabets.pop(random.randint(0, len(alphabets) - 1))
                secondLetter = matching_Alph.pop(random.randint(0, len(matching_Alph) - 1))
                dial_name[firstLetter] = secondLetter
    
    def rotateDial(self, rotations):
        for i in range(self.number_rotars):
            lengthChar = len(self.characters)
            # modular 26 because after rotating 26 times, goes back to starting
            thisRotation = rotations % lengthChar
            self.rotation_scheme[i] += thisRotation
            rotations = int((rotations-thisRotation) / lengthChar)
            # accounting for overflows
            if(self.rotation_scheme[i] >= lengthChar):
                self.rotation_scheme[i] %= lengthChar
                rotations += 1 
    
    def translateCharacter(self, character):
        # pass through plugboard
        character = self.plugboard[character]

        # pass through rotary dials
        for i in range(self.number_rotars):
            rotar = self.rotary_dials[i]
            # rotation mapping accounts for rotating dials
            character = self.rotation_mapping[(self.rotation_mapping[character] - self.rotation_scheme[i]) % len(self.characters)]
            character = rotar[character]
            character = self.rotation_mapping[(self.rotation_mapping[character] + self.rotation_scheme[i]) % len(self.characters)]
        # go to reflector
        character = self.reflector[character]

        # go back through the rotary dials, this time reversed
        for i in range(self.number_rotars- 1, -1, -1):
            rotar = self.reversed_rotary_dials[i]
            character = self.rotation_mapping[(self.rotation_mapping[character] - self.rotation_scheme[i]) % len(self.characters)]
            character = rotar[character]
            character = self.rotation_mapping[(self.rotation_mapping[character] + self.rotation_scheme[i]) % len(self.characters)]
        # pass through plugboard
        character = self.plugboard[character]
        return character

    def translateText(self, text):
        self.last_rotations.append(0)
        translated_text = ""
        # translating each character individually and moving dial by 1 each time
        for i in range(len(text)):
            character = text[i]
            # checks if uppercase and converts it to normal
            if(character.isupper()):
                character = character.lower()
            if (character not in self.characters):
                translated_text += text[i]
            else:
                # translates character and rotates dial
                self.last_rotations[-1] +=1
                translatedCharacter = self.translateCharacter(character)
                if(text[i].isupper()):
                    translatedCharacter = translatedCharacter.upper()
                translated_text += translatedCharacter
                self.rotateDial(1)
        return translated_text

    def undoLastRotations(self):
        # undoes rotations if user makes mistake
        if(len(self.last_rotations) > 0):
            self.rotateDial(self.last_rotations[-1] * -1)
            self.last_rotations.pop()
    
    def writeToFile(self):
        # get useful information: name, key, number of rotars, current moves (to recreate rotational states), characters
        # write useful information to file: this is later used to load the data and recreate exact same machine in same state for later use
        savedInformation = open(self.name + ".txt", "w")
        savedInformation.write(self.key + "\n")
        numMoves = 0
        for i in range(self.number_rotars):
            numMoves += (len(self.characters) ** i) * self.rotation_scheme[i]
        savedInformation.write(str(numMoves) +"\n")
        savedInformation.write("".join(self.characters) + "\n")
        savedInformation.write(str(self.number_rotars) + "\n" )
        savedInformation.write(self.printDials())
        savedInformation.close()
    
    def loadMachine(file, name, password):
        # get corresponding information form saved file and set it into a machine for user use
        # this allows for user to use machine, exit program, and then use same machine alter again
        num_moves = int(file.readline()[:-1])
        characters = file.readline()[:-1]
        number_rotars = int(file.readline()[:-1])
        loaded = EnigmaMachine(name, characters, password, number_rotars)
        loaded.rotateDial(num_moves)
        return loaded

    def useMachine(machine):
        # bs / be for red padding
        bs = '\033[31m'
        be = '\033[39m'
        print("You are currently using the Enigma Machine")
        # check if they want to translate text, undo translations (to repair machine state), or exit out
        reply = input("Type " + bs + "TRANSLATE" + be + " to translate text, " + bs + "UNDO" + be + " to undo a translation, and " + bs + "EXIT" + be + " to exit out of machine\n").lower()
        while True:
            machine.writeToFile()
            if reply == "exit":
                print("Exited out of machine")
                return
            elif reply == "undo":
                print("Undid previous move")
                # changes rotational state to previous state before last translation
                machine.undoLastRotations()
            elif reply == "translate":
                text = input("Type in text you want to translate:\n")
                # translates text and returns it
                text = machine.translateText(text)
                print("\nTranslated Text:")
                print(bs + text + be)
            else:
                print("You did not type a valid response")
                print("Type " + bs + "TRANSLATE" + be + " to translate text, " + bs + "UNDO" + be + " to undo a translation, and " + bs + "EXIT" + be + " to exit out of machine\n")
            print()
            reply = input("Input next action\n")

    # User can either build a machine, or restore a previously used machine
    def startProgram():
        bs = '\033[31m'
        be = '\033[39m'
        action = input("Type " +bs+ "CREATE"  +be+ " to create a machine, type " +bs+ "ACCESS" +be+ " to access a machine \n").lower()
        while action not in ["create", "access"]:
            print("You did not type in a valid input. Please try again. Type in "  +bs+ "CREATE"  +be+ " or " +bs+ "ACCESS" +be)
            action = input().lower()
        # choosing to access machine means to login to a previous machine created, given name of machine and password (the key)
        if action == "access":
            while True:
                username = input("Enter the name/username of your machine:\n")
                password = input("What is the key/password of the machine:\n")
                # checks if file exists
                if os.path.exists(username + ".txt"):
                    information = open(username  + ".txt", "r")
                    key = information.readline()[:-1]
                    if key == password:
                        print("Succesfully logged in")
                        # loads machine for use using paramaters saved, and then runs machine
                        machine = EnigmaMachine.loadMachine(information, username, password)
                        EnigmaMachine.useMachine(machine)
                        break
                    else:
                        print("Incorrect username or password. Try again\n")
                else:
                    print("Incorrect username or password. Try again\n")
        else:
            name = input("Type in a unique name of a machine you want to create. Note: you will need to remember this as a username\n")
            key = input("""Type in key of machine you want to create. Note: you will need to remember this as a password. Each unique key generates a corresponding unique machine\n""")
            customize = input("Type "+ bs+ "DEFAULT" +be+ " if you want to create a default machine, otherwise "+ bs+ "ENTER" +be+" so you can further customize \n")
            if(customize.lower() == "default"):
                machine = EnigmaMachine(name, "", key)
                print("Machine loaded")
            else:
                # gets custom paramaters for custome engima machine for use
                print("Type in the characters that you want to allow to be encrypted. The number of characters must be even, or a character will be pruned. Example of characters:")
                print("abcdef\nNote that if you " + bs + "ENTER" + be + " the default is the english alphabet")
                alphabet = input()
                # length has to be even so each letter has a corresponding letter that it matches and vice versa
                if(len(alphabet) % 2 != 0):
                    alphabet = alphabet[1:]
                number_rotars = input("Type in the number of rotars you want the machine to contain. If you " +bs + "ENTER" + be+ " default is 3\n")
                machine = EnigmaMachine(name, alphabet, key, number_rotars)
                print("\nMachine Made!")
            # user uses engima machine
            EnigmaMachine.useMachine(machine)
            # user exits engima machine, save information
# starts engine machine
EnigmaMachine.startProgram()