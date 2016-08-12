ARIA
====

ARIA is a platform and a set of tools for building TOSCA-based products, such as orchestrators.
Its features can be accessed via a well-documented Python API, as well as a language-agnostic
RESTful API that can be deployed as a microservice.

On its own, ARIA it provides built-in tools for blueprint validation and for creating ready-to-run
deployment plans. 

ARIA adheres strictly and meticulously to the
[TOSCA Simple Profile v1.0 specification](http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/csprd02/TOSCA-Simple-Profile-YAML-v1.0-csprd02.html),
providing state-of-the-art validation at seven different levels:

0. Platform errors. E.g. network, hardware, of even an internal bug in ARIA (let us know,
   please!).
1. Syntax and format errors. E.g. non-compliant YAML, XML, JSON.
2. Field validation. E.g. assigning a string where an integer is expected, using a list
   instead of a dict.
3. Relationships between fields within a type. This is "grammar" as it applies to rules for
   setting the values of fields in relation to each other.
4. Relationships between types. E.g. referring to an unknown type, causing a type inheritance
   loop. 
5. Topology. These errors happen if requirements and capabilities cannot be matched in order
   to assemble a valid topology.
6. External dependencies. These errors happen if requirement/capability matching fails due to
   external resources missing, e.g. the lack of a valid virtual machine, API credentials, etc. 

Validation errors include a plain English message and when relevant the exact location (file,
row, column) of the data the caused the error.

The ARIA API documentation always links to the relevant section of the specification, and
likewise we provide an annotated version of the specification that links back to the API
documentation.


Quick Start
-----------

You need Python v2.7. Use a [virtualenv](https://virtualenv.pypa.io/en/stable/):

	pip install virtualenv
	virtualenv env
	. env/bin/activate
	make aria-requirements

Now create a deployment plan from a TOSCA blueprint:

	./aria blueprints/tosca/node-cellar.yaml


`aria.parsing`
---------------

The ARIA parser's generates a representation of TOSCA profiles in Python, such that they
can be validated, consumed, or manipulated.

Importantly, it keeps the original TOSCA data intact, such that modifications can be
written back to files. This includes keeping all the original comments in the YAML
file in their right places.

It is furthermore possible to use ARIA in order to generate a complete TOSCA profile
programmatically, in Python, and then write it to files. The same technique can be
used to convert from one DSL (parse it) to another (write it).

The parser works in three phases, represented by packages and classes in the API:

* `aria.loading`: Loaders are used to read the TOSCA data, usually as text.
  For example UriTextLoader will load text from URIs (including files).
* `aria.reading`: Readers convert data from the loaders into agnostic raw
  data. For example, YamlReader converts YAML text into Python dicts, lists, and
  primitives.
* `aria.presentation`: Presenters wrap the agnostic raw data in a nice
  Python facade (a "presentation") that makes it much easier to work with the data,
  including utilities for validation, querying, etc. Note that presenters are
  _wrappers_: the agnostic raw data is always maintained intact, and can always be
  accessed directly or written back to files.

The term "agnostic raw data" (ARD?) appears often in the documentation. It denotes
data structures comprising _only_ Python dicts, lists, and primitives, such that
they can always be converted to and from language-agnostic formats such as YAML,
JSON, and XML. A considerable effort has been made to conserve the agnostic raw
data at all times. Thus, though ARIA makes good use of the dynamic power of Python,
you will _always_ be able to use ARIA with other systems.


Consumers
---------

ARIA also comes with various "consumers" that do things with presentations. Consumers
can be generic, or can be designed to work only with specific kinds of presentations.

Though you can simply make use of presentation without using the ARIA consumer API,
the advantage of using it is that you may benefit from other tools that make use of
the API.

With the CLI tool, just include the name of the consumer after the blueprint.

The following consumers are built-in and useful for seeing ARIA at work at different
phases:

* `yaml`: emits a combined, validated, and normalized YAML representation of the
   blueprint.
* `presentation`: emits a colorized textual representation of the Python presentation
   classes wrapping the blueprint. 
* `template`: emits a colorized textual representation of the complete topology
   template derived from the validated blueprint. This includes all the node templates,
   with their requirements satisfied at the level of relating to other node templates.
* `plan`: emits a colorized textual representation of a deployment plan instantiated
   from the deployment template. Here the node templates are each used to create one or
   more nodes, with the appropriate relationships between them. Note that every time you
   run this consumer, you will get a different set of node IDs.

### Generator (extension)

This converts the blueprint into Python code: a bunch of Python classes representing
the blueprint. Thus, node types become classes, the instances being nodes, interfaces
can be turned into methods, and these are connected to each other via special
relationship classes. You can use these classes directly in your product, allowing
a quick and easy way to move from a TOSCA blueprint to executable code.

Note that the generator is entirely optional: it is very much possible to consume
the deployment plan without converting it into Python code.


CLI Tool
--------

Though ARIA is fully exposed as an API, it also comes with a CLI tool to allow you to
work from the shell:

	aria blueprints/tosca/node-cellar.yaml plan

The tool loads YAML files and runs consumers on them. It can be useful for quickly
validating a blueprint.

If other consumers are in the Python path, it can run them, too: it can thus serve as
a useful entry point for complex TOSCA-based tools, such as orchestractors, graphical
representers, etc.

REST Tool
---------

The ARIA REST tool starts a RESTful HTTP server that can do basic validation over the
wire:

    aria-rest

With the server started, you can hit a few endpoints:

    curl http://localhost:8080/validate/blueprints/tosca/simple-blueprint.yaml

You will get a JSON response with a list of validation issues. You can also POST a
blueprint over the wire:

    curl --data-binary @blueprints/tosca/simple-blueprint.yaml http://localhost:8080/validate/
