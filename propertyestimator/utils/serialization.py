"""
A collection of classes which aid in serializing data types.
"""

import importlib
import inspect
import json
import sys
from enum import Enum
from io import BytesIO

from openforcefield.typing.engines.smirnoff import ForceField

from pydantic import BaseModel, ValidationError
from pydantic.validators import dict_validator
from simtk import unit


def _type_string_to_object(type_string):
    last_period_index = type_string.rfind('.')

    if last_period_index < 0 or last_period_index == len(type_string) - 1:
        raise ValueError('The type string is invalid - it should be of the form '
                         'module_path.class_name: {}'.format(type_string))

    module_name = type_string[0:last_period_index]
    module = importlib.import_module(module_name)

    class_name = type_string[last_period_index + 1:]

    if class_name == 'NoneType':
        return None

    class_name_split = class_name.split('->')
    class_object = module

    while len(class_name_split) > 0:
        class_name_current = class_name_split.pop(0)
        class_object = getattr(class_object, class_name_current)

    return class_object


def serialize_quantity(quantity):
    """
    Serialized a simtk.unit.Quantity into a dict of {'unitless_value': X, 'unit': Y}

    .. todo:: Currently duplicates Jeff Wagners implementation.

    Parameters
    ----------
    quantity : A simtk.unit.Quantity-wrapped value or iterator over values
        The object to serialize

    Returns
    -------
    serialzied : dict
        The serialized object
    """

    if not isinstance(quantity, unit.Quantity):
        raise ValueError('{} is not a Quantity'.format(type(quantity)))

    serialized = dict()

    # If it's None, just return None in all fields
    if quantity is None:
        serialized['unitless_value'] = None
        serialized['unit'] = None
        return serialized

    # If it's not None, make sure it's a simtk.unit.Quantity
    assert (hasattr(quantity, 'unit'))

    quantity_unit = list()
    for base_unit in quantity.unit.iter_all_base_units():
        quantity_unit.append((base_unit[0].name, base_unit[1]))

    conversion_factor = quantity.unit.get_conversion_factor_to_base_units()

    unitless_value = (quantity / quantity.unit) * conversion_factor
    serialized['unitless_value'] = unitless_value
    serialized['unit'] = quantity_unit
    return serialized


def deserialize_quantity(serialized):
    """
    Deserializes a simtk.unit.Quantity.

    .. todo:: Currently duplicates Jeff Wagners implementation.

    Parameters
    ----------
    serialized : dict
        Serialized representation of a simtk.unit.Quantity. Must have keys ["unitless_value", "unit"]

    Returns
    -------
    simtk.unit.Quantity
    """

    if '@type' in serialized:
        serialized.pop('@type')

    if (serialized['unitless_value'] is None) and (serialized['unit'] is None):
        return None
    quantity_unit = None
    for unit_name, power in serialized['unit']:
        unit_name = unit_name.replace(' ', '_')  # Convert eg. 'elementary charge' to 'elementary_charge'
        if quantity_unit is None:
            quantity_unit = (getattr(unit, unit_name) ** power)
        else:
            quantity_unit *= (getattr(unit, unit_name) ** power)
    quantity = unit.Quantity(serialized['unitless_value'], quantity_unit)
    return quantity


def serialize_force_field(force_field):
    """A method for turning an `openforcefield.typing.engines.smirnoff.ForceField`
    object into a dictionary of int and str.

    Notes
    -----
    The value in the dictionary is
    temporarily for now just the xml representation of the force field.

    Parameters
    ----------
    force_field: openforcefield.typing.engines.smirnoff.ForceField
        The force field to serialize.
    Returns
    -------
    Dict[int, str]
        The serialised force field, where the keys are int indices, and
        the values are the xml of the serialized force field trees.
    """

    if not isinstance(force_field, ForceField):
        raise ValueError('{} is not a ForceField'.format(type(force_field)))

    file_buffers = tuple([BytesIO() for _ in force_field._XMLTrees])

    force_field.writeFile(file_buffers)

    return_dictionary = {}

    for index, file_buffer in enumerate(file_buffers):

        string_value = file_buffer.getvalue().decode()
        return_dictionary[index] = string_value

        file_buffer.close()

    return return_dictionary


def deserialize_force_field(force_field_dictionary):
    """A method for deserializing a force field which has been
    serialized as a dictionary by the `serialize_force_field` method.

    Notes
    -----
    The value in the dictionary is temporarily for now just the xml
    representation of the force field.

    Parameters
    ----------
    force_field_dictionary: Dict[int, str]
        The serialised force field, where each key of the dictionary is an int index,
        each value is an xml representation of the force field.

    Returns
    -------
    openforcefield.typing.engines.smirnoff.ForceField
        The deserialized force field.
    """

    if '@type' in force_field_dictionary:
        force_field_dictionary.pop('@type')

    file_buffers = [None] * len(force_field_dictionary)

    for index in force_field_dictionary:

        bytes_string = force_field_dictionary[index]

        if isinstance(bytes_string, str):
            bytes_string = bytes_string.encode('utf-8')

        file_buffers[index] = BytesIO(bytes_string)

    from openforcefield.typing.engines.smirnoff import ForceField

    force_field = ForceField(*file_buffers)
    return force_field


def serialize_enum(enum):

    if not isinstance(enum, Enum):
        raise ValueError('{} is not an Enum'.format(type(enum)))

    return {
        'value': enum.value
    }


def deserialize_enum(enum_dictionary):

    if '@type' not in enum_dictionary:

        raise ValueError('The serialized enum dictionary must include'
                         'which type the enum is.')

    if 'value' not in enum_dictionary:

        raise ValueError('The serialized enum dictionary must include'
                         'the enum value.')

    enum_type_string = enum_dictionary['@type']
    enum_value = enum_dictionary['value']

    enum_class = _type_string_to_object(enum_type_string)

    if not issubclass(enum_class, Enum):
        raise ValueError('<{}> is not an Enum'.format(enum_class))

    return enum_class(enum_value)


class TypedJSONEncoder(json.JSONEncoder):

    _natively_supported_types = [
        dict, list, tuple, str, int, float, bool
    ]

    _custom_supported_types = {
        Enum: serialize_enum,
        unit.Quantity: serialize_quantity,
        ForceField: serialize_force_field
    }

    def default(self, value_to_serialize):

        if value_to_serialize is None:
            return None

        type_to_serialize = type(value_to_serialize)

        if type_to_serialize in TypedJSONEncoder._natively_supported_types:
            # If the value is a native type, then let the default serializer
            # handle it.
            return super(TypedJSONEncoder, self).default(value_to_serialize)

        # Otherwise, we need to add a @type attribute to it.
        qualified_name = type_to_serialize.__qualname__
        qualified_name = qualified_name.replace('.', '->')

        type_tag = '{}.{}'.format(type_to_serialize.__module__, qualified_name)
        serializable_dictionary = {}

        custom_encoder = None

        for encoder_type in TypedJSONEncoder._custom_supported_types:

            if not issubclass(type_to_serialize, encoder_type):
                continue

            custom_encoder = TypedJSONEncoder._custom_supported_types[encoder_type]
            break

        if custom_encoder is not None:

            try:
                serializable_dictionary = custom_encoder(value_to_serialize)

            except Exception as e:

                raise ValueError('{} ({}) could not be serialized '
                                 'using a specialized custom encoder: {}'.format(value_to_serialize,
                                                                                 type_to_serialize, e))

        elif hasattr(value_to_serialize, '__getstate__'):

            try:
                serializable_dictionary = value_to_serialize.__getstate__()

            except Exception as e:

                raise ValueError('{} ({}) could not be serialized '
                                 'using its __getstate__ method: {}'.format(value_to_serialize,
                                                                            type_to_serialize, e))

        else:

            raise ValueError('Objects of type {} are not serializable, please either'
                             'add a __getstate__ method, or add the object to the list'
                             'of custom supported types.'.format(type_to_serialize))

        serializable_dictionary['@type'] = type_tag
        return serializable_dictionary


class TypedJSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    _custom_supported_types = {
        Enum: deserialize_enum,
        unit.Quantity: deserialize_quantity,
        ForceField: deserialize_force_field
    }

    @staticmethod
    def object_hook(object_dictionary):

        if '@type' not in object_dictionary:
            return object_dictionary

        type_string = object_dictionary['@type']
        class_type = _type_string_to_object(type_string)

        deserialized_object = None

        custom_decoder = None

        for decoder_type in TypedJSONDecoder._custom_supported_types:

            if not issubclass(class_type, decoder_type):
                continue

            custom_decoder = TypedJSONDecoder._custom_supported_types[decoder_type]
            break

        if custom_decoder is not None:

            try:
                deserialized_object = custom_decoder(object_dictionary)

            except Exception as e:

                raise ValueError('{} ({}) could not be deserialized '
                                 'using a specialized custom decoder: {}'.format(object_dictionary,
                                                                                 type(class_type), e))

        elif hasattr(class_type, '__setstate__'):

            try:

                class_init_signature = inspect.signature(class_type)

                for parameter in class_init_signature.parameters.values():

                    if (parameter.default != inspect.Parameter.empty or
                        parameter.kind == inspect.Parameter.VAR_KEYWORD):

                        continue

                    raise ValueError('Cannot deserialize objects which have'
                                     'non-optional arguments {} in the constructor: {}.'.format(parameter.name,
                                                                                                class_type))

                deserialized_object = class_type()
                deserialized_object.__setstate__(object_dictionary)

            except Exception as e:

                raise ValueError('{} ({}) could not be deserialized '
                                 'using its __setstate__ method: {}'.format(object_dictionary,
                                                                            type(class_type), e))

        else:

            raise ValueError('Objects of type {} are not deserializable, please either'
                             'add a __setstate__ method, or add the object to the list'
                             'of custom supported types.'.format(type(class_type)))

        return deserialized_object


class NewTypedBaseModel(BaseModel):

    def json(self, *, include=None, exclude=None, by_alias=False, encoder=TypedJSONEncoder,**dumps_kwargs,):

        assert include is None and exclude is None and by_alias is False
        json_string = json.dumps(self, cls=encoder or self._json_encoder, **dumps_kwargs,)

        return json_string

    @classmethod
    def parse_raw(cls, byte_string, *, content_type=None, encoding='utf8', proto=None, allow_pickle=False,):

        return_object_state = json.loads(byte_string, encoding=encoding, cls=TypedJSONDecoder).__getstate__()

        if '@type' in return_object_state:
            return_object_state.pop('@type')

        return_object = cls.parse_obj(return_object_state)
        return return_object


class TypedBaseModel(BaseModel):

    module_metadata: str = ''
    type_metadata: str = ''

    @classmethod
    def __get_validators__(cls):
        # yield dict_validator
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, cls):
            return value
        else:
            class_type = getattr(sys.modules[value['module_metadata']], value['type_metadata'])
            return class_type(**dict_validator(value))

    def __init__(self, **data):
        super().__init__(**data)

        self.module_metadata = type(self).__module__
        self.type_metadata = type(self).__name__


class PolymorphicEncoder(json.JSONEncoder):

    def default(self, obj):

        serializable_object = {}

        value_to_serialize = obj
        type_to_serialize = type(obj)

        from simtk import unit

        if isinstance(obj, PolymorphicDataType):

            value_to_serialize = obj.value
            type_to_serialize = obj.type

        if isinstance(value_to_serialize, BaseModel):

            serializable_object = value_to_serialize.dict()

        elif isinstance(value_to_serialize, Enum):

            serializable_object = value_to_serialize.value

        elif isinstance(value_to_serialize, unit.Quantity):

            serializable_object = serialize_quantity(value_to_serialize)

        else:

            try:

                json.dumps(value_to_serialize)  # Check if the value is natively serializable.
                serializable_object = value_to_serialize

            except TypeError as e:

                if isinstance(value_to_serialize, list):

                    serializable_object = []
                    list_object_type = None

                    for value_in_list in value_to_serialize:

                        if isinstance(value_in_list, PolymorphicDataType):
                            raise ValueError("Nested lists of PolymorphicDataType's are not serializable.")

                        if list_object_type is not None and type(value_in_list) != list_object_type:
                            raise ValueError("Nested lists of PolymorphicDataType's are not serializable.")

                        serializable_object.append(self.default(value_in_list))
                        list_object_type = type(value_in_list)

                else:

                    serializable_object = value_to_serialize.__getstate__()

        qualified_name = type_to_serialize.__qualname__
        qualified_name = qualified_name.replace('.', '->')

        return_value = {
            '@type': '{}.{}'.format(type_to_serialize.__module__,
                                    qualified_name),

            'value': serializable_object
        }

        return return_value


class PolymorphicDataType:
    """A helper object wrap values which have a type unknown
    ahead of time.
    """

    def __init__(self, value):
        """Creates a new PolymorphicDataType object.

        Parameters
        ----------
        value: Any
            The value to wrap.
        """

        self.value = value
        self.type = type(value)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """A pydantic helper method for deserializing the object.
        """
        if isinstance(value, PolymorphicDataType):
            return value

        return PolymorphicDataType.deserialize(value)

    @staticmethod
    def deserialize(json_dictionary):
        """A method to deserialize the polymorphic value from its
        JSON dictionary representation.

        Parameters
        ----------
        json_dictionary: Dict[str, Any]
            The JSON dictionary to deserialize.

        Returns
        -------
        Any
            The deserialized object.
        """

        if '@type' not in json_dictionary or 'value' not in json_dictionary:
            raise ValidationError('{} is not a valid PolymorphicDataType'.format(json_dictionary))

        type_string = json_dictionary['@type']
        last_period_index = type_string.rfind('.')

        if last_period_index < 0:
            raise ValidationError('{} is not a valid PolymorphicDataType'.format(json_dictionary))

        module_name = type_string[0:last_period_index]
        module = importlib.import_module(module_name)

        class_name = type_string[last_period_index + 1:]

        if class_name == 'NoneType':
            return PolymorphicDataType(None)

        class_name_split = class_name.split('->')
        class_object = module

        while len(class_name_split) > 0:

            class_name_current = class_name_split.pop(0)
            class_object = getattr(class_object, class_name_current)

        value_object = json_dictionary['value']

        parsed_object = None

        from simtk import unit

        if issubclass(class_object, BaseModel):

            parsed_object = class_object.parse_obj(value_object)

        elif issubclass(class_object, Enum):

            parsed_object = class_object(value_object)

        elif issubclass(class_object, unit.Quantity):

            parsed_object = deserialize_quantity(value_object)

        elif issubclass(class_object, list):

            parsed_object = []

            for list_item in value_object:
                parsed_object.append(PolymorphicDataType.deserialize(list_item).value)

        else:

            parsed_object = value_object

            if hasattr(class_object, 'validate'):
                parsed_object = class_object.validate(parsed_object)

            elif not isinstance(parsed_object, class_object):

                created_object = class_object()
                created_object.__setstate__(parsed_object)

                parsed_object = created_object

        return PolymorphicDataType(parsed_object)

    @staticmethod
    def serialize(value_to_serialize):
        """A method to serialize a polymorphic value, along with its
        type in the form of a JSON dictionary.

        Parameters
        ----------
        value_to_serialize: PolymorphicDataType
            The value to serialize.

        Returns
        -------
        str
            The JSON serialized value.
        """

        # value_json = ''
        #
        # if isinstance(value_to_serialize.value, BaseModel):
        #
        #     value_json = value_to_serialize.value.json()
        #
        # elif isinstance(value_to_serialize.value, Enum):
        #
        #     value_json = value_to_serialize.value.value
        #
        # else:
        #     try:
        #         value_json = json.dumps(value_to_serialize.value)
        #     except TypeError as e:
        #         value_json = json.dumps(value_to_serialize.value.__getstate__())
        #
        # qualified_name = value_to_serialize.type.__qualname__
        # qualified_name = qualified_name.replace('.', '->')
        #
        # return_value = {
        #     '@type': '{}.{}'.format(value_to_serialize.type.__module__,
        #                             qualified_name),
        #
        #     'value': value_json
        # }

        encoder = PolymorphicEncoder()

        return_value = encoder.default(value_to_serialize)
        return return_value
