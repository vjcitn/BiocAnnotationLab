#' Self-description
#' @examples
#' pinfo()
#' @export
pinfo = function() {
  packageName()
  c(name=packageName(), version=packageVersion("BiocAnnotationLab"))
}

