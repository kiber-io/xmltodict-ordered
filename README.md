# xmltodict-ordered
This fork is designed to combine the latest version of xmltodict and [another fork](https://github.com/lindsay-stevens/xmltodict/commits/ordered-children-short-tags) that allows you to preserve the order of tags in xml in .parse and .unparse functions. All the laurels should be given to [lindsay-stevens](https://github.com/lindsay-stevens).

Example:
```python
filepath = 'old_ordered.xml'
xml: str = ''
with open(filepath, 'r') as f:
    xml = ''.join(f.readlines())
xmldict = xmltodict.parse(xml_input=xml, ordered_mixed_children=True) # ordered_mixed_children - flag
xml = xmltodict.unparse(input_dict=xmldict, pretty=True, ordered_mixed_children=True) # ordered_mixed_children - flag
with open('new_ordered.xml', 'w') as f:
    f.write(xml)
```

# xmltodict
`xmltodict` is a Python module that makes working with XML feel like you are working with [JSON](http://docs.python.org/library/json.html), as in this ["spec"](http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html):

[![Build Status](https://app.travis-ci.com/martinblech/xmltodict.svg?branch=master)](https://app.travis-ci.com/martinblech/xmltodict)

```python
>>> print(json.dumps(xmltodict.parse("""
...  <mydocument has="an attribute">
...    <and>
...      <many>elements</many>
...      <many>more elements</many>
...    </and>
...    <plus a="complex">
...      element as well
...    </plus>
...  </mydocument>
...  """), indent=4))
{
    "mydocument": {
        "@has": "an attribute",
        "and": {
            "many": [
                "elements",
                "more elements"
            ]
        },
        "plus": {
            "@a": "complex",
            "#text": "element as well"
        }
    }
}
```

## Namespace support

By default, `xmltodict` does no XML namespace processing (it just treats namespace declarations as regular node attributes), but passing `process_namespaces=True` will make it expand namespaces for you:

```python
>>> xml = """
... <root xmlns="http://defaultns.com/"
...       xmlns:a="http://a.com/"
...       xmlns:b="http://b.com/">
...   <x>1</x>
...   <a:y>2</a:y>
...   <b:z>3</b:z>
... </root>
... """
>>> xmltodict.parse(xml, process_namespaces=True) == {
...     'http://defaultns.com/:root': {
...         'http://defaultns.com/:x': '1',
...         'http://a.com/:y': '2',
...         'http://b.com/:z': '3',
...     }
... }
True
```

It also lets you collapse certain namespaces to shorthand prefixes, or skip them altogether:

```python
>>> namespaces = {
...     'http://defaultns.com/': None, # skip this namespace
...     'http://a.com/': 'ns_a', # collapse "http://a.com/" -> "ns_a"
... }
>>> xmltodict.parse(xml, process_namespaces=True, namespaces=namespaces) == {
...     'root': {
...         'x': '1',
...         'ns_a:y': '2',
...         'http://b.com/:z': '3',
...     },
... }
True
```

## Streaming mode

`xmltodict` is very fast ([Expat](http://docs.python.org/library/pyexpat.html)-based) and has a streaming mode with a small memory footprint, suitable for big XML dumps like [Discogs](http://discogs.com/data/) or [Wikipedia](http://dumps.wikimedia.org/):

```python
>>> def handle_artist(_, artist):
...     print(artist['name'])
...     return True
>>>
>>> xmltodict.parse(GzipFile('discogs_artists.xml.gz'),
...     item_depth=2, item_callback=handle_artist)
A Perfect Circle
Fantômas
King Crimson
Chris Potter
...
```

It can also be used from the command line to pipe objects to a script like this:

```python
import sys, marshal
while True:
    _, article = marshal.load(sys.stdin)
    print(article['title'])
```

```sh
$ bunzip2 enwiki-pages-articles.xml.bz2 | xmltodict.py 2 | myscript.py
AccessibleComputing
Anarchism
AfghanistanHistory
AfghanistanGeography
AfghanistanPeople
AfghanistanCommunications
Autism
...
```

Or just cache the dicts so you don't have to parse that big XML file again. You do this only once:

```sh
$ bunzip2 enwiki-pages-articles.xml.bz2 | xmltodict.py 2 | gzip > enwiki.dicts.gz
```

And you reuse the dicts with every script that needs them:

```sh
$ gunzip enwiki.dicts.gz | script1.py
$ gunzip enwiki.dicts.gz | script2.py
...
```

## Roundtripping

You can also convert in the other direction, using the `unparse()` method:

```python
>>> mydict = {
...     'response': {
...             'status': 'good',
...             'last_updated': '2014-02-16T23:10:12Z',
...     }
... }
>>> print(unparse(mydict, pretty=True))
<?xml version="1.0" encoding="utf-8"?>
<response>
	<status>good</status>
	<last_updated>2014-02-16T23:10:12Z</last_updated>
</response>
```

Text values for nodes can be specified with the `cdata_key` key in the python dict, while node properties can be specified with the `attr_prefix` prefixed to the key name in the python dict. The default value for `attr_prefix` is `@` and the default value for `cdata_key` is `#text`.

```python
>>> import xmltodict
>>>
>>> mydict = {
...     'text': {
...         '@color':'red',
...         '@stroke':'2',
...         '#text':'This is a test'
...     }
... }
>>> print(xmltodict.unparse(mydict, pretty=True))
<?xml version="1.0" encoding="utf-8"?>
<text stroke="2" color="red">This is a test</text>
```

Lists that are specified under a key in a dictionary use the key as a tag for each item. But if a list does have a parent key, for example if a list exists inside another list, it does not have a tag to use and the items are converted to a string as shown in the example below.  To give tags to nested lists, use the `expand_iter` keyword argument to provide a tag as demonstrated below. Note that using `expand_iter` will break roundtripping.

```python
>>> mydict = {
...     "line": {
...         "points": [
...             [1, 5],
...             [2, 6],
...         ]
...     }
... }
>>> print(xmltodict.unparse(mydict, pretty=True))
<?xml version="1.0" encoding="utf-8"?>
<line>
        <points>[1, 5]</points>
        <points>[2, 6]</points>
</line>
>>> print(xmltodict.unparse(mydict, pretty=True, expand_iter="coord"))
<?xml version="1.0" encoding="utf-8"?>
<line>
        <points>
                <coord>1</coord>
                <coord>5</coord>
        </points>
        <points>
                <coord>2</coord>
                <coord>6</coord>
        </points>
</line>
```

## Ok, how do I get it?

### Using pypi

You just need to

```sh
$ pip install xmltodict
```

### Using conda

For installing `xmltodict` using Anaconda/Miniconda (*conda*) from the
[conda-forge channel][#xmltodict-conda] all you need to do is:

[#xmltodict-conda]: https://anaconda.org/conda-forge/xmltodict

```sh
$ conda install -c conda-forge xmltodict
```

### RPM-based distro (Fedora, RHEL, …)

There is an [official Fedora package for xmltodict](https://apps.fedoraproject.org/packages/python-xmltodict).

```sh
$ sudo yum install python-xmltodict
```

### Arch Linux

There is an [official Arch Linux package for xmltodict](https://www.archlinux.org/packages/community/any/python-xmltodict/).

```sh
$ sudo pacman -S python-xmltodict
```

### Debian-based distro (Debian, Ubuntu, …)

There is an [official Debian package for xmltodict](https://tracker.debian.org/pkg/python-xmltodict).

```sh
$ sudo apt install python-xmltodict
```

### FreeBSD

There is an [official FreeBSD port for xmltodict](https://svnweb.freebsd.org/ports/head/devel/py-xmltodict/).

```sh
$ pkg install py36-xmltodict
```

### openSUSE/SLE (SLE 15, Leap 15, Tumbleweed)

There is an [official openSUSE package for xmltodict](https://software.opensuse.org/package/python-xmltodict).

```sh
# Python2
$ zypper in python2-xmltodict

# Python3
$ zypper in python3-xmltodict
```
