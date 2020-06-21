library(jsonlite)
library(gdata)
library(lubridate)
library(ggplot2)
library(matrixcalc)
## User inputs
setwd('D:/precip')
viterbiFile <- 'viterbi_potomac_julsep4state' #Output from MVNHMM viterbi process
paramFile <- 'params.json' #Output from learn_process.py
numLocation <- 387          #Number of locations
numStates   <- 4            #Number of states in HMM
numMix      <- 3            #Number of mixture components
numGamma <- numMix - 1      #Number of Gamma components
numExp <- numMix - 1        #Number of Exponential components
numDays <- 92               #Number of days of year being used
numYrs <- 18                #Number of years of data
dataLen <- numDays*numYrs
startDate <- '2001-07-01'
endDate <- '2001-09-30'
startYear <- 2001
endYear <- startYear + numYrs - 1

## Import files
source('99 - functionDefns.R')
obsdata <- read.table('PotomacJulSep')
#testing = read.table('testingdata')
#training = read.table('trainingdata')
#params = fromJSON('training.json')
params <- fromJSON(paramFile)
viterbistates <- read.table(viterbiFile)

## Spatiotemporal coordinats
date <- seq(ymd(startDate),ymd(endDate),by='days')
month <- month(date)
day <- day(date)
year <- rep(startYear:endYear,each=numDays)

## Getting the lat and long requires the forcig files to be in the same directory
## Getting the lat and long requires the forcig files to be in the same directory
#file_names <- list.files(pattern="forcing_*",full.names = T)
#lat <- substr(file_names,11,17)
#long <- substr(file_names,19,26)
#lat <- as.numeric(as.character(lat))
#long <- as.numeric(as.character(long))
#write.table(data.frame(lat,long),'latlong')
latlong = read.table('latlong')
lat = latlong[,1]
long = latlong[,2]

## Parameters of the HMM from the learn process
alpha <- params$firstEntryProb #Initial distribution at
PI <- params$conditionalProb #Transition probability matrix
dim(params$states)
mix <- params$states[,,1:numMix] #mixture probabilities
tmp <- numMix + 1
gammaparams <- vector(mode = "list", length = numMix) #List to store Gamma parameters
for(i in 1:numGamma){
  gammaparams[[i]] <- params$states[,,(tmp:(tmp+1))]
  tmp <- tmp + 2
}

viterbistates <- as.vector(t(viterbistates))
viterbistates <- viterbistates[!is.na(viterbistates)]
viterbistates <- viterbistates + 1 #Because MVNHMM has states starting from 0
length(viterbistates) #Should be the same length as the input data


gamma.cors <- vector(mode = 'list', length = numStates) #List with correlation matrix for each state
randNormAmt <- array(rnorm(numLocation*dataLen), dim=c(numLocation, dataLen)) #Generate Standard Normal marginals
inputrandAmt <- array(NA, dim=c(numLocation, dataLen)) #dim c(numLoc, numDays)
for(i in 1:numStates)
{
  #amtDataObs <- training[viterbistates==i,]
  amtDataObs <- obsdata[viterbistates==i,] #Observed Data for the i-th state

  #amtDataObs[amtDataObs==0] <- NA
  amtCor <- cor(amtDataObs, use="pairwise.complete.obs", method="spearman") #correlation matrix
  #amtCor <- cor(amtDataObs, use="pairwise.complete.obs")
  binorCor <- 2*sin(pi*amtCor/6) #Spearman to Pearson
  gamma.cors[[i]] <- FnFixCorrMatrix(binorCor) #Make it positive definite
  inputrandAmt[,viterbistates==i] <- t(gamma.cors[[i]]) %*% randNormAmt[,viterbistates==i] #Correlated Normals
  print(i)
}

inputrandAmt <- pnorm(inputrandAmt) #Normal to Uniform
inputrandAmt <- t(inputrandAmt)
synthetic <- array(0,dim=c(dataLen,numLocation)) #Variable to store synthetic data
set.seed(1)
simdata <- matrix(runif(dataLen*numLocation),nrow = dataLen, ncol = numLocation) #runif to select mixture component
PI.array <- array(PI,dim = c(numStates,numStates,1)) #Array format needed for generate.mmc() function
viterbistates2 <- generate.mmc(matrix(runif(dataLen),ncol=1),alpha = matrix(alpha, nrow = 1), PI=PI.array) #States for each day
viterbistates2 <- as.vector(as.numeric(viterbistates2))
for(i in 1:dataLen)
{
  dailystate <- viterbistates2[i] #Find out the state for day i
  for(j in 1:numLocation)
  {
    simdata[i,j] <- initial.state(simdata[i,j],mix[dailystate,j,]) #Which mixture component will be chosen?
    if(simdata[i,j]>1) #1 corresponds to no rain; so this is executed only for rain
    {
      which.gamma <- simdata[i,j] - 1 #Which Gamma component will it rain from?
      #Synthetic data for location j on day i
      synthetic[i,j] <- qgamma(inputrandAmt[i,j],shape = gammaparams[[which.gamma]][dailystate,j,1], rate = gammaparams[[which.gamma]][dailystate,j,2])
    }
    }

}
#tmp <- cor(training)
tmp <- cor(obsdata) #Correlation matrix of observed data
#cor.training <- tmp[col(tmp) != row(tmp)]
cor.obsdata <- tmp[col(tmp) != row(tmp)] #Just keep the unique values
#tmp <- cor(testing)
#cor.testing <- tmp[col(tmp) != row(tmp)]
tmp <- cor(synthetic) #Correlation matrix of synthetic data
cor.synthetic <- tmp[col(tmp) != row(tmp)] #Just keep the unique values
#summary(cor.training - cor.testing)
#summary(cor.training - cor.synthetic)
#summary(cor.testing - cor.synthetic)
summary(cor.obsdata - cor.synthetic)
write.table(synthetic,'gammacopula')
