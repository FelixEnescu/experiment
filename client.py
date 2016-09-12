
"""The Python implementation of the GRPC experiment.ExperimentService command
line client.

"""


from __future__ import print_function
import argparse
import grpc

import experiment_pb2

# Valid commands
COMMAND_START = 'start'
COMMAND_STOP = 'stop'
COMMAND_STATUS = 'status'


def run(grpc_stub, command, experiment_id, experiment_name):
    """ Run the actual command

    Args:
        grpc_stub: gRPC stub
        command: command to execute. Valid values are start, stop, status
        experiment_id:
        experiment_name:

    Returns:
        N/A
    """

    if command == COMMAND_START:
        response = grpc_stub.StartExperiment(experiment_pb2.Experiment(id=experiment_id, name=experiment_name))
    elif command == COMMAND_STATUS:
        response = grpc_stub.GetExperimentStatus(experiment_pb2.ExperimentId(id=experiment_id))
    elif command == COMMAND_STOP:
        response = grpc_stub.StopExperiment(experiment_pb2.Experiment(id=experiment_id, name=experiment_name))
    else:
        raise ValueError("Invalid command %s" % command)

    print("Sent command %s" % command)
    print("Received answer: %s" % response.status)


if __name__ == '__main__':

    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', required=True, dest='command', help='Command to execute. Valid options are: start, stop, status')
    parser.add_argument('-i', '--id', required=True, dest='experiment_id', help='Experiment id')
    parser.add_argument('-n', '--name', required=False, dest='experiment_name', help='Experiment name (default is "Experiment"')
    parser.add_argument('-g', '--grpc', required=False, dest='grpc_host', help='gRPCS host (default is localhost')

    args = parser.parse_args()

    if args.grpc_host is None:
        args.grpc_host = 'localhost'

    if args.experiment_name is None:
        args.experiment_name = 'Experiment'

    channel = grpc.insecure_channel(args.grpc_host + ':50051')
    stub = experiment_pb2.ExperimentServiceStub(channel)

    run(grpc_stub=stub,
        command=args.command,
        experiment_id=args.experiment_id,
        experiment_name=args.experiment_name)
