
"""The Python implementation of the GRPC experiment.ExperimentService
server.
"""


from concurrent import futures
import time
import random

import grpc
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded

import experiment_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_ONE_YEAR_IN_SECONDS = _ONE_DAY_IN_SECONDS * 365

CELERY_CONFIG = {
    "CELERY_APP_NAME": "experiment",
    "CELERY_BROKER_URL": "redis://redis:6379/0",
    "CELERY_RESULT_BACKEND": "redis://redis:6379/0",
    "CELERYD_TASK_TIME_LIMIT": _ONE_YEAR_IN_SECONDS
}

celery_app = Celery(
    CELERY_CONFIG["CELERY_BROKER_URL"],
    backend=CELERY_CONFIG["CELERY_RESULT_BACKEND"],
    broker=CELERY_CONFIG["CELERY_BROKER_URL"],
    include=['server']
    )
celery_app.conf.update(CELERY_CONFIG)


@celery_app.task(bind=True, name="long_task")
def long_task(self, experiment_id):
    """Long running experiment CPU/GPU bound.

    Args:
        experiment_id: the is of experiment

    Returns:
        seconds_count: number of seconds worked
    """

    seconds_count = 0
    while True:
        try:
            time.sleep(1)
            seconds_count += 1

            verb = ["transglutinating", "fine-tuning"]
            adjective = ["injector", "radiant"]
            noun = ["goatherd", "post-processor"]
            message = "%s %s %s (%s)..." % (random.choice(verb),
                                            random.choice(adjective),
                                            random.choice(noun),
                                            experiment_id)
            self.update_state(state="PROGRESS",
                              meta={'current': seconds_count, "status" : message}
                             )
        except SoftTimeLimitExceeded as exception:
            # received termination request
            # clean up and exit
            break
        except Exception as exception:
            # unexpected exception
            # treat it
            break

    return seconds_count


class ExperimentService(experiment_pb2.ExperimentServiceServicer):
    experiments = {}

    def StartExperiment(self, request, context):
        # check if experiment with request.id already started
        if ExperimentService.experiments.get(request.id, None) is None:
            # start experiment
            task_id = long_task.apply_async((request.id,))

            ExperimentService.experiments[request.id] = {
                "name": request.name,
                "task_id": task_id
            }

        # return status
        message = 'Started experiment id %s, name %s, task id %s' % (
            request.id,
            request.name,
            ExperimentService.experiments[request.id]["task_id"].id)
        return experiment_pb2.ExperimentStatus(status=message)

    def StopExperiment(self, request, context):
        if ExperimentService.experiments.get(request.id, None) is None:
            return experiment_pb2.ExperimentStatus(status="Experiment %s not found" % (request.id,))

        # causes the SoftTimeLimitExceeded exception to be raised in the task,
        # normally terminating
        celery_app.control.revoke(
            ExperimentService.experiments[request.id]["task_id"].id,
            terminate=True,
            signal='SIGUSR1')
        message = 'Stoped experiment id %s, name %s, task id %s' % (
            request.id,
            request.name,
            ExperimentService.experiments[request.id]["task_id"].id)
        del ExperimentService.experiments[request.id]
        return experiment_pb2.ExperimentStatus(status=message)

    def GetExperimentStatus(self, request, context):
        if ExperimentService.experiments.get(request.id, None) is None:
            message = "Experiment %s not found" % (request.id,)
        else:
            task = celery_app.AsyncResult(ExperimentService.experiments[request.id]["task_id"].id)
            # pending tasks do not have yet extra info
            try:
                info_current = task.info.get('current', 0)
                info_status = task.info.get('status', 0)
            except:
                info_current = 0
                info_status = ''
            message = "Experiment %s is in state %s; current seconds %s, status message: %s" % (
                request.id,
                task.state,
                info_current,
                info_status)

        return experiment_pb2.ExperimentStatus(status=message)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    experiment_pb2.add_ExperimentServiceServicer_to_server(ExperimentService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
