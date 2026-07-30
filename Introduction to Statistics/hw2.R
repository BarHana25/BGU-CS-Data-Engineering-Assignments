#-----שאלה 3------
#פונקציה למציאת הרצף הארוך ביותר
max_streak <- function(x) {
  max(rle(x)$lengths)
}

#סימולציה של 1000 רצפים של 100 הטלות
simulate_streaks <- function(num_sims = 1000, n = 100) {
  streaks <- numeric(num_sims)
  
  for (i in 1:num_sims) {
    tosses <- sample(c(0,1), size = n, replace = TRUE)
    streaks[i] <- max_streak(tosses)
  }
  
  return(mean(streaks))
}

#הרצת הסימולציה עבור כמה ערכים של n 
ns <- c(50, 100, 200, 500, 1000)
avg_streaks <- numeric(length(ns))

for (i in seq_along(ns)) {
  avg_streaks[i] <- simulate_streaks(num_sims = 1000, n = ns[i])
}

#יצירת טבלת נתונים 
results <- data.frame(
  n = ns,
  average_max_streak = avg_streaks
)

print(results)

#גרף להבנת הנתונים 
plot(ns, avg_streaks, type = "b", pch = 19,
     xlab = "Number of tosses (n)",
     ylab = "Average maximum streak",
     main = "Effect of sample size on maximum streak length")

#-------שאלה 4-------

#יצירת דגימה ברנולית גדולה
set.seed(123)  
n <- 1000      
p <- 0.3     

# סימולציה של n תצפיות
x <- rbinom(n, size = 1, prob = p)

#ממוצע מצטבר
running_mean <- cumsum(x) / (1:n)

#יצירת גרף
plot(1:n, running_mean, type = "l", lwd = 2,
     xlab = "Sample Size (n)",
     ylab = "Sample Mean",
     main = "Demonstrating the Law of Large Numbers (Bernoulli p = 0.3)")
# קו הממוצע התאורטי
abline(h = p, col = "red", lwd = 2) 

#------שאלה 5 ------
set.seed(123)

p <- 0.3        
n <- 100          
num_sims <- 5000  

phat_vals <- numeric(num_sims)

for (i in 1:num_sims) {
  x <- rbinom(n, size = 1, prob = p)
  phat_vals[i] <- mean(x)
}

# היסטוגרמה
hist(phat_vals, breaks = 30,
     main = "Histogram of p-hat (Bernoulli p = 0.3)",
     xlab = "p-hat",
     col = "lightblue",
     border = "black")


