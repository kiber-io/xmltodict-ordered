from xmltodict import parse, unparse

xmldict = parse(open('strings.xml', 'rb'))
unparse(xmldict, open('new.xml', 'w', encoding='utf8'))