import json

class ConfigFileReader:
    def __init__(self, configPath):
        self.configPath = configPath
        self.name = {}
        self.fileType = {}
        self.loopType = {}
        self.key = {}
        self.attributes = {}
        self.populateConfig(configPath)

    def populateConfig(self, path):
        with open(path) as json_file:
            data = json.load(json_file)
            self.name = data["name"]
            self.fileType = data["fileType"]
            self.loopType = data["loopType"]
            self.key = data["key"]
            self.attributes = data["attributes"]
    
    def describeConfig(self):
        print("Description the given configuration file:")
        print("=========================================")
        print("")

        print("1. General:")
        print("")
        print("Converter name: " + self.name)
        print("File type: " + self.fileType)
        print("Loop type: " + self.loopType)
        print("")

        print("2. Key/pivot information:")
        print("")
        print("Key type: " + self.key["keyType"])
        print("Key metatype: " + self.key["type"])
        print("Key referenced class: " + self.key["referenceClass"])
        print("Key referenced attribute: " + self.key["referenceAttribute"])
        print("Key regex: " + self.key["regex"])
        print("Key value name: " + self.key["valueName"])
        print("Key value type: " + self.key["valueType"])
        print("Key range -> Start: " + str(self.key["range"]["start"]) + " | End: " + str(self.key["range"]["end"]))
        print("")

        print("3. Attributes information:")
        print("")
        for inx, attr in enumerate(self.attributes.keys()):
            print("(" + str(inx) + ") Attribute " + str(attr) + ":")
            print("Index: " + str(self.attributes[attr]["index"]))
            print("Type: " + str(self.attributes[attr]["type"]))
            print("Value type: " + str(self.attributes[attr]["valueType"]))
            if("referenceClass" in self.attributes[attr] and "referenceAttribute" in self.attributes[attr]):
                print("Referenced class: " + str(self.attributes[attr]["referenceClass"]))
                print("Referenced attribute: " + str(self.attributes[attr]["referenceAttribute"]))
            print("")

        print("=========================================")

    def getJavaTypeName(self, name):
        return "java.lang." + name.title()

    def generateAdditionsFile(self):
        # 1. Generate the additions file
        # 1.1 Read additions file template
        additionsFile = ""
        with open('templates/additions_xml.template', 'r') as file:
            additionsFile = file.read()
        
        # 1.2 Replace class name 
        additionsFile = additionsFile.replace("CLASSNAME", self.name)

        # 1.3 Create references and attributes for the class
        classRefsAttrs = ""
        for attr in self.attributes.keys():
            # Is it a reference?
            if("referenceClass" in self.attributes[attr] and "referenceAttribute" in self.attributes[attr]):
                reverseReference = self.name[0].lower() + self.name[1:]
                classRefsAttrs += '<reference name="' + self.attributes[attr]["referenceClass"].lower() + '" referenced-type="' + self.attributes[attr]["referenceClass"] + '" reverse-reference="' + reverseReference + '"/>'
            else:
                classRefsAttrs += '<attribute name="' + attr + '" type="' + self.getJavaTypeName(self.attributes[attr]["type"]) + '"/>'

        # 1.4 Replace them in the text
        additionsFile = additionsFile.replace("<fill/>", classRefsAttrs)

        # 1.5 Add the collections for the references
        classRefsCollections = ""
        for attr in self.attributes.keys():
            # Is it a reference?
            if("referenceClass" in self.attributes[attr] and "referenceAttribute" in self.attributes[attr]):
                reverseReference = self.name[0].lower() + self.name[1:]
                classRefsCollections += '<class name="' + self.attributes[attr]["referenceClass"] + '" is-interface="true" extends="BioEntity"><collection name="' + reverseReference + '" referenced-type="' + self.name + '" reverse-reference="' + self.attributes[attr]["referenceClass"].lower() + '"/></class>'
            
        # 1.6 Replace them in the text
        additionsFile = additionsFile.replace("</classes>", classRefsCollections+"</classes>")

        return additionsFile
    
    def generateKeysFile(self):
        keysFile = ""
        with open('templates/keys.template', 'r') as file:
            keysFile = file.read()

        #keysFile = keysFile.replace("CLASSNAME", self.name)
        #keysFile = keysFile.replace("CLASSKEYATTRIBUTE", self.name)

        return keysFile

    def generateConverterCode(self):
        converterFile = ""
        with open('templates/converter.template', 'r') as file:
            converterFile = file.read()

        # 1. Generate the hashmaps for the references
        classRefsHashmaps = ""

        # First if the key uses a reference
        if("referenceClass" in self.key and "referenceAttribute" in self.key):
            classRefsHashmaps += 'private Map<String, String> ' + self.key["referenceClass"].lower() + 's = new HashMap<String, String>();'

        for attr in self.attributes.keys():
            # Is it a reference?
            if("referenceClass" in self.attributes[attr] and "referenceAttribute" in self.attributes[attr]):
                classRefsHashmaps += 'private Map<String, String> ' + self.attributes[attr]["referenceClass"].lower() + 's = new HashMap<String, String>();'
            
        # 2. Replace them in the text
        converterFile = converterFile.replace("// Data structures section", classRefsHashmaps)

        # 3. Create the blocks to get the class items
        getClassItemCodeTemplate = ""
        with open('templates/getClassItem.template', 'r') as file:
            getClassItemCodeTemplate = file.read()

        classRefsGetItems = ""
        # First if the key uses a reference
        if("referenceClass" in self.key and "referenceAttribute" in self.key):
            classRefsGetItems += getClassItemCodeTemplate.replace("CLASSNAMEMAP", self.key["referenceClass"].lower() + 's').replace("CLASSJOINATTRIBUTE", self.key["referenceAttribute"]).replace("CLASSNAME", self.key["referenceClass"])

        for attr in self.attributes.keys():
            # Is it a reference?
            if("referenceClass" in self.attributes[attr] and "referenceAttribute" in self.attributes[attr]):
                classRefsGetItems += getClassItemCodeTemplate.replace("CLASSNAMEMAP", self.attributes[attr]["referenceClass"].lower() + 's').replace("CLASSJOINATTRIBUTE", self.attributes[attr]["referenceAttribute"]).replace("CLASSNAME", self.attributes[attr]["referenceClass"])

        # 4. Replace them in the text
        converterFile = converterFile.replace("// Get class items blocks", classRefsGetItems)

        # 5. Generate the process code
        processCodeTemplate = ""
        with open('templates/processCodeColumnsLoop.template', 'r') as file:
            processCodeTemplate = file.read()

        converterFile = converterFile.replace("// Process code", processCodeTemplate)

        return converterFile

    def generateCode(self):
        # 1. Generate the additions file
        additionsFile = self.generateAdditionsFile()

        # 2. Generate keys file
        keysFile = self.generateKeysFile()

        # 3. Generate the code
        converterCode = self.generateConverterCode()

        # Show files
        print("Additions file:")
        print(additionsFile)
        print("")

        print("Keys file:")
        print(keysFile)
        print("")

        print("Converter code:")
        print(converterCode)
        print("")