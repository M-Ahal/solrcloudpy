from typing import Any, TypeVar, Type, Callable, List, cast

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):  # type: ignore
    for f in fs:
        try:
            return f(x)
        except:
            assert False
    assert False


def to_class(c: Type[T], x: Any) -> dict[str, Any]:
    assert isinstance(x, c)
    return cast(Any, x).to_json()  # type: ignore
