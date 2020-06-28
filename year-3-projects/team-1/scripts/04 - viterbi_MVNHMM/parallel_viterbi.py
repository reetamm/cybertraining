#This file is designed to use the "viterbi" function of the mvnhmm for each location (387 in total)

from mpi4py import MPI
import os
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


numFilesPerRank = 387 // size
remainder = 387 % size
startLocation = 0

#method of evenly dividing computation based on the number of requested processes
if (rank < remainder):
  numFilesPerRank += 1
  startLocation = rank * numFilesPerRank

if (rank >= remainder):
  startLocation = remainder * (numFilesPerRank + 1) + (rank - remainder) * numFilesPerRank


#location of the mvnhmm
os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/bin")


for i in range(startLocation, startLocation + numFilesPerRank):
  
  #make edits to the parameter file
  myFile = open("../param_files/viterbi_param_file")
  vitContent = myFile.readlines()
  myFile.close()

  #eidt the number of emissions and the number of locations
  numEmis = vitContent[11]
  numEmis = numComp.replace("387", "1")
  numEmis = numComp.replace("3", "2")
  vitContent[11] = numComp

  #edit the number of locations from 387 to 1 as each script is only for 1 location
  numComp = vitContent[17]
  numComp = numComp.replace("387", "1")
  vitContent[17] = numComp

  

  #edit the location of the data file
  dataFile = vitContent[14]
  if (i < 10):
    dataFile = dataFile.replace("../data/potomacJulSep", "../data/datafile_387/PotomacJulSep_00" + str(i))
  if ((i >= 10) and (i < 100)):
    dataFile = dataFile.replace("../data/potomacJulSep", "../data/datafile_387/PotomacJulSep_0" + str(i))
  if (i >= 100):
    dataFile = dataFile.replace("../data/potomacJulSep", "../data/datafile_387/PotomacJulSep_" + str(i))
  vitContent[14] = dataFile

  #edit the location of the output file
  output = vitContent[len(vitContent) - 8]
  if (i < 10):
    output = output.replace("../outputs/viterbi_potomac_julsep4state", "../outputs/viterbi_387/viterbiOutput_00" + str(i))
  if ((i >= 10) and (i < 100)):
    output = output.replace("../outputs/viterbi_potomac_julsep4state", "../outputs/viterbi_387/viterbiOutput_0" + str(i))
  if (i >= 100):
    output = output.replace("../outputs/viterbi_potomac_julsep4state", "../outputs/viterbi_387/viterbiOutput_" + str(i))

  vitContent[len(vitContent)-8] = output

  #edit the location of the model file
  modelFile = vitContent[len(vitContent)-5]
  if (i < 10):
     modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/output_387/learnOutput_00" + str(i))
  if ((i >= 10) and (i < 100)):
     modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/output_387/learnOutput_0" + str(i))
  if (i >= 100):
     modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/output_387/learnOutput_" + str(i))
  vitContent[len(vitContent)-5] = modelFile

  os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/bin")

  #create the new paramter file and copy over the edited content into the file
  myFile = open("../param_files/param_files_387/tmpVitParamFile" + str(i), "w")
  newContent = "".join(vitContent)
  myFile.write(newContent)
  myFile.close()
  
  #run the mvnhmm executable using the newly created paramter file for the viterbi function
  os.system("./mvnhmm ../param_files/param_files_387/tmpVitParamFile" + str(i))
