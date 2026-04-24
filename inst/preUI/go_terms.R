#' produce table with terms as a focus
#' @importFrom dplyr filter select mutate left_join
#' @examples
#' con = make_go_con()
#' go_labels(con)
#' @export
go_terms <- function(con, schema = "go", include_deprecated = FALSE) {
  st <- go_statements(con, schema)
  
  labels <- st |> filter(predicate == "rdfs:label") |>
    select(id = subject, label = value)
  ns     <- st |> filter(predicate == "oio:hasOBONamespace") |>
    select(id = subject, ontology = value)
  defs   <- st |> filter(predicate == "IAO:0000115") |>
    select(id = subject, definition = value)
  dep    <- st |> filter(predicate == "owl:deprecated", value == "true") |>
    select(id = subject) |> mutate(deprecated = TRUE)

  out <- labels |>
    filter(id %like% "GO:%") |>
    left_join(ns,  by = "id") |>
    left_join(defs, by = "id") |>
    left_join(dep,  by = "id") |>
    mutate(deprecated = coalesce(deprecated, FALSE))

  if (!include_deprecated) out <- out |> filter(!deprecated)
  out
}
