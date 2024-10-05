try:
    import pydantic.v1 as pydantic
    from pydantic.v1 import (
        BaseConfig,
        BaseModel,
        Field,
        PrivateAttr,
        StrictFloat,
        StrictInt,
        StrictStr,
        create_model,
        root_validator,
        validator,
    )
    from pydantic.v1.error_wrappers import ValidationError
    from pydantic.v1.fields import FieldInfo
    from pydantic.v1.generics import GenericModel
except ImportError:
    import pydantic  # type: ignore
    from pydantic import (
        BaseConfig,
        BaseModel,
        Field,
        PrivateAttr,
        StrictFloat,
        StrictInt,
        StrictStr,
        create_model,
        root_validator,
        validator,
    )
    from pydantic.error_wrappers import ValidationError
    from pydantic.fields import FieldInfo
    from pydantic.generics import GenericModel
