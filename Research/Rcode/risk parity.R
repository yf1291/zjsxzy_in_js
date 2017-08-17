
data1<-read.csv ("assets.csv",head=TRUE)    
a=as.matrix(data1[927:2556,2:7])
date<-data1[927:2556,1]

RiskParity<-function(data1)
{
  m<-ncol(a)
  Cov<-matrix(cov(a,y=NULL, use<-'na.or.complete'),m,m)
  
  TotalTRC<-function(x)
   {
     x<-matrix(c(x,1-sum(x)))
     TRC<-as.vector((Cov%*%x)*x)
     return(sum(outer(TRC,TRC,'-')^2))
  }
  
 sol<-optim(par<-rep(1/m,m-1),TotalTRC)
  w=c(sol$par,1-sum(sol$par))
  return(w)

}

w1<-RiskParity(data1)

re<-a%*%w1
re
plot(date,re)

Cov<-matrix(cov(a,y=NULL, use<-'na.or.complete'),6,6)
(Cov%*%w1)*w1
