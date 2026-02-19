"""Tests for api/types.py - APIRegistry lookups."""

from jcc.api.types import APIRegistry, ClassInfo, MethodInfo
from jcc.ir.types import JCType


def make_test_registry() -> APIRegistry:
    """Create a test registry with common JavaCard classes."""
    # APDU class
    apdu_getBuffer = MethodInfo(
        class_name="javacard/framework/APDU",
        class_token=10,
        method_name="getBuffer",
        method_token=1,
        descriptor="()[B",
        is_static=False,
        return_type=JCType.REF,
    )
    apdu_getCurrentAPDU = MethodInfo(
        class_name="javacard/framework/APDU",
        class_token=10,
        method_name="getCurrentAPDU",
        method_token=5,
        descriptor="()Ljavacard/framework/APDU;",
        is_static=True,
        return_type=JCType.REF,
    )
    apdu = ClassInfo(
        name="javacard/framework/APDU",
        token=10,
        methods={
            "getBuffer": (apdu_getBuffer,),
            "getCurrentAPDU": (apdu_getCurrentAPDU,),
        },
    )

    # ISOException class
    iso_throwIt = MethodInfo(
        class_name="javacard/framework/ISOException",
        class_token=5,
        method_name="throwIt",
        method_token=0,
        descriptor="(S)V",
        is_static=True,
        return_type=None,
    )
    iso = ClassInfo(
        name="javacard/framework/ISOException",
        token=5,
        methods={"throwIt": (iso_throwIt,)},
    )

    # Util class
    util_arrayCopy = MethodInfo(
        class_name="javacard/framework/Util",
        class_token=15,
        method_name="arrayCopy",
        method_token=2,
        descriptor="([BS[BSS)S",
        is_static=True,
        return_type=JCType.SHORT,
    )
    util = ClassInfo(
        name="javacard/framework/Util",
        token=15,
        methods={"arrayCopy": (util_arrayCopy,)},
    )

    return APIRegistry(
        classes={
            "javacard/framework/APDU": apdu,
            "javacard/framework/ISOException": iso,
            "javacard/framework/Util": util,
        }
    )


class TestAPIRegistryLookup:
    def test_lookup_by_class_and_method(self) -> None:
        """Look up method by class and method name."""
        registry = make_test_registry()

        method = registry.lookup("javacard/framework/APDU", "getBuffer")
        assert method is not None
        assert method.method_name == "getBuffer"
        assert method.method_token == 1
        assert method.descriptor == "()[B"

    def test_lookup_unknown_class(self) -> None:
        """Unknown class returns None."""
        registry = make_test_registry()
        assert registry.lookup("unknown/Class", "method") is None

    def test_lookup_unknown_method(self) -> None:
        """Unknown method returns None."""
        registry = make_test_registry()
        assert registry.lookup("javacard/framework/APDU", "unknown") is None


class TestAPIRegistryIntrinsicLookup:
    def test_lookup_instance_method(self) -> None:
        """Look up instance method by C intrinsic name."""
        registry = make_test_registry()

        method = registry.lookup_intrinsic("__java_javacard_framework_APDU_getBuffer")
        assert method is not None
        assert method.method_name == "getBuffer"
        assert method.class_name == "javacard/framework/APDU"
        assert not method.is_static

    def test_lookup_static_method(self) -> None:
        """Look up static method by C intrinsic name."""
        registry = make_test_registry()

        method = registry.lookup_intrinsic("__java_javacard_framework_ISOException_throwIt")
        assert method is not None
        assert method.method_name == "throwIt"
        assert method.is_static

    def test_lookup_no_prefix(self) -> None:
        """Names without __java_ prefix return None."""
        registry = make_test_registry()
        assert registry.lookup_intrinsic("APDU_getBuffer") is None

    def test_lookup_no_underscore(self) -> None:
        """Names without class return None."""
        registry = make_test_registry()
        assert registry.lookup_intrinsic("__java_something") is None

    def test_lookup_unknown_intrinsic(self) -> None:
        """Unknown intrinsic returns None."""
        registry = make_test_registry()
        assert registry.lookup_intrinsic("__java_javacard_framework_Unknown_method") is None


class TestAPIRegistryGetClass:
    def test_get_class(self) -> None:
        """Get class by full name."""
        registry = make_test_registry()

        cls = registry.get_class("javacard/framework/APDU")
        assert cls is not None
        assert cls.token == 10

    def test_get_unknown_class(self) -> None:
        """Unknown class returns None."""
        registry = make_test_registry()
        assert registry.get_class("unknown/Class") is None


class TestMethodInfo:
    def test_return_type(self) -> None:
        """Method info has parsed return type."""
        registry = make_test_registry()

        getBuffer = registry.lookup("javacard/framework/APDU", "getBuffer")
        assert getBuffer is not None
        assert getBuffer.return_type == JCType.REF

        throwIt = registry.lookup("javacard/framework/ISOException", "throwIt")
        assert throwIt is not None
        assert throwIt.return_type is None  # void

        arrayCopy = registry.lookup("javacard/framework/Util", "arrayCopy")
        assert arrayCopy is not None
        assert arrayCopy.return_type == JCType.SHORT
