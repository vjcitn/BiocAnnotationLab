
# tests/testthat/helper-connection.R

#' Ensure a live GO connection exists or skip the calling test
#'
#' Skips if ontoProc2 is not installed or if the GO database cannot
#' be retrieved.  Tests use this as a guard at the top of any
#' expectation block that requires a live connection.
live_con <- function() {
  testthat::skip_if_not_installed("ontoProc2")

  if (!ontoProc2ui::go_connection_active()) {
    tryCatch(
      suppressMessages(ontoProc2ui::make_go_con()),
      error = function(e)
        testthat::skip(paste("Could not establish GO connection:", e$message))
    )
  }

  invisible(NULL)
}

# bottom of tests/testthat/helper-connection.R
withr::defer(
  suppressMessages(ontoProc2ui::disconnect_go()),
  envir = testthat::teardown_env()
)

