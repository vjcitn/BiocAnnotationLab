#' retrieve table of entailed edges in GO (derivable from OWL base axioms)
#' @import DBI dbplyr duckdb
#' @rawNamespace import(dplyr, except=c(sql, ident))
#' @param con live duckdb connection 
#' @param schema character name, defaults to "go"
#' @export
go_entailed_edges <- function(con, schema = "go")
  suppressMessages(tbl(con, DBI::Id(schema = schema, table = "entailed_edge")))

#' retrieve table of statements in GO
#' @param con live duckdb connection 
#' @param schema character name, defaults to "go"
#' @export
go_statements <- function(con, schema = "go")
  suppressMessages(tbl(con, DBI::Id(schema = schema, table = "statements")))
