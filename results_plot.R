library(ggplot2)

df <- data.frame(guesses=as.character(c(2,3,4,5,6,
                                        1,2,3,4,5,6,7,
                                        2,3,4,5,6,7,8,9,
                                        1,2,3,4,5,6,7,8)),
                 words=c(64,784,1178,266,23,
                         1,84,812,1167,236,14,1,
                         117,862,927,320,65,18,5,1,
                         1,146,895,977,244,36,13,3),
                 strat=c(rep('valid',5), 
                         rep('known-good',7), 
                         rep('valid', 8), 
                         rep('known-good',8)),
                 hard=c(rep('normal',5), 
                         rep('normal',7), 
                         rep('hard', 8), 
                         rep('hard',8)))
df$strat = factor(df$strat, c('valid', 'known-good'))
df$hard = factor(df$hard, c('normal', 'hard'))
df$total <- 0

for (strat in levels(df$strat)) {
  for (hard in levels(df$hard)) {
    df[df$strat==strat & df$hard==hard,]$total <- sum(df[df$strat==strat & df$hard==hard,]$words)
  }
}

df$pct <- df$words/df$total

p<-ggplot(df, aes(x=guesses, y=pct, fill=guesses)) +
  geom_col() +
  scale_y_continuous(labels = scales::percent_format()) +
  scale_fill_brewer(palette = "Set1") +
  guides(fill = guide_legend(nrow = 1)) +
  theme_bw() +
  geom_vline(xintercept=6.5) +
  theme(legend.position = 'none') +
  labs(y="", x="Num. of guesses") +
  facet_grid(hard~strat)
p


ggsave('results.png', p, width=6, height=5, dpi=200)
