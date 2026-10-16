library(deaR)
raw <- data.frame(DMU=paste0("D",1:6),x1=c(4,5,7,6,9,8),x2=c(7,5,4,8,7,10),y1=c(8,7,9,8,10,9),y2=c(5,7,6,9,8,11))
d <- make_deadata(raw, dmus=1, inputs=2:3, outputs=4:5)
fit <- model_basic(d, orientation="oo", rts="vrs", maxslack=TRUE, compute_target=TRUE)
write.csv(as.data.frame(efficiencies(fit)), "dear_fixture_eff.csv", row.names=FALSE)
write.csv(as.data.frame(lambdas(fit)), "dear_fixture_lambda.csv", row.names=FALSE)
# deaR object accessors/conventions should be inspected for the installed version before mapping slack/target components.
# The frozen native verification record in this archive is the evidence used by the manuscript.
cat("deaR package version:", as.character(packageVersion("deaR")), "\n")
