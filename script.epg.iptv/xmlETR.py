# -*- coding: utf-8 -*-
import string
import sys
import re
import warnings
from xml.etree.ElementTree import ElementTree
def _encode(s, encoding):
    try:
        return s.encode(encoding)
    except AttributeError:
        return s 
def _escape_attrib(text, encoding=None, replace=string.replace):
    try:
        if encoding:
            try:
                text = _encode(text, encoding)
            except UnicodeError:
                return _encode_entity(text)
        text = replace(text, "&", "&amp;")
        text = replace(text, "'", "&apos;")
        text = replace(text, "\"", "&quot;")
        text = replace(text, "<", "&lt;")
        text = replace(text, ">", "&gt;")
        return text
    except (TypeError, AttributeError):
        _raise_serialization_error(text)
def Comment(text=None):
    element = Element(Comment)
    element.text = text
    return element
def ProcessingInstruction(target, text=None):
    element = Element(ProcessingInstruction)
    element.text = target
    if text:
        element.text = element.text + " " + text
    return element
class QName(object):
    def __init__(self, text_or_uri, tag=None):
        if tag:
            text_or_uri = "{%s}%s" % (text_or_uri, tag)
        self.text = text_or_uri
    def __str__(self):
        return self.text
    def __hash__(self):
        return hash(self.text)
    def __cmp__(self, other):
        if isinstance(other, QName):
            return cmp(self.text, other.text)
        return cmp(self.text, other)
def qnamespaces(elem, encoding, default_namespace=None):
    qnames = {None: None}
    namespaces = {}
    if default_namespace:
        namespaces[default_namespace] = ""
    def encode(text):
        return text.encode(encoding)
    def add_qname(qname):
        try:
            if qname[:1] == "{":
                uri, tag = qname[1:].rsplit("}", 1)
                prefix = namespaces.get(uri)
                if prefix is None:
                    prefix = _namespace_map.get(uri)
                    if prefix is None:
                        prefix = "ns%d" % len(namespaces)
                    if prefix != "xml":
                        namespaces[uri] = prefix
                if prefix:
                    qnames[qname] = encode("%s:%s" % (prefix, tag))
                else:
                    qnames[qname] = encode(tag)
            else:
                if default_namespace:
                    raise ValueError(
                        "cannot use non-qualified names with "
                        "default_namespace option"
                        )
                qnames[qname] = encode(qname)
        except TypeError:
            _raise_serialization_error(qname)
    try:
        iterate = elem.iter
    except AttributeError:
        iterate = elem.getiterator
    for elem in iterate():
        tag = elem.tag
        if isinstance(tag, QName):
            if tag.text not in qnames:
                add_qname(tag.text)
        elif isinstance(tag, basestring):
            if tag not in qnames:
                add_qname(tag)
        elif tag is not None and tag is not Comment and tag is not PI:
            _raise_serialization_error(tag)
        for key, value in elem.items():
            if isinstance(key, QName):
                key = key.text
            if key not in qnames:
                add_qname(key)
            if isinstance(value, QName) and value.text not in qnames:
                add_qname(value.text)
        text = elem.text
        if isinstance(text, QName) and text.text not in qnames:
            add_qname(text.text)
    return qnames, namespaces
def _escape_cdata(text, encoding=None, replace=string.replace):
    try:
        if encoding:
            try:
                text = _encode(text, encoding)
            except UnicodeError:
                return _encode_entity(text)
        text = replace(text, "&", "&amp;")
        text = replace(text, "<", "&lt;")
        text = replace(text, ">", "&gt;")
        return text
    except (TypeError, AttributeError):
        _raise_serialization_error(text)
def serialize_xml(write, elem, encoding, qnames, namespaces):
    tag = elem.tag
    text = elem.text
    if tag is Comment:
        write("<!--%s-->" % _encode(text, encoding))
    elif tag is ProcessingInstruction:
        write("<?%s?>" % _encode(text, encoding))
    else:
        tag = qnames[tag]
        if tag is None:
            if text:
                write(_escape_cdata(text, encoding))
            for e in elem:
                _serialize_xml(write, e, encoding, qnames, None)
        else:
            write("<" + tag)
            items = elem.items()
            if items or namespaces:
                if namespaces:
                    for v, k in sorted(namespaces.items(),
                                       key=lambda x: x[1]):
                        if k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k.encode(encoding),
                            _escape_attrib(v, encoding)
                            ))
                for k, v in sorted(items):
                    if isinstance(k, QName):
                        k = k.text
                    if isinstance(v, QName):
                        v = qnames[v.text]
                    else:
                        v = _escape_attrib(v, encoding)
                    write(" %s=\"%s\"" % (qnames[k], v))
            if text or len(elem):
                write(">")
                if text:
                    write(_escape_cdata(text, encoding))
                for e in elem:
                    serialize_xml(write, e, encoding, qnames, None)
                write("</" + tag + ">"+"\n")
            else:
                write(" />")
    if elem.tail:
        write(_escape_cdata(elem.tail, encoding))
class ETR (ElementTree):
 def write(self, file_or_filename,
              encoding=None,
              default_namespace=None):
        file = open(file_or_filename, "wb")
        write = file.write
        encoding = "utf-8"
        write("<?xml version='1.0' encoding='%s'?>\n" % encoding)
        qnames, namespaces = qnamespaces(self._root, encoding, default_namespace)
        serialize_xml(write, self._root, encoding, qnames, namespaces)
        if file_or_filename is not file:
            file.close()
