from loguru import logger as log


class Logger:
    def info(self, msg: str) -> None:
        log.info(msg)

    def warn(self, msg: str) -> None:
        log.warning(msg)

    def error(self, msg: str) -> None:
        log.error(msg)

    def debug(self, msg: str) -> None:
        log.debug(msg)
