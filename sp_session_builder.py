import xml.etree.cElementTree as ET
import sys
import re


class Session:
    def __int__(self):
        self.name = ""
        self.telnet = ""

    def setname(self, name):
        self.name = name

    def settelnet(self, telnet_link):
        self.telnet = telnet_link

    def getxml(self, xml_obj):
        try:
            ET.SubElement(
                xml_obj,
                "SessionData",
                SessionId="GNS3/{}".format(self.name),
                SessionName=self.name,
                ImageKey="computer",
                # match IP address
                Host=re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
                                self.telnet)[0],
                # match port
                Port=re.findall(r"\d{1,4}$", self.telnet)[0],
                Proto="Telnet",
                PuttySession="Default Settings",
                Username="",
                ExtraArgs="",
                SPSLFileName="",
                RemotePath="",
                LocalPath="")

        except Exception as error:
            # handle the exception
            print("An exception occurred:", error)


if __name__ == "__main__":

    session_file = sys.argv[1] if len(sys.argv) > 1 else "sessions.txt"

    xml_sessions = []

    xml_root = ET.Element("ArrayOfSessionData")
    # Add namespaces
    xml_root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    xml_root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    with open(session_file) as f:
        for i, row in enumerate(f.readlines(), start=1):
            if "#" in row:
                continue
            if i % 2 != 0:
                s = Session()
            if "telnet" in row:
                s.settelnet(row)
                s.getxml(xml_root)
            else:
                s.setname(row)

    tree = ET.ElementTree(xml_root)
    tree.write("{}.xml".format(session_file.replace('.txt', '')))

    # # fix superputty sessions bug by editing Sessions.XML
    # # https://github.com/jimradford/superputty/issues/686
    #
    # try:
    #     home_directory = os.path.expanduser('~')
    #     path = os.path.join(home_directory, 'Documents', 'SuperPuTTY')
    #     print(path)
    #     xml_new = []
    #     with open(os.path.join(path,"Sessions.XML")) as f_xml_old:
    #         for row in f_xml_old.readlines():
    #             xml_new.append(row.replace("Imported/",""))
    #     print(xml_new)
    #     print('ok')
    #     with open(r'{}'.format(os.path.join(path, "Sessions.XML")),'w')
    #       as f_xml_new:
    #         f_xml_new.write(''.join(xml_new))
    # except:
    #     print("errore correzione {}".format(path))
