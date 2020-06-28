#This file is designed to use the "learn" function of the mvnhmm for each location (387 in total) 

from mpi4py import MPI
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


#only use if learning for all 387 locations
numFilesPerRank = 387 // size
remainder = 387 % size
startLocation = 0


#method of evenly dividing computation based on the number of requested processes
if (rank < remainder):
  numFilesPerRank += 1
  startLocation = rank * numFilesPerRank

if (rank >= remainder):
  startLocation = remainder * (numFilesPerRank + 1) + (rank - remainder) * numFilesPerRank


#Define number of states and emissions
state = 4 
emission = 2 

#directory where mvnhmm is located
os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/bin")


vectCompNum = [1]


#for loop through the number of locations for each rank
for i in range(startLocation, startLocation + numFilesPerRank):
  
  #locaation of where parameter script is located
  myFile = open("../param_files/learn_param_file")
  
  #the following lines of code edit the parameter script for each location
  #this can be edited  
  content = myFile.readlines()
  myFile.close()

  #edit the state number 
  editState = content[7]
  editState = editState[:len(editState)-2]
  editState = editState + str(state) + "\n"
  content[7] = editState 

  #edit emission number
  editEmis = content[11]
  editEmis = editEmis[:len(editEmis)-2] 
  editEmis= editEmis + str(emission) + "\n"

  #edit the location of the data file
  dataFile = content[14]
  if (i < 10):
    dataFile = dataFile.replace("../data/potomacJulSep", "../data/datafile_387/PotomacJulSep_00" + str(i))
  if ((i >= 10) and (i < 100)):
    dataFile = dataFile.replace("../data/potomacJulSep", "../data/datafile_387/PotomacJulSep_0" + str(i))
  if (i >= 100):
    dataFile = dataFile.replace("../data/potomacJulSep", "../data/datafile_387/PotomacJulSep_" + str(i))
  content[14] = dataFile
 
  #edit the number of locations per script,
  #in this case, there will be 1
  number = content[17]
  number = number.replace("387", "1")
  content[17] = number

  #edit the numebr of emissions
  editEmis = editEmis.replace("387", "1")
  content[11] = editEmis


  #edit output location in the script
  output = content[len(content) - 7]
  if (i < 10):
    output = output.replace("../outputs/learn_hmm_potomac_julsep", "../outputs/output_387/" \
    + "learnOutput_00" + str(i))
  if ((i >= 10) and (i < 100)):
    output = output.replace("../outputs/learn_hmm_potomac_julsep", "../outputs/output_387/" \
    + "learnOutput_0" + str(i))
  if (i >= 100):
    output = output.replace("../outputs/learn_hmm_potomac_julsep", "../outputs/output_387/" \
    + "learnOutput_" + str(i))

  content[len(content) - 7] = output 
  
  #make tmpParamFile 
  myFile = open("../param_files/param_files_387/tmpLearnParamFile_" + str(i), "w")
  newContent = "".join(content)
  
  myFile.write(newContent)
  myFile.close()
  

  #run the mvnhmm executable using the location of the temporary parameter file 
  os.system("./mvnhmm ../param_files/param_files_387/tmpLearnParamFile_" + str(i))
