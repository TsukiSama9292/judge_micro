from judge_micro.config.settings import setting
from judge_micro.sdk.docker_ssh import RemoteDockerManager
import docker
from judge_micro.docker.images import DOCKER_IMAGES
class DockerEngine():
    DOCKER_IMAGES = DOCKER_IMAGES
    def __init__(self, docker_client=None):
        if not docker_client and setting.docker_ssh_remote:
            self.docker_client: RemoteDockerManager = RemoteDockerManager(
                host=setting.DOCKER_SSH_HOST,
                port=setting.DOCKER_SSH_PORT,
                key_path=setting.DOCKER_SSH_KEY_PATH,
                username=setting.DOCKER_SSH_USER,
                password=setting.DOCKER_SSH_PASSWORD,
            ).docker_client
        else:
            self.docker_client: docker.DockerClient = docker.from_env()

    def get_client(self):
        return self.docker_client

    def pull_needed_images(self):
        """
        Pull images if not found, but ignore if already exists
        """
        for image in self.DOCKER_IMAGES.values():
            try:
                if self.docker_client.images.get(image):
                    print(f"✅ Image {image} already exists")
                else:
                    self.docker_client.images.pull(image)
                    print(f"✅ Image {image} pulled successfully")
            
            except docker.errors.APIError:
                print(f"❌ Failed to pull image {image}, it may already exist or there is an issue with the Docker daemon")

docker_client = DockerEngine()
default_docker_client = docker_client.get_client()