# theme_house.R - Figure house style for ggplot2.
#   source("theme_house.R"); theme_set(theme_house("paper"))
# Conventions: see ../SKILL.md and ../references/palettes.md

library(ggplot2)

# ── Colours ────────────────────────────────────────────────────────────────────
pal_pair      <- c("#0000FF", "#FF0000")          # baseline-like vs changed-like (name it to your groups)
pal_accent    <- c(accent = "#0E7C7B", control = "#9AA0A6")
shapes_ordered <- c(16, 17, 15)                     # ● ▲ ■ for a second factor
okabe_ito     <- c("#0072B2", "#E69F00", "#009E73", "#D55E00",
                   "#CC79A7", "#56B4E9", "#F0E442", "#000000")
ref_grey      <- "grey50"

# Replicate tones: n shades of one hue, dark -> light
rep_tones <- function(hue = c("Blues", "Reds", "Greens"), n) {
  hue <- match.arg(hue)
  scales::brewer_pal(palette = hue)(9)[round(seq(9, 4, length.out = n))]
}

# ── Theme ──────────────────────────────────────────────────────────────────────
# Sizes are at final printed/projected size.
theme_house <- function(target = c("paper", "thesis", "slide")) {
  target <- match.arg(target)
  base <- c(paper = 8, thesis = 10, slide = 14)[[target]]
  theme_classic(base_size = base, base_family = "sans") +
    theme(
      plot.title       = element_text(face = "bold", size = rel(1.1), hjust = 0.5),
      strip.background = element_blank(),
      strip.text       = element_text(face = "bold"),
      axis.text        = element_text(colour = "black"),
      axis.line        = element_line(colour = "black", linewidth = 0.4),
      axis.ticks       = element_line(colour = "black", linewidth = 0.4),
      legend.position  = "bottom",
      legend.title     = element_text(size = rel(0.9)),
      legend.key.size  = unit(0.9, "lines"),
      plot.background  = element_rect(fill = "white", colour = NA),
      panel.background = element_rect(fill = "white", colour = NA)
    )
}

# ── Marks ──────────────────────────────────────────────────────────────────────
# mean ± 1 SD without Hmisc
mean_sd1 <- function(y) data.frame(y = mean(y), ymin = mean(y) - sd(y), ymax = mean(y) + sd(y))

# Scatter-dot + black mean ± SD (Prism "scatter dot plot, mean with SD").
geom_dot_mean_sd <- function(width = 0.12, size = 2.2) {
  list(
    geom_jitter(width = width, height = 0, size = size, shape = 21,
                colour = "black", stroke = 0.3),
    stat_summary(fun = mean, geom = "crossbar", width = 0.35, linewidth = 0.4,
                 colour = "black"),
    stat_summary(fun.data = mean_sd1, geom = "errorbar", width = 0.18,
                 linewidth = 0.5, colour = "black")
  )
}

# Exact-p label: "p = 0.009", "p < 0.001"
fmt_p <- function(p) ifelse(p < 0.001, "p < 0.001",
                     ifelse(p < 0.01, sprintf("p = %.2g", p), sprintf("p = %.3f", p)))

# Significance bracket for SIGNIFICANT comparisons only (never draw 'ns').
sig_bracket <- function(x1, x2, y, p, tip = 0.02, size = 2.6) {
  if (p >= 0.05) return(NULL)
  list(
    annotate("segment", x = c(x1, x1, x2), xend = c(x1, x2, x2),
             y = c(y * (1 - tip), y, y), yend = c(y, y, y * (1 - tip)), linewidth = 0.4),
    annotate("text", x = (x1 + x2) / 2, y = y, label = fmt_p(p), vjust = -0.5, size = size)
  )
}

# Dotted reference line with direct label (control, baseline, threshold ...).
ref_line <- function(y, label = NULL, x = Inf) {
  list(
    geom_hline(yintercept = y, linetype = "dotted", colour = ref_grey, linewidth = 0.4),
    if (!is.null(label)) annotate("text", x = x, y = y, label = label, hjust = 1.02,
                                  vjust = -0.4, size = 2.5, colour = ref_grey)
  )
}

# Plain-number log10 axis (0.5, 2, 10, 50 ...) as used for dose-response.
scale_x_log_plain <- function(breaks) scale_x_log10(breaks = breaks, labels = format(breaks, trim = TRUE, drop0trailing = TRUE))

# Export: PDF (vector) + 300 dpi PNG, same stem. Sizes in mm.
save_fig <- function(plot, stem, w_mm = 85, h_mm = 70, dir = "output/figures") {
  dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  ggsave(file.path(dir, paste0(stem, ".pdf")), plot, width = w_mm, height = h_mm, units = "mm")
  ggsave(file.path(dir, paste0(stem, ".png")), plot, width = w_mm, height = h_mm, units = "mm",
         dpi = 300, bg = "white")
  invisible(file.path(dir, paste0(stem, ".png")))
}
