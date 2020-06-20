library(DescTools)
library(gdata)
train <- read.table('D:/precip/trainingdata')
test <- read.table('D:/precip/testingdata')
sim2state <- read.table('d:/precip/sim_outputs/s2e3_DG')
sim3state <- read.table('d:/precip/sim_outputs/s3e3_DG')
sim4state <- read.table('d:/precip/sim_outputs/s4e3_DG')
sim5state <- read.table('d:/precip/sim_outputs/s5e3_DG')
sim6state <- read.table('d:/precip/sim_outputs/s6e3_DG')

train.cor <- upperTriangle(cor(train))
test.cor <- upperTriangle(cor(test))

sim2.cor <- upperTriangle(cor(sim2state))
sim3.cor <- upperTriangle(cor(sim3state))
sim4.cor <- upperTriangle(cor(sim4state))
sim5.cor <- upperTriangle(cor(sim5state))
sim6.cor <- upperTriangle(cor(sim6state))

mad.train.2 <- mean(abs(train.cor-sim2.cor))
mad.train.3 <- mean(abs(train.cor-sim3.cor))
mad.train.4 <- mean(abs(train.cor-sim4.cor))
mad.train.5 <- mean(abs(train.cor-sim5.cor))
mad.train.6 <- mean(abs(train.cor-sim6.cor))

mad.test.2 <- mean(abs(test.cor-sim2.cor))
mad.test.3 <- mean(abs(test.cor-sim3.cor))
mad.test.4 <- mean(abs(test.cor-sim4.cor))
mad.test.5 <- mean(abs(test.cor-sim5.cor))
mad.test.6 <- mean(abs(test.cor-sim6.cor))

mad.train.2
mad.train.3
mad.train.4
mad.train.5
mad.train.6

mad.test.2
mad.test.3
mad.test.4
mad.test.5
mad.test.6

library(ggplot2)
library(forecast)
library(lubridate)
library(gdata)
library(tidyr)
library(psych)
theme_set(theme_bw())
library(sf)
setwd("D:/precip/")
inputdata <- read.table('PotomacJulSep')
#View(inputdata)
hmmoutput <- read.table('sim_potomac_data_julsep')
copulaoutput <- read.table('gammacopula',header = T)
#View(outputdata)
#outputdata <- outputdata[,-388]

date <- rep(seq(ymd('2001-07-01'),ymd('2001-09-30'),by='days'),18)
month <- month(date)
day <- day(date)
year <- rep(2001:2018,each=92)
date <- make_date(year,month, day)
date <- substr(date,1,7)
head(date)

#inputdata <- cbind(inputdata,date)
#copulaoutput <- cbind(copulaoutput,date)
month <- rep(c(7,8,9),18)

tmp1 <- aggregate(inputdata, list(date), sum)
tmp2 <- aggregate(copulaoutput,list(date),sum)
tmp1 <- tmp1[,-1]
tmp2 <- tmp2[,-1]
tmp1 <- aggregate(tmp1,list(month),mean)
tmp2 <- aggregate(tmp2,list(month),mean)
input.monthly.mean <- tmp1[,-1]
copula.monthly.mean <- tmp2[,-1]
tmp2 <- c(t(as.matrix(copula.monthly.mean)))
tmp1 <- c(t(as.matrix(input.monthly.mean)))


tmp3 <- aggregate(inputdata,list(date),function(x)mean(x==0))
tmp4 <- aggregate(copulaoutput,list(date),function(x)mean(x==0))
tmp3 <- tmp3[,-1]
tmp4 <- tmp4[,-1]
tmp3 <- aggregate(tmp3,list(month),mean)
tmp4 <- aggregate(tmp4,list(month),mean)
input.monthly.prop <- tmp3[,-1]
copula.monthly.prop <- tmp4[,-1]
tmp4 <- c(t(as.matrix(copula.monthly.prop)))
tmp3 <- c(t(as.matrix(input.monthly.prop)))

summaryplot <- data.frame(month = rep(month.abb[7:9],each=387), mean.obs = tmp1, mean.sim=tmp2, prop.obs = tmp3, prop.sim=tmp4)
summaryplot$month <- relevel(summaryplot$month, ref = 'Jul')
xrng <- range(summaryplot$mean.obs)
yrng <- range(summaryplot$mean.sim)
ggplot(summaryplot,aes(x=mean.obs,y=mean.sim,col=month)) + geom_point() + geom_abline() +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15), 
        axis.text.x = element_text(color = "grey20", size = 12, angle = 0, hjust = .5, vjust = .5, face = "plain"),
        axis.text.y = element_text(color = "grey20", size = 12, angle = 0, hjust = 1, vjust = 0, face = "plain"),  
        axis.title.x = element_text(color = "grey20", size = 17, angle = 0, hjust = .5, vjust = 0, face = "plain"),
        axis.title.y = element_text(color = "grey20", size = 17, angle = 90, hjust = .5, vjust = 2, face = "plain"),
        legend.text = element_text(size=12), legend.title = element_text(size=15)) +
  guides(colour = guide_legend(override.aes = list(size=3))) +
  labs(x='IMERG precipitation (mm)', y = 'Synthetic precipitation from HMM-GC (mm)', col = 'Month') +
  annotate(geom = "text", x = xrng[1], y = yrng[2], 
    label = 'RMSE = 6.32 mm', hjust = 0, vjust = 1, size = 5)

xrng <- range(summaryplot$prop.obs)
yrng <- range(summaryplot$prop.sim)
ggplot(summaryplot,aes(x=prop.obs,y=prop.sim,col=month)) + geom_point() + geom_abline()+
  theme(panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5, size = 15), 
        axis.text.x = element_text(color = "grey20", size = 12, angle = 0, hjust = .5, vjust = .5, face = "plain"),
        axis.text.y = element_text(color = "grey20", size = 12, angle = 0, hjust = 1, vjust = 0, face = "plain"),  
        axis.title.x = element_text(color = "grey20", size = 17, angle = 0, hjust = .5, vjust = 0, face = "plain"),
        axis.title.y = element_text(color = "grey20", size = 17, angle = 90, hjust = .5, vjust = 2, face = "plain"),
        legend.text = element_text(size=12), legend.title = element_text(size=15)) +
  guides(colour = guide_legend(override.aes = list(size=3))) +
  labs(x='Proportion of dry days based on IMERG', y = 'Proportion of dry days based on HMM', col = 'Month') +
  annotate(geom = "text", x = xrng[1], y = yrng[2], 
           label = 'RMSE = 0.06', hjust = 0, vjust = 1, size = 5)


RMSE(summaryplot$mean.sim,summaryplot$mean.obs)
RMSE(summaryplot$prop.sim,summaryplot$prop.obs)

summaryplot2 <- gather(summaryplot[,1:3],source,mean,mean.obs:mean.sim )
summaryplot3 <- gather(summaryplot[,c(1,4,5)],source,prop,prop.obs:prop.sim )

ggplot(summaryplot2, aes(x=month, y=mean, fill=source)) + geom_boxplot()
ggplot(summaryplot3, aes(x=month, y=prop, fill=source)) + geom_boxplot()
