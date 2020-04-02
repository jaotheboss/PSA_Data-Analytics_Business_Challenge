import re
from time import strptime, strftime

_INPUT_PATHS = ('PN_TRANS_jan2020.txt', 'PN_TRANS_feb2020.txt')
_OUTPUT_PATHS = ('jan2020Cleaned.csv', 'feb2020Cleaned.csv')
_REGEX_PATTERN = re.compile('(link|webenv)(?:=)(.+?)(?:;)')
_HEADERS = 'date,userID,orgCode,urlType,category1,category2'

for inputPath, outputPath in zip(_INPUT_PATHS, _OUTPUT_PATHS):
    print('Currenting converting {} to {}...'.format(inputPath, outputPath))

    entryData = []
    with open(inputPath, 'r') as inputFile:
        for _ in range(3):
            inputFile.readline()
        for line in inputFile:
            if len(line.split(',')) < 4:
                continue
            date, userData, userID, orgCode = line.strip().split(',')
            if userData[:4] != 'link' and userData[:6] != 'webenv':
                continue

            # Split userDate
            searchRes = _REGEX_PATTERN.search(userData)
            urlType = searchRes.group(1)
            category1, *category2 = searchRes.group(2).split('>')
            category1 = category1.strip()
            category2 = category2[0].strip() if category2 else ''

            # Neaten date
            date = date.strip()
            date = strptime(date, '%d-%b-%y %I.%M.%S.%f %p')

            userID = userID.strip()
            orgCode = orgCode.strip()
            entryData.append((date, userID, orgCode, urlType, category1, category2))

    entryData.sort()

    with open(outputPath, 'w') as outputFile:
        outputFile.write(_HEADERS)
        outputFile.write('\n')
        for entry in entryData:
            date, *others = entry
            date = strftime('%d/%m/%Y %H:%M:%S', date)
            outputFile.write('{},{},{},{},{},{}\n'.format(date, *others))
    outputFile.close()

    print('Converting done!\n')