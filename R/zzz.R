# R/zzz.R

.cache <- NULL

.onLoad <- function(libname, pkgname) {
  .cache <<- new.env(parent = emptyenv())
}

.onUnload <- function(libpath) {
  if (!is.null(.cache) && exists("con", envir = .cache)) {
    if (dbIsValid(.cache$con))
      dbDisconnect(.cache$con, shutdown = TRUE)
  }
  .cache <<- NULL
}
