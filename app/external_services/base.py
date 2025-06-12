from abc import abstractmethod


__all__ = ["BaseService"]


class BaseService:
    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    async def start(self):
        """
        Run actions for starting a service
        """
        raise NotImplementedError()

    @abstractmethod
    async def stop(self):
        """
        Run actions for stopping a service
        """
        raise NotImplementedError()

    async def healthcheck(self) -> tuple[bool, str]:
        return True, ""
