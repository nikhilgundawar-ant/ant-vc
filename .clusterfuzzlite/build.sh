#!/bin/bash -eu
# ClusterFuzzLite calls this inside the base image, which already has Atheris and PyInstaller.
cd "$SRC/ant-vc"
for fuzzer in .clusterfuzzlite/fuzz_*.py; do
  compile_python_fuzzer "$fuzzer" --paths engine --paths hooks \
    --add-data "evals/golden/bundles/aditi.json:." --add-data "ontology:ontology"
done
