from mpi4py import MPI
import os
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


#
#numFilesPerRank = 387 // size
#remainder = 387 % size
#startLocation = 0

#if (rank < remainder):
#  numFilesPerRank += 1
#  startLocation = rank * numFilesPerRank
#
#if (rank >= remainder):
#  startLocation = remainder * (numFilesPerRank + 1) + (rank - remainder) * numFilesPerRank

#numLocations = [92, 89, 47, 159]
#for i in range(len(numLocations)):
#i = int(sys.argv[1])
#print(i)

#location of the mvnhmm
os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/bin")

myFile = open("../param_files/viterbi_param_file")
simContent = myFile.readlines()
myFile.close()



#for i in range(startLocation, startLocation + numFilesPerRank):

  #open file for simulations
  #myFile = open("../param_files/viterbi_potomac_julsep4state")
  #vitContent = myFile.readlines()
  #myFile.close()

##FOR SIMULATION##
#numComp = simContent[14]
#numComp = numComp.replace("387", str(numLocations[i]))
#simContent[14] = numComp
#numComp = simContent[11]
#numComp = numComp.replace("387", str(numLocations[i]))
#simContent[11] = numComp

numStates = simContent[7]
numStates = numStates.replace("4", str(rank + 2))
simContent[7] = numStates
#print(numStates)

output = simContent[len(simContent) - 8]
output = output.replace("../outputs/sim_potomac_data_julsep4state", "../outputs/05072020study16years/sim_outputs/s" + str(rank + 2) + "e3_DG")
simContent[len(simContent)-8] = output

modelFile = simContent[len(simContent)-5]
modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/05072020study16years/s" + str(rank+2) + "e3_DG")
simContent[len(simContent)-5] = modelFile

  #modelFile
#  modelFile = vitContent[len(vitContent)-5]
#  if (i < 10):
#     modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/output_387/learnOutput_00" + str(i))
#  if ((i >= 10) and (i < 100)):
#     modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/output_387/learnOutput_0" + str(i))
#  if (i >= 100):
#     modelFile = modelFile.replace("../outputs/learn_hmm_potomac_julsep4state", "../outputs/output_387/learnOutput_" + str(i))
#  vitContent[len(vitContent)-5] = modelFile
  #../outputs/learn_hmm_potomac_julsep4state

os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/outputs")
  #os.system("mkdir sim_outputs_potomac_julsep")
  #os.system("mkdir vit_outputs_potomac_julsep")
os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/bin")

#myFile = open("../param_files/tmpSimParamFile" + str(rank+2), "w")
newContent = "".join(simContent)
#myFile.write(newContent)
print(newContent)
#myFile.close()

#os.system("./mvnhmm ../param_files/tmpSimParamFile" + str(rank+2))

#os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/mvnhmm/param_files")
#os.system("rm tmp*")
