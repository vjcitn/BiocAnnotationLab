#' dummy function
#' @export
pinfo = function() {
  packageName()
  c(name=packageName(), version=packageVersion("BiocAnnotationLab"))
}

