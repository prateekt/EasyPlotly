import EasyPlotly as EP
import YayROCS as YP
import pandas as pd
import scipy.stats as sc
import numpy as np
import sklearn.metrics

def manhattanPlot(df,posColName,pvalueColName,title=None,height=None):

	#plot
	runningPos=0
	cnt=0
	h = [None]*22
	for chrs in range(1,23):
		chrName = 'chr'+str(chrs)
		chrDF = df[df.Chr==chrName]
		maxPos = np.max(chrDF[posColName].values)
		ptsX = chrDF[posColName].values + runningPos
		ptsY = -1*np.log10(chrDF[pvalueColName].values)
		h[chrs-1] = EP.scattergl(ptsX,ptsY,name=chrName,xlabel='Chromosome',ylabel='-log10(p)',title=title,markerSize=3)
		cnt = cnt + len(chrDF)
		runningPos = runningPos+maxPos
	EP.plotAll(h,panels=np.ones((len(h),),dtype=int).tolist(),numCols=1,showLegend=True,height=height)

def chrRollingMedian(chrPosDF,chrValDF,rollwinsize,ylabel=None,title=None,withhold=False,xlim=None,ylim=None):

	#plot
	x=chrPosDF.values
	y=chrValDF.rolling(rollwinsize).median()
	linePlot = EP.line(x=x,y=y,title=title,xlabel='Chr Position',ylabel=ylabel,ylim=ylim)
	if(withhold):
		return linePlot
	else:
		EP.plotAll([linePlot])

def chrCount(boolVals,chrDF,title=None,withhold=False):

	#extract unique chr vals
	uniqVals = chrDF.unique()

	#make chromosome-level counts
	counts = np.zeros((len(uniqVals),))
	cnt=0
	for u in uniqVals:
		counts[cnt] = np.sum(boolVals[chrDF==u])
		cnt = cnt + 1
	
	#plot
	barPlot = EP.bar(counts,x=uniqVals,title=title,xlabel='Chromosome',ylabel='Count')
	if(withhold):
		return barPlot
	else:
		EP.plotAll([barPlot])

def chrDistr(data,chrDF,distrName,title=None,withhold=False):

	#extract unique chr vals
	uniqVals = chrDF.unique()

	#make chromosome-level counts
	pVals = np.zeros((len(uniqVals),))
	cnt=0
	for u in uniqVals:
		chrDat = data[chrDF==u]
		res= sc.kstest(chrDat,distrName)
		pVals[cnt]  = res[1]
		cnt = cnt + 1
	
	#plot
	barPlot = EP.bar(pVals,x=uniqVals,title=title,xlabel='Chromosome',ylabel='P-value (Null: Data is '+distrName+')',ylim=[0,1])
	if(withhold):
		return barPlot
	else:
		EP.plotAll([barPlot])

def chrCountDistr(boolVals,chrDF,title=None,withhold=False):
	#bool vals = N pos x M replicates

	#extract unique chr vals
	uniqVals = chrDF.unique()

	#make chromosome-level counts
	means = np.zeros((len(uniqVals),))
	stds = np.zeros((len(uniqVals),))
	cnt=0
	for u in uniqVals:
		reps = boolVals[chrDF==u]
		sums = np.sum(reps,axis=0)
		means[cnt] = np.mean(sums)
		stds[cnt] = np.std(sums)
		cnt = cnt + 1
	
	#plot
	barPlot = EP.bar(y=means,x=uniqVals,error_y=stds,title=title,xlabel='Chromosome',ylabel='Count')
	if(withhold):
		return barPlot
	else:
		EP.plotAll([barPlot])

def chrHist(df,chrCol,colName,minBin=None,maxBin=None,binSize=None,title=None,xlabel=None,ylabel=None,histnorm=None,x_dTick=None,y_dTick=None,outFile=None):
	
	#labels
	if(xlabel==None):
		xlabel = colName
	if(ylabel==None):
		ylabel = 'Count'

	#chrs
	chrsList = list()
	for i in range(1,23):
		chrsList.append('chr'+str(i))
	chrsList.append('chrX')
	chrsList.append('chrY')

	#extract unique chr values
	uniqVals = df.iloc[:,chrCol].unique()

	#make chromosome level hists
	hists = list()
	for uChr in chrsList:
		if(uChr in uniqVals):
			data = df[colName][df.iloc[:,chrCol]==uChr]
			EPHist = EP.hist(data,title=uChr,xlabel=xlabel,minBin=minBin,maxBin=maxBin,binSize=binSize,ylabel=ylabel,color='#1ad1ff',histnorm=histnorm,x_dTick=x_dTick,y_dTick=y_dTick)
			hists.append(EPHist)
	
	#make plot
	EP.plotAll(hists,numCols=5,title=title,chrPacked=True,outFile=outFile)

def chrQQ(df,chrCol,colName,sparams=(),dist='norm',title=None,outFile=None):

	#chrs
	chrsList = list()
	for i in range(1,23):
		chrsList.append('chr'+str(i))
	chrsList.append('chrX')
	chrsList.append('chrY')

	#extract unique chr values
	uniqVals = df.iloc[:,chrCol].unique()

	#make chromosome level qq-plots
	plots = list()
	panels = list()
	panelIndex=1
	for uChr in chrsList:
		if(uChr in uniqVals):
			data = df[colName][df.iloc[:,chrCol]==uChr].values
			qq = qqplot(data,sparams=sparams,dist=dist,title=uChr)
			plots.append(qq[0])
			plots.append(qq[1])
			panels.append(panelIndex)
			panels.append(panelIndex)
			panelIndex = panelIndex + 1	

	#make plot
	EP.plotAll(plots,panels=panels,numCols=5,height=1000,title=title,chrPacked=True,outFile=outFile)

def qqplot(data,sparams=(),dist='norm',title=None,name=None,markerColor='blue',lineColor='red'):
	qq = sc.probplot(data,dist=dist,sparams=sparams)
	x=np.array([qq[0][0][0],qq[0][0][-1]])
	ptsScatter = EP.scattergl(x=qq[0][0],y=qq[0][1],title=title,xlabel='Expected',ylabel='Observed',markerSize=5,markerColor=markerColor,name=name)
	if(name==None):
		name = ''	
	linePlot = EP.line(x=x,y=qq[1][1] + qq[1][0]*x,width=3,color=lineColor,title=title,name=(name + ' (distribution='+dist+')'))
	return (ptsScatter,linePlot)

def roc(preds,gt,panel=1,names=None,title=None,xScale=None,yScale=None):
	#preds = N-ROC x L
	#gt = (L,)

	#structure
	plots = list()
	panels = list()

	#add chance curve
	p = EP.line(x=np.arange(0.0,1.01,0.01),y=np.arange(0.0,1.01,0.01),width=2,name='Chance Curve',color='black',xlabel='False Positive Rate',ylabel='True Positive Rate',title=title,xlim=[0,1.01],ylim=[0,1.01],xScale=xScale,yScale=yScale,x_dTick=0.1,y_dTick=0.1)
	plots.append(p)
	panels.append(panel)

	#for each predictor compute roc curve
	for i in range(0,preds.shape[0]):
		fpr,tpr = YP.roc(preds[i,:],gt)
#		fpr,tpr,_ = sklearn.metrics.roc_curve(gt,preds[:,i])
		AUC = np.round(YP.auc(fpr,tpr),3)
		name='AUC='+str(AUC)
		if(names!=None):
			name = names[i] + '('+'AUC='+str(AUC)+')'
		p = EP.line(x=fpr,y=tpr,width=2,name=name,xlim=[0,1.0],ylim=[0,1.01],xScale=xScale,yScale=yScale,x_dTick=0.1,y_dTick=0.1)
		plots.append(p)
		panels.append(panel)

	#return
	return (plots,panels)

def ecdf(data,minBin,maxBin,binSize,title=None,xlabel=None,ylabel=None,norm=False,name=None,xScale=None,yScale=None,x_dTick=None,y_dTick=None):
	counts, bin_edges = np.histogram(data, bins=np.arange(minBin,maxBin+binSize,binSize))
	countsSum = np.sum(counts)
	counts = counts / countsSum
	cdf = np.cumsum(counts)
	if(not norm):
		if(ylabel is None):
			ylabel = 'Cum Freq'
		cdfLine = EP.line(x=bin_edges[1:],y=countsSum*cdf,title=title,xlabel=xlabel,ylabel=ylabel,xlim=[minBin,maxBin+binSize],name=name,xScale=xScale,yScale=yScale,x_dTick=x_dTick,y_dTick=y_dTick)
	else:
		if(ylabel is None):
			ylabel = 'CDF'
		cdfLine = EP.line(x=bin_edges[1:],y=cdf,title=title,xlabel=xlabel,ylabel=ylabel,xlim=[minBin,maxBin+binSize],ylim=[0,1.0],name=name,xScale=xScale,yScale=yScale,x_dTick=x_dTick,y_dTick=y_dTick)
	return cdfLine

def rcdf(data,minBin,maxBin,binSize,title=None,xlabel=None,ylabel=None,norm=False,name=None,xScale=None,yScale=None,x_dTick=None,y_dTick=None):
	counts, bin_edges = np.histogram(data, bins=np.arange(minBin,maxBin+binSize,binSize))
	countsSum = np.sum(counts)
	counts = counts / countsSum
	cdf = np.cumsum(counts)
	if(not norm):
		if(ylabel is None):
			ylabel = 'Cum Freq'
		cdfLine = EP.line(x=bin_edges[1:],y=np.round(countsSum*(1.0-cdf),5),title=title,xlabel=xlabel,ylabel=ylabel,xlim=[minBin,maxBin+binSize],name=name,xScale=xScale,yScale=yScale,x_dTick=x_dTick,y_dTick=y_dTick)
	else:
		if(ylabel is None):
			ylabel = 'CDF'
		cdfLine = EP.line(x=bin_edges[1:],y=np.round(1.0-cdf,5),title=title,xlabel=xlabel,ylabel=ylabel,xlim=[minBin,maxBin+binSize],ylim=[0,1.0],name=name,xScale=xScale,yScale=yScale,x_dTick=x_dTick,y_dTick=y_dTick)
	return cdfLine

def corrPlot(x,y,xlabel=None,ylabel=None,title=None,name=None,xScale=None,yScale=None,x_dTick=None,y_dTick=None,xlim=None,ylim=None):
	corrVal = pd.core.nanops.nancorr(x,y)
	if(name is None):
		name = 'corr='+str(np.round(corrVal,3))
	else:
		name = name + ' ('+'corr='+str(np.round(corrVal,3))+')'
	scatterPlot = EP.scattergl(x=x,y=y,xlabel=xlabel,ylabel=ylabel,title=title,name=name,xScale=xScale,yScale=yScale,x_dTick=x_dTick,y_dTick=y_dTick,xlim=xlim,ylim=ylim)
	return scatterPlot