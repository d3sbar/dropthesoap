from dropthesoap.schema import xs
from dropthesoap.schema.model import Namespace

from .helpers import validate, tostring


def test_simple_schema():
    AddRequest = xs.element('AddRequest')(xs.cts(
        xs.element('x', xs.string),
        xs.element('y', xs.int)))

    AddResponse = xs.element('AddResponse', xs.int)

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        AddRequest,
        AddResponse
    )

    assert validate(schema, AddRequest.instance(x='10', y='15'))
    assert validate(schema, AddResponse.instance(15))

    obj = schema.fromstring(tostring(AddRequest.instance(x='11', y='12')))
    assert obj.x == '11'
    assert obj.y == 12

    obj = schema.fromstring(tostring(AddResponse.instance(30)))
    assert obj == 30


def test_zero_min_occurs():
    Request = xs.element('Request')(xs.cts(
        xs.element('x', xs.string, minOccurs=0),
        xs.element('y', xs.int)))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance(y=15)
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.x == None
    assert obj.y == 15


def test_max_occurs_grater_then_one():
    Request = xs.element('Request')(xs.cts(
        xs.element('x', xs.int, maxOccurs=xs.unbounded)))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance(x=[15, 22, 30])
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.x == [15, 22, 30]


def test_attributes():
    Request = xs.element('Request')(
        xs.complexType()(
            xs.sequence()(
                xs.element('x', xs.int)),
            xs.attribute('y', xs.int)))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance(x=15, y=20)
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.x == 15
    assert obj.y == 20


def test_enumeration():
    Request = xs.element('Request')(
        xs.simpleType()(
            xs.restriction(base=xs.string)(
                xs.enumeration('en'),
                xs.enumeration('ru'))))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance('en')
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj == 'en'
    assert Request.type.en == 'en'

    request = Request.instance('fr')
    assert not validate(schema, request)


def test_simple_content():
    Request = xs.element('Request')(
        xs.complexType()(
            xs.simpleContent()(
                xs.extension(xs.string)(
                    xs.attribute('lang', xs.string)))))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance(value='message', lang='en')
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.value == 'message'
    assert obj.lang == 'en'


def test_type_instances():
    Request = xs.element('Request')(xs.cts(
        xs.element('x', xs.string)))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.type.instance(x='message')
    real_request = request.create(Request)
    assert validate(schema, real_request)

    obj = schema.fromstring(tostring(real_request))
    assert obj.x == 'message'


    request = Request.type.instance()
    request.x = 'message'
    real_request = request.create(Request)
    assert validate(schema, real_request)

    obj = schema.fromstring(tostring(real_request))
    assert obj.x == 'message'


def test_none_values_should_be_wrapped_into_empty_element():
    schema = xs.schema(Namespace('http://boo', 'boo'))(
        xs.element('Request')(xs.cts(
            xs.element('foo', xs.string)
        ))
    )

    request = schema['Request'].instance(foo=None)
    assert validate(schema, request)
    assert '<boo:foo />' in tostring(request)


def test_dict_intances():
    schema = xs.schema(Namespace('http://boo', 'boo'))(
        xs.element('Request')(xs.cts(
            xs.element('foo')(xs.cts(
                xs.element('x', xs.string),
                xs.element('y', xs.int),
            ))
        ))
    )

    request = schema['Request'].instance(foo={'x':'boo', 'y':100})
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.foo.x == 'boo'
    assert obj.foo.y == 100


def test_type_aliases():
    schema = xs.schema(Namespace('http://boo', 'boo'))(
        xs.complexType(name='fooType')(
            xs.sequence()(
                xs.element('x', xs.string),
                xs.element('y', xs.int))),

        xs.element('Request')(xs.cts(
            xs.element('foo', 'fooType')))
    )

    request = schema['Request'].instance(foo={'x':'boo', 'y':100})
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.foo.x == 'boo'
    assert obj.foo.y == 100


def test_boolean():
    schema = xs.schema(Namespace('http://boo', 'boo'))(
        xs.element('Request')(xs.cts(
            xs.element('foo', xs.boolean)))
    )

    request = schema['Request'].instance(foo=True)
    assert validate(schema, request)
    obj = schema.fromstring(tostring(request))
    assert obj.foo == True

    request = schema['Request'].instance(foo=False)
    assert validate(schema, request)
    obj = schema.fromstring(tostring(request))
    assert obj.foo == False


def test_binary_data():
    schema = xs.schema(Namespace('http://boo', 'boo'))(
        xs.element('Request')(xs.cts(
            xs.element('foo', xs.hexBinary),
            xs.element('boo', xs.base64Binary)))
    )

    data = '\x01\x02\x03'
    request = schema['Request'].instance(foo=data, boo=data)
    assert validate(schema, request)

    string_request = tostring(request)
    assert '010203' in string_request
    assert 'AQID' in string_request

    obj = schema.fromstring(string_request)
    assert obj.foo == data
    assert obj.boo == data


def test_dict_instantiation_for_aliased_types():
    schema = xs.schema(Namespace('http://boo', 'boo'))(
        xs.complexType('Point')(
            xs.attribute('x', xs.int),
            xs.attribute('y', xs.int)),

        xs.complexType('Vector')(
            xs.sequence()(
                xs.element('a', 'Point'),
                xs.element('b', 'Point'))),

        xs.element('Request')(xs.cts(
            xs.element('vector', 'Vector', minOccurs=0, maxOccurs=xs.unbounded))),
    )

    request = schema['Request'].instance(vector=[{'a':{'x':1, 'y':2}, 'b':{'x':3, 'y':4}}])
    assert validate(schema, request)
    obj = schema.fromstring(tostring(request))
    assert obj.vector[0].a.x == 1
    assert obj.vector[0].a.y == 2
    assert obj.vector[0].b.x == 3
    assert obj.vector[0].b.y == 4


def test_customize_optional():
    Request = xs.element('Request')(xs.cts(
        xs.element('x', xs.optional(xs.string)),
        xs.element('y', xs.int)))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance(y=15)
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.x == None
    assert obj.y == 15


def test_customize_array():
    Request = xs.element('Request')(xs.cts(
        xs.element('x', xs.array(xs.int))))

    schema = xs.schema(Namespace('http://boo', 'boo'))(
        Request,
    )

    request = Request.instance(x=[15, 22, 30])
    assert validate(schema, request)

    obj = schema.fromstring(tostring(request))
    assert obj.x == [15, 22, 30]
