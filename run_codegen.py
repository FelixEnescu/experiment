
"""Runs protoc with the gRPC plugin to generate messages and gRPC stubs."""

from grpc.tools import protoc

protoc.main(
    (
	'',
	'-I./',
	'--python_out=.',
	'--grpc_python_out=.',
	'./experiment.proto',
    )
)
