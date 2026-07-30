
data(faithful)        
str(faithful)          
head(faithful, 10)     
summary(faithful$waiting)


#a
x  <- faithful$waiting
n  <- length(x)
m  <- mean(x)
med<- median(x)
s  <- sd(x)
iq <- IQR(x)
print(list(
  n = n,
  mean = m,
  median = med,
  sd = s,
  IQR = iq
))


#b
h <- 3.5 * sd(x) * n^(-1/3)
anchor <- floor(min(x))
brks <- seq(anchor, max(x) + h, by = h)

hist(x, breaks = brks, right = FALSE,
     main = sprintf("Histogram (Scott) — h=%.2f", h),
     xlab = "waiting (minutes)")


