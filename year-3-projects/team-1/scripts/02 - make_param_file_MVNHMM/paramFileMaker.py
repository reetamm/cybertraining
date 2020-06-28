from mpi4py import MPI
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


#number of param_files per proccess
numFilesPerRank = 1

os.chdir("/umbc/xfs1/cybertrn/cybertraining2020/team1/research/python_scripts/githubCode")

for i in range(numFilesPerRank):
  #for making the paramter file, specify everything in the []
  param_file = open("generic_param_file", "w")
  
  param_file.write("# Action")
  param_file.write("\n")
  param_file.write("action [learn,viterbi,simulation,etc]")
  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Type of the model")
  param_file.write("\n")
  param_file.write("model_type [hmm]")
  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Number of hidden states")
  param_file.write("\n")
  param_file.write("num_states [number]")
  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Emission distribution")
  param_file.write("\n")
  param_file.write("emission")
  param_file.write("\n")
  param_file.write("independent [num of locations] [distribution type] [num of distributions]")
  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Data file")
  param_file.write("\n")
  param_file.write("data [data file location]")
  param_file.write("\n")
  param_file.write("\n")

  #FOR LEARN
  param_file.write("# Number of real-valued vector components for the data")
  param_file.write("\n")
  param_file.write("num_real_data_components [number]")
  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Number of output data sequences")
  param_file.write("\n")
  param_file.write("num_data_sequences [number]")
  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Length of each sequence")
  param_file.write("\n")

  ############### FOR LEARNING ############## 
  param_file.write("data_sequence_length [number]")
  ###########################################

  ############## FOR VITERBI ################
  """
  param_file.write("data_sequence_length_distinct [sequence of numbers]")
  """
  ###########################################

  param_file.write("\n")
  param_file.write("\n")
  param_file.write("# Output file")
  param_file.write("\n")
  param_file.write("output [output file location]")
  param_file.write("\n")
  param_file.write("\n")

############### FOR LEARNING ##############
param_file.write("# Number of random restarts")
param_file.write("\n")
param_file.write("num_restarts [num]")
param_file.write("\n")
param_file.write("\n")
param_file.write("em_verbose")
param_file.write("\n")
###########################################

############## FOR VITERBI ################
"""
param_file.write("# Model")
param_file.write("\n")
param_file.write("model_filename [model location]")
param_file.write("\n")
param_file.write("\n")
param_file.write("# Cross-validation")
param_file.write("# xval_type none")
param_file.write("\n")
"""
###########################################

############# FOR SIMULATION ##############
"""
param_file.write("# Model")
param_file.write("\n")
param_file.write("model_filename [model location]")
param_file.write("\n")
param_file.write("\n")
param_file.write("# Number of simulations per output sequence")
param_file.write("num_simulations [number]")
param_file.write("\n")
"""
###########################################
param_file.close()

#Run the parameter file
#os.system([location of the mvnhmm executable] [location of the parameter file])
