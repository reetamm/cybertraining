import numpy as np
from sys import argv
import json

def loadFile(name):
  with open(name, "r") as f:
    grade = f.readlines()[1:]
    text = [text.split("\n") for text in grade]
    lines = text
  return lines

def startsWithString(item, val):
  if isinstance(item, str):
    if (len(item) >= len(val)):
      return item[0:len(val)] == val
    else:
      return False
  elif isinstance(item, list):
    return startsWithString(item[0], val)
  else:
    return False

def isState(item):
  return startsWithString(item, '# State')

def isEmptiness(item):
  if isinstance(item, str):
    if len(item) == 0:
      return True
    else:
      return False
  elif isinstance(item, list):
    return isEmptiness(item[0])
  else:
    return False

def lineToArray(line):
  s = ""
  if isinstance(line, list):
    s = line[0]
  else:
    s = line
  
  return np.array(list(map(lambda x: float(x), s.strip().split('\t'))))

def findLine(remainder, startsWith):
  while(not startsWithString(remainder[0], startsWith)):
    remainder = remainder[1:]
  return remainder

def getFirstEntryProb(remainder):

  #while(not startsWithString(remainder[0], '# First')):
  #  remainder = remainder[1:]
  remainder = findLine(remainder, '# First')
  #print(remainder[1][0].strip().split('\t'))
  #output = np.array(list(map(lambda x: float(x), remainder[1][0].strip().split('\t'))))
  output = lineToArray(remainder[1])
  return (output, remainder[2:])

def getConditionalProb(remainder, size):
  #while(not startsWithString(remainder[0], '# Conditional')):
  #  remainder = remainder[1:]
  remainder = findLine(remainder, '# Conditional')
  matrix = np.array(list(map(lineToArray, remainder[1:size+1])))
  return (matrix, remainder[size+1:])
  

#getFirstEntryProb(lines)

#o, r = getFirstEntryProb(lines)
#print(o)
#print(r)

def chunkToRow(chunk):
  # First and third lines are comments
  withoutComments = [chunk[1][0]] + list(map(lambda x: x[0], chunk[3:]))
  splitUp = map(lambda x: x.strip().split('\t'), withoutComments)

  result = []
  for a in splitUp:
    result = result + a

  output = np.array(list(map(lambda x: float(x), result)))
  return output

def parseState(remainder, chunkSize):
  output = []
  while((not isState(remainder[0])) and (not isEmptiness(remainder[0]))):
    chunk = remainder[0:chunkSize]
    remainder = remainder[chunkSize:]
    output = output + [chunkToRow(chunk)]
  
  return (np.array(output), remainder)

def getRemainingStates(remainder, chunkSize):
  states = []
  while (isState(remainder[0])):
    newState, remainder = parseState(remainder[1:], chunkSize)
    states = states + [newState]

  return np.array(states), remainder

#data, left = np.array(parseState(lines[12:]))

def processData(remainder, gammas, stateCount):
  chunkSize = gammas + 3
  firstEntryProb, remainder = getFirstEntryProb(remainder)
  conditionalProb, remainder = getConditionalProb(remainder, stateCount)
  remainder = findLine(remainder, '# State')
  states, remainder = getRemainingStates(remainder, chunkSize)

  return (firstEntryProb, conditionalProb, states)

def makeFilename(fnPrefix, num):
  return fnPrefix + str(num).rjust(3, '0')

def concatenateData(fnPrefix, stateCount=4, count=387, gammas=1):
  firstEntryProbs = []
  conditionalProbs = []
  states = np.empty((stateCount, 0, 4))
  for i in range(count):
    fep, cp, st = processData(loadFile(makeFilename(fnPrefix, i)), gammas, 
                                                                   stateCount)
    firstEntryProbs.append(fep)
    conditionalProbs.append(cp.tolist())
    states = np.concatenate((states, st), 1)


  return (np.array(firstEntryProbs), np.array(conditionalProbs), states)

def createFileTemplate(dname, fname):
  default = "learnOutput_"
  if len(fname) > 0:
    default = fname
  
  if (dname[-1] != "/"):
    dname += "/"

  return dname + default

if __name__ == "__main__":
  fname = ""
  dname = ""
  stateCount = 4
  locationCount = 387
  gammas = 1

  if ("-f" in argv):
    fname = argv[argv.index('-f') + 1]

  if ("-d" in argv):
    dname = argv[argv.index('-d') + 1]

  if ("-l" in argv):
    locationCount = int(argv[argv.index('-l') + 1])

  if ("-s" in argv):
    stateCount = int(argv[argv.index('-s') + 1])

  if ("-g" in argv):
    gammas = int(argv[argv.index('-g') + 1])

  print(dname)

  if ("-o" in argv) and (len(fname)>0 or len(dname)>0):
    outputname = argv[argv.index('-o') + 1]
    
    if len(dname) > 0:
      fileTemplate = createFileTemplate(dname, fname)
      firstEntryProbs, conditionalProbs, states = \
        concatenateData(fileTemplate, stateCount, locationCount, gammas)
      data = {"firstEntryProbs": firstEntryProbs.tolist(),
              "conditionalProbs": conditionalProbs.tolist(),
              "states": states.tolist()}
    else: 
      # Is able to automatically determine locationCount and states
      firstEntryProb, conditionalProb, states = \
        processData(loadFile(fname), gammas, stateCount)
      data = {"firstEntryProb": firstEntryProb.tolist(),
              "conditionalProb": conditionalProb.tolist(),
              "states": states.tolist()}

    with open(outputname, "w") as write_file:
      json.dump(data, write_file)
  else:
    print("Usage:")
    print("python script.py -f inputfile -o output.json")
    print("python script.py -d directory -f fileprefix -o output.json")
    print("Optional arguments:")
    print("-l locationCount (default = 387)")
    print("-s stateCount (default = 4)")
    print("-g gammas (default = 1)")

