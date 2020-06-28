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
  matrix = np.array(list(map(lineToArray, remainder[1:5])))
  return (matrix, remainder[5:])
  

#getFirstEntryProb(lines)

#o, r = getFirstEntryProb(lines)
#print(o)
#print(r)

def chunkToRow(chunk):
  withoutComments = [chunk[1][0]] + list(map(lambda x: x[0], chunk[3:5]))
  splitUp = map(lambda x: x.strip().split('\t'), withoutComments)

  result = []
  for a in splitUp:
    result = result + a

  output = np.array(list(map(lambda x: float(x), result)))
  return output

def parseState(remainder):
  output = []
  while((not isState(remainder[0])) and (not isEmptiness(remainder[0]))):
    chunk = remainder[0:5]
    remainder = remainder[5:]
    output = output + [chunkToRow(chunk)]
  
  return (np.array(output), remainder)

def getRemainingStates(remainder):
  states = []
  while (isState(remainder[0])):
    newState, remainder = parseState(remainder[1:])
    states = states + [newState]

  return np.array(states), remainder

#data, left = np.array(parseState(lines[12:]))

def processData(remainder):
  firstEntryProb, remainder = getFirstEntryProb(remainder)
  conditionalProb, remainder = getConditionalProb(remainder, 4)
  remainder = findLine(remainder, '# State')
  states, remainder = getRemainingStates(remainder)

  return (firstEntryProb, conditionalProb, states)

#firstEntryProb, conditionalProb, states = processData(loadFile(sys.argv[1]))
#print(firstEntryProb)
#print(conditionalProb)
#print(states)

if __name__ == "__main__":
  if ("-o" in argv) & ("-f" in argv):
    filename = argv[argv.index('-f') + 1]
    outputname = argv[argv.index('-o') + 1]

    firstEntryProb, conditionalProb, states = processData(loadFile(filename))
    data = {"firstEntryProb": firstEntryProb.tolist(),
            "conditionalProb": conditionalProb.tolist(),
            "states": states.tolist()}
    with open(outputname, "w") as write_file:
      json.dump(data, write_file)
  else:
    print("Usage:")
    print("python script.py -f input -o output.json")
