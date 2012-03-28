from . import xs
from .model import Namespace

namespace = Namespace('http://schemas.xmlsoap.org/soap/envelope/', 'soap')

Header = xs.element('Header', minOccurs=0)(
    xs.complexType()(
        xs.sequence()(
            xs.any(minOccurs=0, maxOccurs=xs.unbounded))))

Body = xs.element('Body', minOccurs=0)(
    xs.complexType()(
        xs.sequence()(
            xs.any(minOccurs=0, maxOccurs=xs.unbounded))))

Envelope = xs.element('Envelope')(
    xs.complexType()(
        xs.sequence()(
            Header,
            Body)))

Fault = xs.element('Fault')(xs.cts(
    xs.element('faultcode', xs.string),
    xs.element('faultstring', xs.string),
    xs.element('faultactor', xs.string, minOccurs=0),
    xs.element('detail', xs.string, minOccurs=0)))

schema = xs.schema(namespace)(
    Envelope
)

schema.update_schema([Fault])
