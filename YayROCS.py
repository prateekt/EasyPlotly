import numpy as np

#input = predictor vector, ground truth vector
def roc(pred,gt):

	#make sure pred /gt are correct shape
	if((pred.ndim==2) and (pred.shape[1] > pred.shape[0])):
		pred = pred.T
	elif((pred.ndim==1)):
		pred = pred.reshape(-1,1)
	if((gt.ndim==2) and (gt.shape[1] > gt.shape[0])):
		gt = gt.T
	elif((gt.ndim==1)):
		gp = gp.rehsape(-1,1)

	#make results table
	results = np.concatenate([pred,gt],axis=1)

	#compute step sizes
	A = results.shape[0]
	numPos = np.sum(results[:,1])
	numNeg = A - numPos
	stepX = 1.0/numNeg
	stepY = 1.0/numPos
	currentX= 0.0
	currentY= 0.0

	#sort results
	ind = np.lexsort((results[:,1],-1*results[:,0]))
	results = results[ind]

	#roc compute
	FPR = np.zeros((A+1,))
	TPR = np.zeros((A+1,))
	cnt=1
	for i in range(0,A):
		if(results[i,1]==1):
			currentY = currentY + stepY
			FPR[cnt] = currentX
			TPR[cnt] = currentY
		else:
			currentX = currentX + stepX
			FPR[cnt] = currentX
			TPR[cnt] = currentY
		cnt = cnt + 1

	#resize and return
	cnt = cnt - 1
	TPR = TPR[0:cnt]
	FPR = FPR[0:cnt]
	return(FPR,TPR)

#input 1 roc (X,Y)
def auc(X,Y):

	#align to reference binning
	ref_binning = np.arange(0,1.1,0.01)
	binInd = 0
	AUC = 0
	for i in range(0,len(ref_binning)):
		#find appropriate bin to draw
		while((binInd < (len(X)-1)) and (ref_binning[i] > X[binInd])):
			binInd = binInd + 1
		AUC = AUC + Y[binInd]
	AUC = AUC / len(ref_binning)
	return AUC