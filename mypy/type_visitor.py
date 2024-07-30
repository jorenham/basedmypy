"""Type visitor classes.

This module defines the type visitors that are intended to be
subclassed by other code.  They have been separated out into their own
module to ease converting mypy to run under mypyc, since currently
mypyc-extension classes can extend interpreted classes but not the
other way around. Separating them out, then, allows us to compile
types before we can compile everything that uses a TypeVisitor.

The visitors are all re-exported from mypy.types and that is how
other modules refer to them.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Callable, Final, Generic, Iterable, Sequence, TypeVar, cast

from mypy_extensions import mypyc_attr, trait

from mypy.types import (
    AnyType,
    CallableArgument,
    CallableType,
    DeletedType,
    EllipsisType,
    ErasedType,
    Instance,
    IntersectionType,
    LiteralType,
    NoneType,
    Overloaded,
    Parameters,
    ParamSpecType,
    PartialType,
    PlaceholderType,
    RawExpressionType,
    TupleType,
    Type,
    TypeAliasType,
    TypedDictType,
    TypeGuardType,
    TypeList,
    TypeType,
    TypeVarLikeType,
    TypeVarTupleType,
    TypeVarType,
    UnboundType,
    UninhabitedType,
    UnionType,
    UnpackType,
    get_proper_type,
)

T = TypeVar("T")


@trait
@mypyc_attr(allow_interpreted_subclasses=True)
class TypeVisitor(Generic[T]):
    """Visitor class for types (Type subclasses).

    The parameter T is the return type of the visit methods.
    """

    @abstractmethod
    def visit_unbound_type(self, t: UnboundType) -> T:
        pass

    @abstractmethod
    def visit_any(self, t: AnyType) -> T:
        pass

    @abstractmethod
    def visit_none_type(self, t: NoneType) -> T:
        pass

    @abstractmethod
    def visit_uninhabited_type(self, t: UninhabitedType) -> T:
        pass

    @abstractmethod
    def visit_erased_type(self, t: ErasedType) -> T:
        pass

    @abstractmethod
    def visit_deleted_type(self, t: DeletedType) -> T:
        pass

    @abstractmethod
    def visit_type_var(self, t: TypeVarType) -> T:
        pass

    @abstractmethod
    def visit_param_spec(self, t: ParamSpecType) -> T:
        pass

    @abstractmethod
    def visit_parameters(self, t: Parameters) -> T:
        pass

    @abstractmethod
    def visit_type_var_tuple(self, t: TypeVarTupleType) -> T:
        pass

    @abstractmethod
    def visit_instance(self, t: Instance) -> T:
        pass

    @abstractmethod
    def visit_callable_type(self, t: CallableType) -> T:
        pass

    @abstractmethod
    def visit_overloaded(self, t: Overloaded) -> T:
        pass

    @abstractmethod
    def visit_tuple_type(self, t: TupleType) -> T:
        pass

    @abstractmethod
    def visit_typeddict_type(self, t: TypedDictType) -> T:
        pass

    @abstractmethod
    def visit_literal_type(self, t: LiteralType) -> T:
        pass

    @abstractmethod
    def visit_union_type(self, t: UnionType) -> T:
        pass

    @abstractmethod
    def visit_intersection_type(self, t: IntersectionType) -> T:
        pass

    @abstractmethod
    def visit_partial_type(self, t: PartialType) -> T:
        pass

    @abstractmethod
    def visit_type_type(self, t: TypeType) -> T:
        pass

    @abstractmethod
    def visit_type_alias_type(self, t: TypeAliasType) -> T:
        pass

    @abstractmethod
    def visit_unpack_type(self, t: UnpackType) -> T:
        pass

    def visit_typeguard_type(self, t: TypeGuardType) -> T:
        raise NotImplementedError


@trait
@mypyc_attr(allow_interpreted_subclasses=True)
class SyntheticTypeVisitor(TypeVisitor[T]):
    """A TypeVisitor that also knows how to visit synthetic AST constructs.

    Not just real types.
    """

    @abstractmethod
    def visit_type_list(self, t: TypeList) -> T:
        pass

    @abstractmethod
    def visit_callable_argument(self, t: CallableArgument) -> T:
        pass

    @abstractmethod
    def visit_ellipsis_type(self, t: EllipsisType) -> T:
        pass

    @abstractmethod
    def visit_raw_expression_type(self, t: RawExpressionType) -> T:
        pass

    @abstractmethod
    def visit_placeholder_type(self, t: PlaceholderType) -> T:
        pass


@mypyc_attr(allow_interpreted_subclasses=True)
class TypeTranslator(TypeVisitor[Type]):
    """Identity type transformation.

    Subclass this and override some methods to implement a non-trivial
    transformation.
    """

    def visit_unbound_type(self, t: UnboundType) -> Type:
        return t

    def visit_any(self, t: AnyType) -> Type:
        return t

    def visit_none_type(self, t: NoneType) -> Type:
        return t

    def visit_uninhabited_type(self, t: UninhabitedType) -> Type:
        return t

    def visit_erased_type(self, t: ErasedType) -> Type:
        return t

    def visit_deleted_type(self, t: DeletedType) -> Type:
        return t

    def visit_instance(self, t: Instance) -> Type:
        last_known_value: LiteralType | None = None
        if t.last_known_value is not None:
            raw_last_known_value = t.last_known_value.accept(self)
            assert isinstance(raw_last_known_value, LiteralType)  # type: ignore[misc]
            last_known_value = raw_last_known_value
        result = Instance(
            typ=t.type,
            args=self.translate_types(t.args),
            line=t.line,
            column=t.column,
            last_known_value=last_known_value,
        )
        result.metadata = t.metadata
        return result

    def visit_type_var(self, t: TypeVarType) -> Type:
        return t

    def visit_param_spec(self, t: ParamSpecType) -> Type:
        return t

    def visit_parameters(self, t: Parameters) -> Type:
        return t.copy_modified(arg_types=self.translate_types(t.arg_types))

    def visit_type_var_tuple(self, t: TypeVarTupleType) -> Type:
        return t

    def visit_partial_type(self, t: PartialType) -> Type:
        return t

    def visit_unpack_type(self, t: UnpackType) -> Type:
        return UnpackType(t.type.accept(self))

    def visit_callable_type(self, t: CallableType) -> Type:
        return t.copy_modified(
            arg_types=self.translate_types(t.arg_types),
            ret_type=t.ret_type.accept(self),
            variables=self.translate_variables(t.variables),
        )

    def visit_tuple_type(self, t: TupleType) -> Type:
        return TupleType(
            self.translate_types(t.items),
            # TODO: This appears to be unsafe.
            cast(Any, t.partial_fallback.accept(self)),
            t.line,
            t.column,
        )

    def visit_typeddict_type(self, t: TypedDictType) -> Type:
        items = {item_name: item_type.accept(self) for (item_name, item_type) in t.items.items()}
        return TypedDictType(
            items,
            t.required_keys,
            # TODO: This appears to be unsafe.
            cast(Any, t.fallback.accept(self)),
            t.line,
            t.column,
        )

    def visit_literal_type(self, t: LiteralType) -> Type:
        fallback = t.fallback.accept(self)
        assert isinstance(fallback, Instance)  # type: ignore[misc]
        return LiteralType(value=t.value, fallback=fallback, line=t.line, column=t.column)

    def visit_union_type(self, t: UnionType) -> Type:
        return UnionType(
            self.translate_types(t.items),
            t.line,
            t.column,
            uses_pep604_syntax=t.uses_pep604_syntax,
        )

    def visit_intersection_type(self, t: IntersectionType) -> Type:
        return IntersectionType(self.translate_types(t.items), t.line, t.column)

    def translate_types(self, types: Iterable[Type]) -> list[Type]:
        return [t.accept(self) for t in types]

    def translate_variables(
        self, variables: Sequence[TypeVarLikeType]
    ) -> Sequence[TypeVarLikeType]:
        return variables

    def visit_overloaded(self, t: Overloaded) -> Type:
        items: list[CallableType] = []
        for item in t.items:
            new = item.accept(self)
            assert isinstance(new, CallableType)  # type: ignore[misc]
            items.append(new)
        return Overloaded(items=items)

    def visit_type_type(self, t: TypeType) -> Type:
        return TypeType.make_normalized(t.item.accept(self), line=t.line, column=t.column)

    @abstractmethod
    def visit_type_alias_type(self, t: TypeAliasType) -> Type:
        # This method doesn't have a default implementation for type translators,
        # because type aliases are special: some information is contained in the
        # TypeAlias node, and we normally don't generate new nodes. Every subclass
        # must implement this depending on its semantics.
        pass


@mypyc_attr(allow_interpreted_subclasses=True)
class TypeQuery(SyntheticTypeVisitor[T]):
    """Visitor for performing queries of types.

    strategy is used to combine results for a series of types,
    common use cases involve a boolean query using `any` or `all`.

    Note: this visitor keeps an internal state (tracks type aliases to avoid
    recursion), so it should *never* be re-used for querying different types,
    create a new visitor instance instead.

    # TODO: check that we don't have existing violations of this rule.
    """

    def __init__(self, strategy: Callable[[list[T]], T]) -> None:
        self.strategy = strategy
        # Keep track of the type aliases already visited. This is needed to avoid
        # infinite recursion on types like A = Union[int, List[A]].
        self.seen_aliases: set[TypeAliasType] = set()
        # By default, we eagerly expand type aliases, and query also types in the
        # alias target. In most cases this is a desired behavior, but we may want
        # to skip targets in some cases (e.g. when collecting type variables).
        self.skip_alias_target = False

    def visit_unbound_type(self, t: UnboundType) -> T:
        return self.query_types(t.args)

    def visit_type_list(self, t: TypeList) -> T:
        return self.query_types(t.items)

    def visit_callable_argument(self, t: CallableArgument) -> T:
        return t.typ.accept(self)

    def visit_any(self, t: AnyType) -> T:
        return self.strategy([])

    def visit_uninhabited_type(self, t: UninhabitedType) -> T:
        return self.strategy([])

    def visit_none_type(self, t: NoneType) -> T:
        return self.strategy([])

    def visit_erased_type(self, t: ErasedType) -> T:
        return self.strategy([])

    def visit_deleted_type(self, t: DeletedType) -> T:
        return self.strategy([])

    def visit_type_var(self, t: TypeVarType) -> T:
        return self.query_types([t.upper_bound, t.default] + t.values)

    def visit_param_spec(self, t: ParamSpecType) -> T:
        return self.query_types([t.upper_bound, t.default, t.prefix])

    def visit_type_var_tuple(self, t: TypeVarTupleType) -> T:
        return self.query_types([t.upper_bound, t.default])

    def visit_unpack_type(self, t: UnpackType) -> T:
        return self.query_types([t.type])

    def visit_parameters(self, t: Parameters) -> T:
        return self.query_types(t.arg_types)

    def visit_partial_type(self, t: PartialType) -> T:
        return self.strategy([])

    def visit_instance(self, t: Instance) -> T:
        return self.query_types(t.args)

    def visit_callable_type(self, t: CallableType) -> T:
        # FIX generics
        return self.query_types(t.arg_types + [t.ret_type])

    def visit_tuple_type(self, t: TupleType) -> T:
        return self.query_types(t.items)

    def visit_typeddict_type(self, t: TypedDictType) -> T:
        return self.query_types(t.items.values())

    def visit_raw_expression_type(self, t: RawExpressionType) -> T:
        if t.node is not None:
            return t.node.accept(self)
        return self.strategy([])

    def visit_literal_type(self, t: LiteralType) -> T:
        return self.strategy([])

    def visit_union_type(self, t: UnionType) -> T:
        return self.query_types(t.items)

    def visit_intersection_type(self, t: IntersectionType) -> T:
        return self.query_types(t.items)

    def visit_overloaded(self, t: Overloaded) -> T:
        return self.query_types(t.items)

    def visit_type_type(self, t: TypeType) -> T:
        return t.item.accept(self)

    def visit_ellipsis_type(self, t: EllipsisType) -> T:
        return self.strategy([])

    def visit_placeholder_type(self, t: PlaceholderType) -> T:
        return self.query_types(t.args)

    def visit_type_alias_type(self, t: TypeAliasType) -> T:
        # Skip type aliases already visited types to avoid infinite recursion.
        # TODO: Ideally we should fire subvisitors here (or use caching) if we care
        #       about duplicates.
        if t in self.seen_aliases:
            return self.strategy([])
        self.seen_aliases.add(t)
        if self.skip_alias_target:
            return self.query_types(t.args)
        return get_proper_type(t).accept(self)

    def query_types(self, types: Iterable[Type]) -> T:
        """Perform a query for a list of types using the strategy to combine the results."""
        return self.strategy([t.accept(self) for t in types])


# Return True if at least one type component returns True
ANY_STRATEGY: Final = 0
# Return True if no type component returns False
ALL_STRATEGY: Final = 1


class BoolTypeQuery(SyntheticTypeVisitor[bool]):
    """Visitor for performing recursive queries of types with a bool result.

    Use TypeQuery if you need non-bool results.

    'strategy' is used to combine results for a series of types. It must
    be ANY_STRATEGY or ALL_STRATEGY.

    Note: This visitor keeps an internal state (tracks type aliases to avoid
    recursion), so it should *never* be re-used for querying different types
    unless you call reset() first.
    """

    def __init__(self, strategy: int) -> None:
        self.strategy = strategy
        if strategy == ANY_STRATEGY:
            self.default = False
        else:
            assert strategy == ALL_STRATEGY
            self.default = True
        # Keep track of the type aliases already visited. This is needed to avoid
        # infinite recursion on types like A = Union[int, List[A]]. An empty set is
        # represented as None as a micro-optimization.
        self.seen_aliases: set[TypeAliasType] | None = None
        # By default, we eagerly expand type aliases, and query also types in the
        # alias target. In most cases this is a desired behavior, but we may want
        # to skip targets in some cases (e.g. when collecting type variables).
        self.skip_alias_target = False

    def reset(self) -> None:
        """Clear mutable state (but preserve strategy).

        This *must* be called if you want to reuse the visitor.
        """
        self.seen_aliases = None

    def visit_unbound_type(self, t: UnboundType) -> bool:
        return self.query_types(t.args)

    def visit_type_list(self, t: TypeList) -> bool:
        return self.query_types(t.items)

    def visit_callable_argument(self, t: CallableArgument) -> bool:
        return t.typ.accept(self)

    def visit_any(self, t: AnyType) -> bool:
        return self.default

    def visit_uninhabited_type(self, t: UninhabitedType) -> bool:
        return self.default

    def visit_none_type(self, t: NoneType) -> bool:
        return self.default

    def visit_erased_type(self, t: ErasedType) -> bool:
        return self.default

    def visit_deleted_type(self, t: DeletedType) -> bool:
        return self.default

    def visit_type_var(self, t: TypeVarType) -> bool:
        return self.query_types([t.upper_bound, t.default] + t.values)

    def visit_param_spec(self, t: ParamSpecType) -> bool:
        return self.query_types([t.upper_bound, t.default])

    def visit_type_var_tuple(self, t: TypeVarTupleType) -> bool:
        return self.query_types([t.upper_bound, t.default])

    def visit_unpack_type(self, t: UnpackType) -> bool:
        return self.query_types([t.type])

    def visit_parameters(self, t: Parameters) -> bool:
        return self.query_types(t.arg_types)

    def visit_partial_type(self, t: PartialType) -> bool:
        return self.default

    def visit_instance(self, t: Instance) -> bool:
        return self.query_types(t.args)

    def visit_callable_type(self, t: CallableType) -> bool:
        # FIX generics
        # Avoid allocating any objects here as an optimization.
        args = self.query_types(t.arg_types)
        ret = t.ret_type.accept(self)
        if self.strategy == ANY_STRATEGY:
            return args or ret
        else:
            return args and ret

    def visit_tuple_type(self, t: TupleType) -> bool:
        return self.query_types(t.items)

    def visit_typeddict_type(self, t: TypedDictType) -> bool:
        return self.query_types(list(t.items.values()))

    def visit_raw_expression_type(self, t: RawExpressionType) -> bool:
        if t.node is not None:
            return t.node.accept(self)
        return self.default

    def visit_literal_type(self, t: LiteralType) -> bool:
        return self.default

    def visit_union_type(self, t: UnionType) -> bool:
        return self.query_types(t.items)

    def visit_intersection_type(self, t: IntersectionType) -> bool:
        return self.query_types(t.items)

    def visit_overloaded(self, t: Overloaded) -> bool:
        return self.query_types(t.items)  # type: ignore[arg-type]

    def visit_type_type(self, t: TypeType) -> bool:
        return t.item.accept(self)

    def visit_ellipsis_type(self, t: EllipsisType) -> bool:
        return self.default

    def visit_placeholder_type(self, t: PlaceholderType) -> bool:
        return self.query_types(t.args)

    def visit_type_alias_type(self, t: TypeAliasType) -> bool:
        # Skip type aliases already visited types to avoid infinite recursion.
        # TODO: Ideally we should fire subvisitors here (or use caching) if we care
        #       about duplicates.
        if self.seen_aliases is None:
            self.seen_aliases = set()
        elif t in self.seen_aliases:
            return self.default
        self.seen_aliases.add(t)
        if self.skip_alias_target:
            return self.query_types(t.args)
        return get_proper_type(t).accept(self)

    def query_types(self, types: list[Type] | tuple[Type, ...]) -> bool:
        """Perform a query for a sequence of types using the strategy to combine the results."""
        # Special-case for lists and tuples to allow mypyc to produce better code.
        if isinstance(types, list):
            if self.strategy == ANY_STRATEGY:
                return any(t.accept(self) for t in types)
            else:
                return all(t.accept(self) for t in types)
        else:
            if self.strategy == ANY_STRATEGY:
                return any(t.accept(self) for t in types)
            else:
                return all(t.accept(self) for t in types)
