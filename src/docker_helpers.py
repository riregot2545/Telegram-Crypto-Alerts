import logging

from get_docker_secret import get_docker_secret

logger = logging.getLogger()


def get_swarm_secret(secret_name):
    try:
        return get_docker_secret(secret_name, safe=False, autocast_name=False)
    except Exception as e:
        logger.error(f"Error retrieving secret '{secret_name}': {e}")
        raise RuntimeError(e)
