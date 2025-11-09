from aoq_factory.exc import AOQFactoryBaseException


class AnimeAlreadyExists(AOQFactoryBaseException):
    pass


class NoSuchAnime(AOQFactoryBaseException):
    pass


class SongAlreadyExists(AOQFactoryBaseException):
    pass


class NoSuchSong(AOQFactoryBaseException):
    pass


class SourceAlreadyExists(AOQFactoryBaseException):
    pass


class NoSuchSource(AOQFactoryBaseException):
    pass


class TimingAlreadyExists(AOQFactoryBaseException):
    pass


class NoSuchTiming(AOQFactoryBaseException):
    pass


class LevelAlreadyExists(AOQFactoryBaseException):
    pass


class NoSuchLevel(AOQFactoryBaseException):
    pass


class InvalidLevelValue(AOQFactoryBaseException):
    pass


class UniqueConstraintViolation(AOQFactoryBaseException):
    pass
