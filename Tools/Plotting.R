install.packages("https://cran.r-project.org/src/contrib/Archive/patchwork/patchwork_1.1.0.tar.gz", repos = NULL, type = "source", dependencies = TRUE)

install.packages("broom")
install.packages("dplyr")
install.packages("labelled")
install.packages("tidyr")


install.packages("https://cran.r-project.org/src/contrib/Archive/broom.helpers/broom.helpers_1.4.0.tar.gz", repos = NULL, type = "source", dependencies = TRUE)

install.packages("https://cran.r-project.org/src/contrib/Archive/ggstats/ggstats_0.5.0.tar.gz", repos = NULL, type = "source", dependencies = TRUE)

library(datasets)
data(iris)


#install.packages("GGally")

library(GGally)
ggpairs(iris, mapping=ggplot2::aes(colour = Species))