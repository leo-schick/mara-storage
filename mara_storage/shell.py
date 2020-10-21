"""
Shell command generation for
- reading/writing/deleting files in storages via their command line clients
"""

from functools import singledispatch
import shlex

from mara_storage.compression import Compression, uncompressor
from mara_storage import storages, config


@singledispatch
def read_file_command(storage: object, file_name: str, compression: Compression = Compression.NONE) -> str:
    """
    Creates a shell command that reads a file and sends it to stdout

    Args:
        storage: The storage where the file is stored
        file_name: The file name within the storage
        compression: The compression to be used to uncompress the file

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement read_file_command for type "{storage.__class__.__name__}"')


@read_file_command.register(str)
def __(alias: str, file_name: str, compression: Compression = Compression.NONE):
    return read_file_command(storages.storage(alias), file_name=file_name, compression=compression)


@read_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE):
    return f'{uncompressor(compression)} '+shlex.quote(str( (storage.base_path / file_name).absolute() ))


# -----------------------------------------------------------------------------


@singledispatch
def write_file_command(storage: object, file_name: str, compression: Compression = Compression.NONE) -> str:
    """
    Creates a shell command that writes a file content from stdin

    Args:
        storage: The storage where the file will be stored
        file_name: The file name within the storage
        compression: The compression to be used to compress the file

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement write_file_command for type "{storage.__class__.__name__}"')


@write_file_command.register(str)
def __(alias: str, file_name: str, compression: Compression = Compression.NONE):
    return write_file_command(storages.storage, file_name=file_name, compression=compression)


@write_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, compression: Compression = Compression.NONE):
    if compression not in [Compression.NONE]:
        ValueError(f'Only compression NONE is supported from storage type "{storage.__class__.__name__}"')
    return 'cat - > ' + shlex.quote(str( (storage.base_path / file_name).absolute() ))


# -----------------------------------------------------------------------------


@singledispatch
def delete_file_command(storage: object, file_name: str, force: bool = True) -> str:
    """
    Creates a shell command that deletes a file on a storage

    When the file does not exist, the command should silently end
    without error (exit code 0)

    Args:
        storage: The storage where the file is stored
        file_name: The file name within the storage
        force: If True, the command will silently end without error (exit code 0)
               when the file does not exist

    Returns:
        A shell command string
    """
    raise NotImplementedError(f'Please implement delete_file_command for type "{storage.__class__.__name__}"')


@delete_file_command.register(str)
def __(alias: str, file_name: str, force: bool = True):
    return delete_file_command(storages.storage(alias), file_name=file_name, force=force)


@delete_file_command.register(storages.LocalStorage)
def __(storage: storages.LocalStorage, file_name: str, force: bool = True):
    return ('rm '
            + ('-f ' if force else '')
            + shlex.quote(str( (storage.base_path / file_name).absolute() )))
