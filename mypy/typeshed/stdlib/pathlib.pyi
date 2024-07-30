import sys
import types
from _typeshed import (
    OpenBinaryMode,
    OpenBinaryModeReading,
    OpenBinaryModeUpdating,
    OpenBinaryModeWriting,
    OpenTextMode,
    ReadableBuffer,
    StrOrBytesPath,
    StrPath,
    Unused,
)
from collections.abc import Callable, Generator, Iterator, Sequence
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from os import PathLike, stat_result
from types import TracebackType
from typing import IO, Any, BinaryIO, ClassVar, Literal, overload
from typing_extensions import Self, deprecated

if sys.version_info >= (3, 9):
    from types import GenericAlias

__all__ = ["PurePath", "PurePosixPath", "PureWindowsPath", "Path", "PosixPath", "WindowsPath"]

if sys.version_info >= (3, 13):
    __all__ += ["UnsupportedOperation"]

class PurePath(PathLike[str]):
    if sys.version_info >= (3, 13):
        parser: ClassVar[types.ModuleType]
        def full_match(self, pattern: StrPath, *, case_sensitive: bool | None = None) -> bool: ...

    @property
    def parts(self) -> tuple[str, ...]: ...
    @property
    def drive(self) -> str: ...
    @property
    def root(self) -> str: ...
    @property
    def anchor(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def suffix(self) -> str: ...
    @property
    def suffixes(self) -> list[str]: ...
    @property
    def stem(self) -> str: ...
    if sys.version_info >= (3, 12):
        def __new__(cls, *args: StrPath, **kwargs: Unused) -> Self: ...
        def __init__(self, *args: StrPath) -> None: ...
    else:
        def __new__(cls, *args: StrPath) -> Self: ...

    def __hash__(self) -> int: ...
    def __str__(self) -> str: ...
    def __fspath__(self) -> str: ...
    def __lt__(self, other: PurePath) -> bool: ...
    def __le__(self, other: PurePath) -> bool: ...
    def __gt__(self, other: PurePath) -> bool: ...
    def __ge__(self, other: PurePath) -> bool: ...
    def __truediv__(self, key: StrPath) -> Self: ...
    def __rtruediv__(self, key: StrPath) -> Self: ...
    def __bytes__(self) -> bytes: ...
    def as_posix(self) -> str: ...
    def as_uri(self) -> str: ...
    def is_absolute(self) -> bool: ...
    def is_reserved(self) -> bool: ...
    if sys.version_info >= (3, 12):
        def is_relative_to(self, other: StrPath, /, *_deprecated: StrPath) -> bool: ...
    elif sys.version_info >= (3, 9):
        def is_relative_to(self, *other: StrPath) -> bool: ...

    if sys.version_info >= (3, 12):
        def match(self, path_pattern: str, *, case_sensitive: bool | None = None) -> bool: ...
    else:
        def match(self, path_pattern: str) -> bool: ...

    if sys.version_info >= (3, 12):
        def relative_to(self, other: StrPath, /, *_deprecated: StrPath, walk_up: bool = False) -> Self: ...
    else:
        def relative_to(self, *other: StrPath) -> Self: ...

    def with_name(self, name: str) -> Self: ...
    if sys.version_info >= (3, 9):
        def with_stem(self, stem: str) -> Self: ...

    def with_suffix(self, suffix: str) -> Self: ...
    def joinpath(self, *other: StrPath) -> Self: ...
    @property
    def parents(self) -> Sequence[Self]: ...
    @property
    def parent(self) -> Self: ...
    if sys.version_info >= (3, 9) and sys.version_info < (3, 11):
        def __class_getitem__(cls, type: Any) -> GenericAlias: ...

    if sys.version_info >= (3, 12):
        def with_segments(self, *args: StrPath) -> Self: ...

class PurePosixPath(PurePath): ...
class PureWindowsPath(PurePath): ...

class Path(PurePath):
    def __new__(cls, *args: StrPath, **kwargs: Any) -> Self: ...
    @classmethod
    def cwd(cls) -> Self: ...
    if sys.version_info >= (3, 10):
        def stat(self, *, follow_symlinks: bool = True) -> stat_result: ...
        def chmod(self, mode: int, *, follow_symlinks: bool = True) -> None: ...
    else:
        def stat(self) -> stat_result: ...
        def chmod(self, mode: int) -> None: ...

    if sys.version_info >= (3, 13):
        @classmethod
        def from_uri(cls, uri: str) -> Path: ...
        def is_dir(self, *, follow_symlinks: bool = True) -> bool: ...
        def is_file(self, *, follow_symlinks: bool = True) -> bool: ...
        def read_text(self, encoding: str | None = None, errors: str | None = None, newline: str | None = None) -> str: ...
    else:
        def __enter__(self) -> Self: ...
        def __exit__(self, t: type[BaseException] | None, v: BaseException | None, tb: TracebackType | None) -> None: ...
        def is_dir(self) -> bool: ...
        def is_file(self) -> bool: ...
        def read_text(self, encoding: str | None = None, errors: str | None = None) -> str: ...

    if sys.version_info >= (3, 13):
        def glob(
            self, pattern: str, *, case_sensitive: bool | None = None, recurse_symlinks: bool = False
        ) -> Generator[Self, None, None]: ...
        def rglob(
            self, pattern: str, *, case_sensitive: bool | None = None, recurse_symlinks: bool = False
        ) -> Generator[Self, None, None]: ...
    elif sys.version_info >= (3, 12):
        def glob(self, pattern: str, *, case_sensitive: bool | None = None) -> Generator[Self, None, None]: ...
        def rglob(self, pattern: str, *, case_sensitive: bool | None = None) -> Generator[Self, None, None]: ...
    else:
        def glob(self, pattern: str) -> Generator[Self, None, None]: ...
        def rglob(self, pattern: str) -> Generator[Self, None, None]: ...

    if sys.version_info >= (3, 12):
        def exists(self, *, follow_symlinks: bool = True) -> bool: ...
    else:
        def exists(self) -> bool: ...

    def is_symlink(self) -> bool: ...
    def is_socket(self) -> bool: ...
    def is_fifo(self) -> bool: ...
    def is_block_device(self) -> bool: ...
    def is_char_device(self) -> bool: ...
    if sys.version_info >= (3, 12):
        def is_junction(self) -> bool: ...

    def iterdir(self) -> Generator[Self, None, None]: ...
    def lchmod(self, mode: int) -> None: ...
    def lstat(self) -> stat_result: ...
    def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None: ...
    # Adapted from builtins.open
    # Text mode: always returns a TextIOWrapper
    # The Traversable .open in stdlib/importlib/abc.pyi should be kept in sync with this.
    @overload
    def open(
        self,
        mode: OpenTextMode = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> TextIOWrapper: ...
    # Unbuffered binary mode: returns a FileIO
    @overload
    def open(
        self, mode: OpenBinaryMode, buffering: Literal[0], encoding: None = None, errors: None = None, newline: None = None
    ) -> FileIO: ...
    # Buffering is on: return BufferedRandom, BufferedReader, or BufferedWriter
    @overload
    def open(
        self,
        mode: OpenBinaryModeUpdating,
        buffering: Literal[-1, 1] = -1,
        encoding: None = None,
        errors: None = None,
        newline: None = None,
    ) -> BufferedRandom: ...
    @overload
    def open(
        self,
        mode: OpenBinaryModeWriting,
        buffering: Literal[-1, 1] = -1,
        encoding: None = None,
        errors: None = None,
        newline: None = None,
    ) -> BufferedWriter: ...
    @overload
    def open(
        self,
        mode: OpenBinaryModeReading,
        buffering: Literal[-1, 1] = -1,
        encoding: None = None,
        errors: None = None,
        newline: None = None,
    ) -> BufferedReader: ...
    # Buffering cannot be determined: fall back to BinaryIO
    @overload
    def open(
        self, mode: OpenBinaryMode, buffering: int = -1, encoding: None = None, errors: None = None, newline: None = None
    ) -> BinaryIO: ...
    # Fallback if mode is not specified
    @overload
    def open(
        self, mode: str, buffering: int = -1, encoding: str | None = None, errors: str | None = None, newline: str | None = None
    ) -> IO[Any]: ...
    if sys.platform != "win32":
        # These methods do "exist" on Windows, but they always raise NotImplementedError,
        # so it's safer to pretend they don't exist
        if sys.version_info >= (3, 13):
            def owner(self, *, follow_symlinks: bool = True) -> str: ...
            def group(self, *, follow_symlinks: bool = True) -> str: ...
        else:
            def owner(self) -> str: ...
            def group(self) -> str: ...

    # This method does "exist" on Windows on <3.12, but always raises NotImplementedError
    # On py312+, it works properly on Windows, as with all other platforms
    if sys.platform != "win32" or sys.version_info >= (3, 12):
        def is_mount(self) -> bool: ...

    if sys.version_info >= (3, 9):
        def readlink(self) -> Self: ...

    def rename(self, target: str | PurePath) -> Self: ...
    def replace(self, target: str | PurePath) -> Self: ...
    def resolve(self, strict: bool = False) -> Self: ...
    def rmdir(self) -> None: ...
    def symlink_to(self, target: StrOrBytesPath, target_is_directory: bool = False) -> None: ...
    if sys.version_info >= (3, 10):
        def hardlink_to(self, target: StrOrBytesPath) -> None: ...

    def touch(self, mode: int = 0o666, exist_ok: bool = True) -> None: ...
    def unlink(self, missing_ok: bool = False) -> None: ...
    @classmethod
    def home(cls) -> Self: ...
    def absolute(self) -> Self: ...
    def expanduser(self) -> Self: ...
    def read_bytes(self) -> bytes: ...
    def samefile(self, other_path: StrPath) -> bool: ...
    def write_bytes(self, data: ReadableBuffer) -> int: ...
    if sys.version_info >= (3, 10):
        def write_text(
            self, data: str, encoding: str | None = None, errors: str | None = None, newline: str | None = None
        ) -> int: ...
    else:
        def write_text(self, data: str, encoding: str | None = None, errors: str | None = None) -> int: ...
    if sys.version_info < (3, 12):
        if sys.version_info >= (3, 10):
            @deprecated("Deprecated as of Python 3.10 and removed in Python 3.12. Use hardlink_to() instead.")
            def link_to(self, target: StrOrBytesPath) -> None: ...
        else:
            def link_to(self, target: StrOrBytesPath) -> None: ...
    if sys.version_info >= (3, 12):
        def walk(
            self, top_down: bool = ..., on_error: Callable[[OSError], object] | None = ..., follow_symlinks: bool = ...
        ) -> Iterator[tuple[Self, list[str], list[str]]]: ...

class PosixPath(Path, PurePosixPath): ...
class WindowsPath(Path, PureWindowsPath): ...

if sys.version_info >= (3, 13):
    class UnsupportedOperation(NotImplementedError): ...
