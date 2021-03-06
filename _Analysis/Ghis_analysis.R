library(plyr)
library(ggplot2) 
library(stringr)

# use this vector length later in text 
files = list.files("~/GitHub/Ghis_Multimodal_IOR/For Analysis/EXP_TXT")
len = length(files)

# read in data 
a = ldply(
  .data = list.files(
    path = "~/GitHub/Ghis_Multimodal_IOR/For Analysis/EXP_TXT"
    , pattern = '_data.txt'
    , full.names = T
    , recursive = T
  )
  , .fun = function(x){
    read.table(
      file = x
      , header = TRUE
      , sep = "\t"
    )
  }
)

################################### EYE TRACKING #################################

# order data frame as a function of dates then create reverse ordered list of dates 
a$date = as.Date(sprintf("%i/%i", a$month, a$day), format = "%m/%d")
a= a[order(a$date),]
date_order = as.vector(levels(as.factor(a$date)))
date_order = rev(date_order)

# remember which ids have the same date 
date_id = table(a$date, a$id)

# get rid of practice 
#a = a[a$block != "practice",]

bb = NULL

pnum = c(2:5, 7:len )

# cycle through each participant folder
for (w in pnum) {
  setwd(sprintf("~/GitHub/multimodal_ior/For Analysis/ASC/p%i", w))
  
  saccades = NULL
  blinks = NULL
  eye_trial_data = NULL 
  
  saccades = read.table('saccades.txt',sep='\t')
  names(saccades)[c(2:3,5:8)] = c('start','end', 'x1', 'y1', 'x2', 'y2')
  blinks = read.table('blinks.txt',sep='\t')
  names(blinks)[2:3] = c('start','end')
  
  eye_trial_data = read.table('trials.txt',sep='\t')
  names(eye_trial_data) = c('time','message','id' , 'block','trial_num')
  
  eye_trial_data = eye_trial_data[eye_trial_data$block!='practice',]
  eye_trial_data$block = as.numeric(as.character(eye_trial_data$block))
  
  eye_trial_data = reshape(eye_trial_data,direction='wide',v.names='time',idvar=c('id','block','trial_num'),timevar='message')
  names(eye_trial_data) = str_replace(names(eye_trial_data),'time.','')
  
  if (w>10 & w<16) {
    temp = 16 - w
    b = a[a$date == date_order[temp],]
  } else if (w == 10) {
      b = a[a$id == sprintf("p%i", w),]
  } else if (w == 9) {
      b = a[a$id == sprintf("p0%i", w),]
  } else {
      temp = 16 - w
      b = a[a$date == date_order[temp - 1],] 
  }
  
  b = merge(b,eye_trial_data,all=T)
  
  # when exactly do blinks and saccades start, for all participants
  for(i in 1:nrow(b)){
    temp = min(blinks$start[ (blinks$start>b$trial_start[i]) & (blinks$start<b$trialDone[i]) ])
    b$blink_start[i] = (temp - b$trial_start[i])
    b$blink_after_cue[i] = (temp - (b$trial_start[i] + b$fixation_duration[i]*1000) )

    temp = min(saccades$start[ (saccades$start>b$trial_start[i]) & (saccades$start<b$trialDone[i]) ])
    b$saccade_start[i] = (temp - b$trial_start[i])
    b$saccade_after_cue[i] = (temp - (b$trial_start[i] + b$fixation_duration[i]*1000) )
    
    # where exactly are participants looking 
    b$x1[i] = saccades[saccades$start == temp,]$x1[1]
    b$y1[i] = saccades[saccades$start == temp,]$y1[1]
    b$x2[i] = saccades[saccades$start == temp,]$x2[1]
    b$y2[i] = saccades[saccades$start == temp,]$y2[1]
  }  
  
  b$start_critical_period = b$trial_start + (b$fixation_duration)*1000
  b$end_critical_period = b$start_critical_period + 1300
  
  # critical blinks and saccades for first 10 participants
  if (w < 11) {
    b$critical_blink = FALSE
    b$critical_saccade = FALSE
    for(i in 1:nrow(b)){
      b$critical_blink[i] = sum( ( (blinks$start>b$start_critical_period[i]) & (blinks$start<b$end_critical_period[i]) ) | ( (blinks$end>b$start_critical_period[i]) & (blinks$end<b$end_critical_period[i]) ) ) > 0
      b$critical_saccade[i] = sum( ( (saccades$start>b$start_critical_period[i]) & (saccades$start<b$end_critical_period[i]) ) | ( (saccades$end>b$start_critical_period[i]) & (saccades$end<b$end_critical_period[i]) ) ) > 0
    }
  }
  bb = rbind(bb, b)
}

# when do the saccades occur?
hist(bb$saccade_start, br = 100, main = "Saccade onset relative to trial initiation", xlab = "Time after trial initiation (ms)")
hist(bb$saccade_after_cue, br = 100, main = "Saccade onset relative to cue onset", xlab = "Time after cue onset (ms)")

# when do the blinks occur?
hist(bb$blink_start, br = 100, main = "Blink onset relative to trial initiation", xlab = "Time after trial initiation (ms)")
hist(bb$blink_after_cue, br = 100, main = "Blink onset relative to cue onset", xlab = "Time after cue onset (ms)")

# display monitor paramters 
xr = range(0:1920) # this might be 1920
yr = range(0:1080)

# do rotation on dots
#bb$x1 = xr[2] - bb$x1
#bb$x2 = xr[2] - bb$x2

# DOCUMENTATION says y = 0 correspond to the top of the screen, so FLIP!
bb$y1 = yr[2] - bb$y1
bb$y2 = yr[2] - bb$y2
# WARNING: we get negative numbers for y2 ... 
# SEE mean, median, min  for these 


# where to EMs occur ?
hist(bb$x1, br = 100, xlim = xr)
hist(bb$x2, br = 100, xlim = xr)
hist(bb$y1, br = 100, xlim = yr)
hist(bb$y2, br = 100, xlim = yr)


# plot dots 
ggplot(bb, aes(x1, y1) ) +
  geom_point(alpha = .2) +
  coord_equal(xlim = xr, ylim =yr)

ggplot(bb, aes(x2, y2) ) +
  geom_point(alpha = .2) +
  coord_equal(xlim = xr, ylim =yr)

# where to EMs occur IF in critical interval ?
hist(bb[bb$critical_saccade == TRUE,]$x1, br = 100, xlim = xr)
hist(bb[bb$critical_saccade == TRUE,]$x2, br = 100, xlim = xr)
hist(bb[bb$critical_saccade == TRUE,]$y1, br = 100, xlim = yr)
hist(bb[bb$critical_saccade == TRUE,]$y2, br = 100, xlim = yr)


# plot dots again
ggplot(bb[bb$critical_saccade == TRUE,], aes(x1, y1) ) +
  geom_point(alpha = .2) +
  coord_equal(xlim = xr, ylim =yr)

ggplot(bb[bb$critical_saccade == TRUE,], aes(x2, y2) ) +
  geom_point(alpha = .2) +
  coord_equal(xlim = xr, ylim =yr)

# know where does Mike move his eyes to ..?
# where to EMs occur ?
hist(bb[bb$date == date_order[1],]$x1, br = 100, xlim = xr)
hist(bb[bb$date == date_order[1],]$x2, br = 100, xlim = xr)
hist(bb[bb$date == date_order[1],]$y1, br = 100, xlim = yr)
hist(bb[bb$date == date_order[1],]$y2, br = 100, xlim = yr)


# plot dots 
ggplot(bb[bb$date == date_order[1],], aes(x1, y1) ) +
  geom_point(alpha = .2) +
  coord_equal(xlim = xr, ylim =yr)

ggplot(bb[bb$date == date_order[1],], aes(x2, y2) ) +
  geom_point(alpha = .2) +
  coord_equal(xlim = xr, ylim =yr)

############################## Klein Table #################################

# I want 1 row/subject and 1 column/cueing/cue_modality/target_modality + 1 column for exclusion proportion

d=a

# make e11v2 e11
d$id[d$id == "e11v2"] = "e11"
len = len - 1 

# get rid of e18 - missing False Tactile Visual
d = d[d$id != "e18",]
len = len - 1

# get rid of e15 - missing True Visual Tactile 
d = d[d$id != "e15",]
len = len - 1

# define cued 
d$cued = FALSE
d$cued[d$target_location == "right" & d$cue_location == "right" | d$target_location == "left" & d$cue_location == "left"] = TRUE

# get rid of practice blocks 
d = d[d$block != "practice",]

# define blink or saccade
d$SorB = FALSE
d$SorB[d$blink == TRUE | d$saccade == TRUE] = TRUE 

d$count = TRUE 

# count number of blinks or saccades 
dSum = aggregate(SorB ~ id, data = d, FUN = sum)
dLength = aggregate(count ~ id, data = d, FUN = sum)
dProp = dSum$SorB/dLength$count

# now do the same for critical interval
d$CritSorB = FALSE
d$CritSorB[d$critical_blink == TRUE | d$critical_saccade == TRUE] = TRUE 

dSum2 = aggregate(CritSorB ~ id, data = d, FUN = sum)
dLength2 = aggregate(count ~ id, data = d, FUN = sum)
dProp2 = dSum2$CritSorB/dLength2$count

#Get rid of blink/saccade trials
e = d
e = e[e$SorB == FALSE,]

# LOOK AT IOR WITHOUT BLINKS OR SACCADES 
eAgg = aggregate(target_response_rt ~ cued + cue_modality + target_modality + id, data = e, FUN = mean)

# create data frame of IOR and add other parameters  
kleinTable = data.frame(matrix(eAgg$target_response_rt, nrow = len, byrow = TRUE))

# count how many trials there were in total and then determine what proportion are used in analysis 
usedAgg = aggregate(cue_modality ~ id , d, length)
used_trials = usedAgg$cue_modality * (1 - dProp)

# add number of used trials and proportion to which it corresponds to table 
kleinTable = cbind(round(used_trials), round(kleinTable) )
kleinTable = cbind(round(dProp, digits = 2), kleinTable)

# LOOK AT IOR WITHOUT CRITICAL ... 
f = d
f = f[f$CritSorB == FALSE,]

fAgg = aggregate(target_response_rt ~ cued + cue_modality + target_modality + id, data = f, FUN = mean)

# create data frame of IOR  
kleinTable2 = data.frame(matrix(fAgg$target_response_rt, nrow = len, byrow = TRUE))

# add data frame and parameters to initial data frame 
used_trials2 = usedAgg$cue_modality * (1 - dProp2)

kleinTable = cbind(kleinTable, round(dProp2, digits = 2) ) 
kleinTable = cbind(kleinTable, round(used_trials2) )
kleinTable = cbind(kleinTable, round(kleinTable2) )


# set names for all columns: watch out for orderering, etc. 
names(kleinTable) = c("exclusion proportion - entire trial", "trials used - entire trial", "uncued TT", "cued TT", "uncued VT", "cued VT", "uncued TV", "cued TV", "uncued VV", "cued VV" 
                      ,"exclusion proportion - cue to 300 ms post", "trials used - cue to 300 ms post", "uncued TT", "cued TT", "uncued VT", "cued VT", "uncued TV", "cued TV", "uncued VV", "cued VV")

# check to make sure that names match actual columns 
perms = eAgg[,1:3]

participants = unique(eAgg$id) 

kleinTable = cbind(participants, kleinTable)







