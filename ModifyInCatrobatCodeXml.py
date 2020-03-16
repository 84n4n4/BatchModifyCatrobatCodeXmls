import glob
from pathlib import Path
import tempfile
import zipfile
import shutil
import os
import re

# what is actually done to each code xml
# ###############################################
def removeAssertionVariables(xmlString):
    modifiedXml = xmlString.replace("    <userVariable>_ACTUAL</userVariable>\n", "")
    modifiedXml = modifiedXml.replace("    <userVariable>_EXPECTED</userVariable>\n", "")
    modifiedXml = modifiedXml.replace("    <userVariable>_READY</userVariable>\n", "")

    assertionVaribleRegex = re.compile(r"""    <userVariable type="UserVariable" serialization="custom">
      <userVariable>
        <default>
          <deviceValueKey>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}</deviceValueKey>
          <name>((_READY)|(_ACTUAL)|(_EXPECTED)){1}</name>
        </default>
      </userVariable>
    </userVariable>
""", re.MULTILINE)
    modifiedXml = assertionVaribleRegex.sub("", modifiedXml)
    return modifiedXml


# call here what you want to do with the code xml
# ###############################################
def modify(xmlString):
    xmlOld = xmlString[:]
    xmlNew = removeAssertionVariables(xmlString)
    printDiff(xmlOld, xmlNew)
    return xmlNew

# everything below is just for iterating through .catrobat files, and extracting from and recompressing them
# ###############################################
def printDiff(old, new):
    import difflib
    oldLines = old.splitlines(1)
    newLines = new.splitlines(1)
    diff = difflib.unified_diff(oldLines, newLines)
    print(''.join(diff))


# ###############################################
def recompressZipFileWOCodeXml(zipFileName):
    tempDir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempDir, 'new.zip')
        with zipfile.ZipFile(zipFileName, 'r') as zipRead:
            with zipfile.ZipFile(tempname, 'w') as zipWrite:
                for item in zipRead.infolist():
                    if item.filename != 'code.xml':
                        data = zipRead.read(item.filename)
                        zipWrite.writestr(item, data)
        shutil.move(tempname, zipFileName)
    finally:
        shutil.rmtree(tempDir)


# ###############################################
def getCodeXML(filename):
    try:
        zf = zipfile.ZipFile(filename, "r")
        codeXMLfile = zf.open("code.xml", "r")
        xmlString = codeXMLfile.read().decode("utf-8")
        codeXMLfile.close()
        zf.close()
        return xmlString
    except:
        print("error in:" + zf.filename)
        return


# ###############################################
def main():
    for filename in Path('').rglob('*.catrobat'):
        print(filename)
        xmlString = getCodeXML(str(filename))
        if xmlString:
            xmlString = modify(xmlString)
            recompressZipFileWOCodeXml(str(filename))
            with open("code.xml","w") as newCodeXml:
                newCodeXml.write(xmlString)
            with zipfile.ZipFile(str(filename), 'a') as zipFile:
                zipFile.write("code.xml")
            os.remove("code.xml")


# ###############################################
if __name__ == "__main__":
    main()
