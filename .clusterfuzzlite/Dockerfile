# Fuzz build only. Nothing here ships in the plugin, and the engine stays standard library.
FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:6ccbb6b02fcbb8e07d15680e933a6d835cdb579636032cec7d256d0f25d483e4
COPY . $SRC/ant-vc
WORKDIR $SRC/ant-vc
COPY .clusterfuzzlite/build.sh $SRC/
