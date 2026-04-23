#' obtain a duckdb connection to GO SemanticSQL
#' @note uses ontoProc2 to obtain reference to SQLite reference to GO
#' @export
make_go_con <- function() {
  requireNamespace("ontoProc2")
  gcon = ontoProc2::semsql_connect(ontology="go") # will use BiocFileCache
  gpath = gcon@db_path
  con     <- dbConnect(duckdb())
  sch_id  <- dbQuoteIdentifier(con, "go")
  gpath_l <- dbQuoteLiteral(con, gpath)
  dbExecute(con, "INSTALL sqlite; LOAD sqlite;")
  dbExecute(con, paste("ATTACH", gpath_l, "AS", sch_id, "(TYPE sqlite, READ_ONLY)"))
  con
}

