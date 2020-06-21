Team x Project of the CyberTraining program at UMBC in 2020 (http://cybertraining.umbc.edu/)

**Title**: 

**Team members**: 

**Mentors**: 

**Abstract**: 

**Structures of implementation**:

**Instructions on how to run the code**

The following ancillary files should be in the same folder as the R scripts:  
**viterbi_potomac_julsep4state** - the Viterbi output from MVNHMM  
**params.json** - Parameter file extracted from MVNHMM output  
**PotomacJulSep** - The historical data  
**latlong** - File with latitude and longitude data  

**01 - gammacorrels.R**  
Set values for line numbers 7-21, for the User Inputs section. Explanation for each variable is in the file.
This file reads in the historical data, the model fit from MVNHMM, and the Viterbi sequence from MVNHMM and generates a synthetic dataset using a Gaussian copula. Size of synthetic data can be set.
the output file is gammacopula and saves in the same directory.

**02 - hmmgammacopulaoutput.R**  
Set values for line numbers 10-24, for the User Inputs section. Explanation for each variable is in the file.
This file reads in the same data as the previous file, as well as the synthetic data and generates the Viterbi states plot, the time series plots (for 2018), spatial correlation plot, daily basin maxima
and mean plot, and the spatial plots for the basin precipitation. no ggsave function is built in so once the plots are generated they need to be saved manually.  
**Note** - feature can be added to ggsave() the plots to a fixed resolution.

**02 - hmmwilksoutput.R**  
Functionally identical to 02 - hmmgammacopulaoutput.R but instead of comparing HMM and HMM-GC it compares HMM and Wilks to produce identical plots.

**03 - rmse and scatterplots.R**  
Set values for line numbers 7-21, for the User Inputs section. Explanation of variabes should be the same as files 01 and 02.
This generates the RMSE values for proportion of dry days and mean rainfall. Also the corresponding scatterplots for historical data vs. HMM-GC.  
**Note** - in the tech report, we use 100 years of synthetic data vs 18 years of observed data. That required some hardcoding on the fly.

**99 - functionDefns.R**  
Contains functions used by the other files. Sourced by most of the R files above.
