from judge_micro.config.settings import setting
from judge_micro.sdk.docker_ssh import RemoteDockerManager
import docker

class DockerEngine():
    def __init__(self, docker_client=None):
        if not docker_client and setting.docker_ssh_remote:
            self.docker_client: RemoteDockerManager = RemoteDockerManager(
                host=setting.DOCKER_SSH_HOST,
                port=setting.DOCKER_SSH_PORT,
                key_path=setting.DOCKER_SSH_KEY_PATH,
                username=setting.DOCKER_SSH_USER,
                password=setting.DOCKER_SSH_PASSWORD,
            )
        else:
            self.docker_client: docker.DockerClient = docker.from_env()

    def get_client(self):
        return self.docker_client

default_docker_client = DockerEngine().get_client()