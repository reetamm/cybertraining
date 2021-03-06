library(ggplot2)
library(forecast)
library(lubridate)
library(gdata)
library(psych)
theme_set(theme_bw())
library(sf)

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
inputdata <- read.table('PotomacJulSep')

hmmoutput <- read.table('sim_potomac_data_julsep')
copulaoutput <- read.table('JulSepWilksSyn',header = T)
#View(outputdata)
#outputdata <- outputdata[,-388]

## Spatiotemporal coordinats
date <- seq(ymd(startDate),ymd(endDate),by='days')
month <- month(date)
day <- day(date)
year <- rep(startYear:endYear,each=numDays)

#### State sequence plots
viterbigrid <- data.frame(states = as.character(viterbistates), day=rep(1:numDays, numYrs), year = year)

ggplot(viterbigrid, aes(x=day, y=year, fill=states)) + geom_tile() +
      scale_fill_brewer(type = 'qual') + scale_y_continuous(breaks=year) +
      theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
      axis.text.x = element_text(color = "grey20", size = 10, angle = 0, hjust = .5, vjust = .5, face = "plain"),
      axis.text.y = element_text(color = "grey20", size = 10, angle = 0, hjust = 1, vjust = 0, face = "plain"),
      axis.title.x = element_text(color = "grey20", size = 17, angle = 0, hjust = .5, vjust = 0, face = "plain"),
      axis.title.y = element_text(color = "grey20", size = 17, angle = 90, hjust = .5, vjust = 2, face = "plain"),
      legend.text = element_text(size=12), legend.title = element_text(size=15),legend.key.size = unit(.8, "cm")) +
      labs(x='Days from July 1 to September 30', y = 'Year', fill = 'States')


occurrence.obs <- array(0, dim=c(dataLen,numLocation))
for(i in 1:dataLen)
  for(j in 1:numLocation)
    if(inputdata[i,j]>0)
      occurrence.obs[i,j] <- 1
numdrydays <- apply(occurrence.obs, 1, mean)
numdrydays <- 1 - numdrydays
precipsummary <- apply(obsdata, 1, mean)
stateproperties <- data.frame(states=viterbistates, precip = precipsummary, numdrydays = numdrydays, month=month)
tapply(precipsummary,viterbistates,describe)
tapply(numdrydays, viterbistates, sum)
addmargins(prop.table(xtabs(~month+states,data=stateproperties),1),2)
##################################################

inputdata$total <- apply(inputdata,1,sum)
hmmoutput$total <- apply(hmmoutput,1,sum)
copulaoutput$total <- apply(copulaoutput,1,sum)
inputdata$source <- 'IMERG'
copulaoutput$source <- 'Wilks'
hmmoutput$source <- 'HMM'
inputdata$seq <- date
hmmoutput$seq <- date
copulaoutput$seq <- date
data <- rbind(inputdata,hmmoutput,copulaoutput)
data$source <- relevel(as.factor(data$source),ref='IMERG')

#data$total[data$total>10000]=10000
data$year <- year

## Lat and Long data
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

## temporal data
ggplot(data[data$year==2018 & data$source!='Wilks',],aes(y=total,x=seq,col=source))+geom_line(lwd=1.1) +
        theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
        axis.text.x = element_text(color = "grey20", size = 18, angle = 0, hjust = .5, vjust = .5, face = "plain"),
        axis.text.y = element_text(color = "grey20", size = 18, angle = 0, hjust = 1, vjust = 0, face = "plain"),
        axis.title.x = element_text(color = "grey20", size = 20, angle = 0, hjust = .5, vjust = 0, face = "plain"),
        axis.title.y = element_text(color = "grey20", size = 20, angle = 90, hjust = .5, vjust = 2, face = "plain"),
        legend.text = element_text(size=15), legend.title = element_text(size=18)) +
        guides(colour = guide_legend(override.aes = list(size=2))) +
        labs(x='Days', y = 'Daily total basin rainfall (mm)', col = 'Source')

ggplot(data[data$year==2018 & data$source!='HMM',],aes(y=total,x=seq,col=source))+geom_line(lwd=1.1)  +
        theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
        axis.text.x = element_text(color = "grey20", size = 18, angle = 0, hjust = .5, vjust = .5, face = "plain"),
        axis.text.y = element_text(color = "grey20", size = 18, angle = 0, hjust = 1, vjust = 0, face = "plain"),
        axis.title.x = element_text(color = "grey20", size = 20, angle = 0, hjust = .5, vjust = 0, face = "plain"),
        axis.title.y = element_text(color = "grey20", size = 20, angle = 90, hjust = .5, vjust = 2, face = "plain"),
        legend.text = element_text(size=15), legend.title = element_text(size=18)) +
        guides(colour = guide_legend(override.aes = list(size=2))) +
        labs(x='Days', y = 'Daily total basin rainfall (mm)', col = 'Source')

#spatial correlations
inputdata <- inputdata[,1:numLocation]
hmmoutput <- hmmoutput[,1:numLocation]
copulaoutput <- copulaoutput[,1:numLocation]

inputprecip <- apply(inputdata, 2, sum)
hmmprecip <- apply(hmmoutput, 2, sum)
hmmgcprecip <- apply(copulaoutput, 2, sum)

basinprecip <- data.frame(inputprecip = inputprecip/numYrs, hmmprecip = hmmprecip/numYrs, hmmgcprecip = hmmgcprecip/numYrs, lat, long)

ggplot(basinprecip,aes(x=long,y=lat,fill=inputprecip)) + geom_tile() + scale_fill_gradientn(colours=rainbow(7)) +
        coord_map() +  theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
        axis.text.x = element_text(color = "grey20", size = 18, angle = 0, hjust = .5, vjust = .5, face = "plain"),
        axis.text.y = element_text(color = "grey20", size = 18, angle = 0, hjust = 1, vjust = 0, face = "plain"),
        axis.title.x = element_text(color = "grey20", size = 20, angle = 0, hjust = .5, vjust = 0, face = "plain"),
        axis.title.y = element_text(color = "grey20", size = 20, angle = 90, hjust = .5, vjust = 2, face = "plain"),
        legend.text = element_text(size=15), legend.title = element_text(size=18), legend.key.size = unit(.8, "cm")) +
        labs(x='Longitude', y = 'Latitude', fill = 'Total (mm)', title = 'Total rainfall from Jul-Sep from IMERG')


ggplot(basinprecip[basinprecip$hmmprecip<500,],aes(x=long,y=lat,fill=hmmprecip)) + geom_tile() +
      scale_fill_gradientn(colours=rainbow(7)) + coord_map() +
      theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
      axis.text.x = element_text(color = "grey20", size = 18, angle = 0, hjust = .5, vjust = .5, face = "plain"),
      axis.text.y = element_text(color = "grey20", size = 18, angle = 0, hjust = 1, vjust = 0, face = "plain"),
      axis.title.x = element_text(color = "grey20", size = 20, angle = 0, hjust = .5, vjust = 0, face = "plain"),
      axis.title.y = element_text(color = "grey20", size = 20, angle = 90, hjust = .5, vjust = 2, face = "plain"),
      legend.text = element_text(size=15), legend.title = element_text(size=18), legend.key.size = unit(.8, "cm")) +
      labs(x='Longitude', y = 'Latitude', fill = 'Total (mm)', title = 'Total rainfall from Jul-Sep from HMM')


ggplot(basinprecip,aes(x=long,y=lat,fill=hmmgcprecip)) + geom_tile() + scale_fill_gradientn(colours=rainbow(7)) +
      labs(fill = 'Total (mm)', x='Longitude', y='Latitude',title = 'Total rainfall from Jul-Sep from Wilks') +
      coord_map() +  theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
      axis.text.x = element_text(color = "grey20", size = 18, angle = 0, hjust = .5, vjust = .5, face = "plain"),
      axis.text.y = element_text(color = "grey20", size = 18, angle = 0, hjust = 1, vjust = 0, face = "plain"),
      axis.title.x = element_text(color = "grey20", size = 20, angle = 0, hjust = .5, vjust = 0, face = "plain"),
      axis.title.y = element_text(color = "grey20", size = 20, angle = 90, hjust = .5, vjust = 2, face = "plain"),
      legend.text = element_text(size=15), legend.title = element_text(size=18), legend.key.size = unit(.8, "cm"))

julcorinput <- upperTriangle(cor(inputdata[month==7,]))
julcorhmm <- upperTriangle(cor(hmmoutput[month==7,]))
julcorcopula <- upperTriangle(cor(copulaoutput[month==7,]))
augcorinput <- upperTriangle(cor(inputdata[month==8,]))
augcorhmm <- upperTriangle(cor(hmmoutput[month==8,]))
augcorcopula <- upperTriangle(cor(copulaoutput[month==8,]))
sepcorinput <- upperTriangle(cor(inputdata[month==9,]))
sepcorhmm <- upperTriangle(cor(hmmoutput[month==9,]))
sepcorcopula <- upperTriangle(cor(copulaoutput[month==9,]))
cordata <- data.frame(cor=c(julcorinput,augcorinput,sepcorinput,julcorhmm,augcorhmm,sepcorhmm, julcorcopula, augcorcopula, sepcorcopula))
cordata$month <- rep(c('July','August','September'),each=74691)
cordata$source <- rep(c('IMERG','HMM', 'Wilks'),each=74691*3)
cordata$month <- relevel(as.factor(cordata$month),ref='July')
cordata$source <- factor(cordata$source, levels = c('IMERG','HMM','Wilks'))

ggplot(cordata,aes(x=month,y=cor,fill=source)) + geom_boxplot() +
      theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
      axis.text.x = element_text(color = "grey20", size = 18, angle = 0, hjust = .5, vjust = .5, face = "plain"),
      axis.text.y = element_text(color = "grey20", size = 18, angle = 0, hjust = 1, vjust = 0, face = "plain"),
      axis.title.x = element_text(color = "grey20", size = 20, angle = 0, hjust = .5, vjust = 0, face = "plain"),
      axis.title.y = element_text(color = "grey20", size = 20, angle = 90, hjust = .5, vjust = 2, face = "plain"),
      legend.text = element_text(size=15), legend.title = element_text(size=18), legend.key.size = unit(.8, "cm")) +
      labs(x='Month', y = 'Correlation between grid point pairs', fill = 'Source')

# Extreme values
#View(inputdata)
inputsummary <- data.frame(month = month ,source=rep('IMERG',dataLen))
avg1 <- apply(inputdata[month==7,1:numLocation],1,mean)
avg2 <- apply(inputdata[month==8,1:numLocation],1,mean)
avg3 <- apply(inputdata[month==9,1:numLocation],1,mean)
inputsummary$total <- c(avg1,avg2,avg3)

max1 <- apply(inputdata[month==7,1:numLocation],1,quantile,1)
max2 <- apply(inputdata[month==8,1:numLocation],1,quantile,1)
max3 <- apply(inputdata[month==9,1:numLocation],1,quantile,1)
inputsummary$extreme <- c(max1,max2,max3)
#View(inputsummary)

hmmsummary <- data.frame(month = month ,source=rep('HMM',dataLen))
avg1 <- apply(hmmoutput[month==7,1:numLocation],1,mean)
avg2 <- apply(hmmoutput[month==8,1:numLocation],1,mean)
avg3 <- apply(hmmoutput[month==9,1:numLocation],1,mean)
hmmsummary$total <- c(avg1,avg2,avg3)

max1 <- apply(hmmoutput[month==7,1:numLocation],1,quantile,1)
max2 <- apply(hmmoutput[month==8,1:numLocation],1,quantile,1)
max3 <- apply(hmmoutput[month==9,1:numLocation],1,quantile,1)
hmmsummary$extreme <- c(max1,max2,max3)


copulasummary <- data.frame(month = month ,source=rep('Wilks',dataLen))
avg1 <- apply(copulaoutput[month==7,1:numLocation],1,mean)
avg2 <- apply(copulaoutput[month==8,1:numLocation],1,mean)
avg3 <- apply(copulaoutput[month==9,1:numLocation],1,mean)
copulasummary$total <- c(avg1,avg2,avg3)

max1 <- apply(copulaoutput[month==7,1:numLocation],1,quantile,1)
max2 <- apply(copulaoutput[month==8,1:numLocation],1,quantile,1)
max3 <- apply(copulaoutput[month==9,1:numLocation],1,quantile,1)
copulasummary$extreme <- c(max1,max2,max3)

#View(outputsummary)



summary <- rbind(inputsummary,hmmsummary, copulasummary)
summary$month <- as.character(summary$month)
summary$month[summary$month=='7'] <- 'July'
summary$month[summary$month=='8'] <- 'August'
summary$month[summary$month=='9'] <- 'September'
summary$month <- factor(summary$month)
summary$month <- relevel(summary$month,ref='July')

ggplot(summary,aes(x=month,y=total,fill=source)) + geom_boxplot() +
      theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
      axis.text.x = element_text(color = "grey20", size = 17, angle = 0, hjust = .5, vjust = .5, face = "plain"),
      axis.text.y = element_text(color = "grey20", size = 17, angle = 0, hjust = 1, vjust = 0, face = "plain"),
      axis.title.x = element_text(color = "grey20", size = 19, angle = 0, hjust = .5, vjust = 0, face = "plain"),
      axis.title.y = element_text(color = "grey20", size = 19, angle = 90, hjust = .5, vjust = 2, face = "plain"),
      legend.text = element_text(size=15), legend.title = element_text(size=18), legend.key.size = unit(.8, "cm")) +
      labs(x='Month', y = 'Daily mean basin precipitation (mm)', fill = 'Source')

ggplot(summary,aes(x=month,y=extreme,fill=source)) + geom_boxplot() +
      theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15),
      axis.text.x = element_text(color = "grey20", size = 17, angle = 0, hjust = .5, vjust = .5, face = "plain"),
      axis.text.y = element_text(color = "grey20", size = 17, angle = 0, hjust = 1, vjust = 0, face = "plain"),
      axis.title.x = element_text(color = "grey20", size = 19, angle = 0, hjust = .5, vjust = 0, face = "plain"),
      axis.title.y = element_text(color = "grey20", size = 19, angle = 90, hjust = .5, vjust = 2, face = "plain"),
      legend.text = element_text(size=15), legend.title = element_text(size=18), legend.key.size = unit(.8, "cm")) +
      labs(x='Month', y = 'Daily maximum precipitation (mm)', fill = 'Source')
