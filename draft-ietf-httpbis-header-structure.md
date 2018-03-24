---
title: Structured Headers for HTTP
docname: draft-ietf-httpbis-header-structure-latest
date: {DATE}
category: std
ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft

stand_alone: yes
pi:
  toc: yes
  tocindent: yes
  sortrefs: yes
  symrefs: yes
  strict: yes
  compact: yes
  comments: yes
  inline: yes
  tocdepth: 2


author:
 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization: Fastly
    email: mnot@mnot.net
    uri: https://www.mnot.net/
 -
    ins: P-H. Kamp
    name: Poul-Henning Kamp
    organization: The Varnish Cache Project
    email: phk@varnish-cache.org

normative:

informative:
  IEEE754:
    target: http://ieeexplore.ieee.org/document/4610935/
    title: IEEE Standard for Floating-Point Arithmetic
    author:
    -
      organization: IEEE
    date: 2008-08
    seriesinfo:
      IEEE: 754-2008
      DOI:  10.1109/IEEESTD.2008.4610935
      ISBN: 978-0-7381-5752-8
    annotation: See also <http://grouper.ieee.org/groups/754/>.


--- abstract

This document describes a set of data types and parsing algorithms associated with them that are intended to make it easier and safer to define and handle HTTP header fields. It is intended for use by new specifications of HTTP header fields as well as revisions of existing header field specifications when doing so does not cause interoperability issues.


--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.github.io/>; source code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/header-structure>.

--- middle

# Introduction

Specifying the syntax of new HTTP header fields is an onerous task; even with the guidance in {{?RFC7231}}, Section 8.3.1, there are many decisions -- and pitfalls -- for a prospective HTTP header field author.

Once a header field is defined, bespoke parsers for it often need to be written, because each header has slightly different handling of what looks like common syntax.

This document introduces structured HTTP header field values (hereafter, Structured Headers) to address these problems. Structured Headers define a generic, abstract model for header field values, along with a concrete serialisation for expressing that model in textual HTTP headers, as used by HTTP/1 {{?RFC7230}} and HTTP/2 {{?RFC7540}}.

HTTP headers that are defined as Structured Headers use the types defined in this specification to define their syntax and basic handling rules, thereby simplifying both their definition and parsing.

Additionally, future versions of HTTP can define alternative serialisations of the abstract model of Structured Headers, allowing headers that use it to be transmitted more efficiently without being redefined.

Note that it is not a goal of this document to redefine the syntax of existing HTTP headers; the mechanisms described herein are only intended to be used with headers that explicitly opt into them.

To specify a header field that uses Structured Headers, see {{specify}}.

{{types}} defines a number of abstract data types that can be used in Structured Headers. Dictionaries and lists are only usable at the "top" level, while the remaining types can be specified appear at the top level or inside those structures.

Those abstract types can be serialised into textual headers -- such as those used in HTTP/1 and HTTP/2 -- using the algorithms described in {{text}}.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as
described in BCP 14 {{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals, as
shown here.

This document uses the Augmented Backus-Naur Form (ABNF) notation of {{!RFC5234}}, including the DIGIT, ALPHA and DQUOTE rules from that document. It also includes the OWS rule from {{!RFC7230}}.


# Specifying Structured Headers {#specify}

A HTTP header that uses Structured Headers need to be defined to do so explicitly; recipients and generators need to know that the requirements of this document are in effect. The simplest way to do that is by referencing this document in its definition.

The field's definition will also need to specify the field-value's allowed syntax, in terms of the types described in {{types}}, along with their associated semantics.

A header field definition cannot relax or otherwise modify the requirements of this specification; doing so would preclude handling by generic software.

However, header field authors are encouraged to clearly state additional constraints upon the syntax, as well as the consequences when those constraints are violated. Such additional constraints could include additional structure (e.g., a list of URLs {{?RFC3986}} inside a string) that cannot be expressed using the primitives defined here.

For example:

~~~ example
# FooExample Header

The FooExample HTTP header field conveys a list of integers about how
much Foo the sender has.

FooExample is a Structured header [RFCxxxx]. Its value MUST be a
dictionary ([RFCxxxx], Section Y.Y).

The dictionary MUST contain:

* Exactly one member whose key is "foo", and whose value is an
  integer ([RFCxxxx], Section Y.Y), indicating the number of foos in
  the message.
* Exactly one member whose key is "barUrls", and whose value is a
  string ([RFCxxxx], Section Y.Y), conveying the Bar URLs for the
  message. See below for processing requirements.

If the parsed header field does not contain both, it MUST be ignored.

"foo" MUST be between 0 and 10, inclusive; other values MUST be
ignored.

"barUrls" contains a space-separated list of URI-references
([RFC3986], Section 4.1):

   barURLs = URI-reference *( 1*SP URI-reference )

If a member of barURLs is not a valid URI-reference, it MUST be
ignored.

If a member of barURLs is a relative reference ([RFC3986],
Section 4.2), it MUST be resolved ([RFC3986], Section 5) before being
used.
~~~

Note that empty header field values are not allowed by the syntax, and therefore parsing for them will fail.


# Parsing Text into Structured Headers {#text}

When a receiving implementation parses textual HTTP header fields (e.g., in HTTP/1 or HTTP/2) that are known to be Structured Headers, it is important that care be taken, as there are a number of edge cases that can cause interoperability or even security problems. This section specifies the algorithm for doing so.

Given an ASCII string input_string that represents the chosen header's field-value, return the parsed header value.

1. Discard any leading OWS from input_string.
2. If the field-value is defined to be a dictionary, let output be the result of Parsing a Dictionary from Text ({{parse-dictionary}}).
3. If the field-value is defined to be a list, let output be the result of Parsing a List from Text ({{parse-list}}).
4. If the field-value is defined to be a parameterised list, let output be the result of Parsing a Parameterised List from Text ({{parse-param-list}}).
5. Otherwise, let output be the result of Parsing an Item from Text ({{parse-item}}).
6. Discard any leading OWS from input_string.
7. If input_string is not empty, fail parsing.
8. Otherwise, return output.

When generating input_string, parsers MUST combine all instances of the target header field into one comma-separated field-value, as per {{?RFC7230}}, Section 3.2.2; this assures that the header is processed correctly.

Note that in the case of lists, parameterised lists and dictionaries, this has the effect of coalescing all of the values for that field. However, for singular items, parsing will fail if more than instance of that header field is present.

If parsing fails, the entire header field's value MUST be discarded. This is intentionally strict, to improve interoperability and safety, and specifications referencing this document cannot loosen this requirement.

Note that this has the effect of discarding any header field with non-ASCII characters in input_string.


# Structured Header Data Types {#types}

This section defines the abstract value types that can be composed into Structured Headers, along with the textual HTTP serialisations of them.


## Dictionaries {#dictionary}

Dictionaries are unordered maps of key-value pairs, where the keys are identifiers ({{identifier}}) and the values are items ({{item}}). There can be from 1 to 1024 members, and keys are required to be unique.

In the textual HTTP serialisation, keys and values are separated by "=" (without whitespace), and key/value pairs are separated by a comma with optional whitespace. Duplicate keys MUST cause parsing to fail.

~~~ abnf
dictionary  = dict_member 0*1023( OWS "," OWS dict_member )
dict_member = identifier "=" item
~~~

For example, a header field whose value is defined as a dictionary could look like:

~~~ example
ExampleDictHeader: foo=1.23, en="Applepie", da=*w4ZibGV0w6ZydGUK*
~~~

Typically, a header field specification will define the semantics of individual keys, as well as whether their presence is required or optional. Recipients MUST ignore keys that are undefined or unknown, unless the header field's specification specifically disallows them.


### Parsing a Dictionary from Text {#parse-dictionary}

Given an ASCII string input_string, return a mapping of (identifier, item). input_string is modified to remove the parsed value.

1. Let dictionary be an empty, unordered mapping.
2. While input_string is not empty:
   1. Let this_key be the result of running Parse Identifier from Text ({{parse-identifier}}) with input_string.
   2. If dictionary already contains this_key, fail parsing.
   3. Consume a "=" from input_string; if none is present, fail parsing.
   4. Let this_value be the result of running Parse Item from Text ({{parse-item}}) with input_string.
   5. Add key this_key with value this_value to dictionary.
   6. If dictionary has more than 1024 members, fail parsing.
   7. Discard any leading OWS from input_string.
   8. If input_string is empty, return dictionary.
   9. Consume a COMMA from input_string; if no comma is present, fail parsing.
   0. Discard any leading OWS from input_string.
   1. If input_string is empty, fail parsing.
3. No structured data has been found; fail parsing.


## Lists {#list}

Lists are arrays of items ({{item}}) with one to 1024 members.

In the textual HTTP serialisation, each member is separated by a comma and optional whitespace.

~~~ abnf
list = list_member 0*1023( OWS "," OWS list_member )
list_member = item
~~~

For example, a header field whose value is defined as a list of identifiers could look like:

~~~ example
ExampleIdListHeader: foo, bar, baz_45
~~~


### Parsing a List from Text {#parse-list}

Given an ASCII string input_string, return a list of items. input_string is modified to remove the parsed value.

1. Let items be an empty array.
2. While input_string is not empty:
   1. Let item be the result of running Parse Item from Text ({{parse-item}}) with input_string.
   2. Append item to items.
   3. If items has more than 1024 members, fail parsing.
   4. Discard any leading OWS from input_string.
   5. If input_string is empty, return items.
   6. Consume a COMMA from input_string; if no comma is present, fail parsing.
   7. Discard any leading OWS from input_string.
   8. If input_string is empty, fail parsing.
3. No structured data has been found; fail parsing.


## Parameterised Lists {#param}

Parameterised Lists are arrays of a parameterised identifiers with 1 to 256 members.

A parameterised identifier is an identifier ({{identifier}}) with up to 256 parameters, each parameter having a identifier and an optional value that is an item ({{item}}). Ordering between parameters is not significant, and duplicate parameters MUST cause parsing to fail.

In the textual HTTP serialisation, each parameterised identifier is separated by a comma and optional whitespace. Parameters are delimited from each other using semicolons (";"), and equals ("=") delimits the parameter name from its value.

~~~ abnf
param_list = param_id 0*255( OWS "," OWS param_id )
param_id   = identifier 0*256( OWS ";" OWS identifier [ "=" item ] )
~~~

For example,

~~~ example
ExampleParamListHeader: abc_123;a=1;b=2; c, def_456, ghi;q="19";r=foo
~~~


### Parsing a Parameterised List from Text {#parse-param-list}

Given an ASCII string input_string, return a list of parameterised identifiers. input_string is modified to remove the parsed value.

1. Let items be an empty array.
2. While input_string is not empty:
   1. Let item be the result of running Parse Parameterised Identifier from Text ({{parse-param-id}}) with input_string.
   2. Append item to items.
   3. If items has more than 256 members, fail parsing.
   4. Discard any leading OWS from input_string.
   5. If input_string is empty, return items.
   6. Consume a COMMA from input_string; if no comma is present, fail parsing.
   7. Discard any leading OWS from input_string.
   8. If input_string is empty, fail parsing.
3. No structured data has been found; fail parsing.


### Parsing a Parameterised Identifier from Text {#parse-param-id}

Given an ASCII string input_string, return a identifier with an mapping of parameters. input_string is modified to remove the parsed value.

1. Let primary_identifier be the result of Parsing a Identifier from Text ({{parse-identifier}}) from input_string.
2. Let parameters be an empty, unordered mapping.
3. In a loop:
   1. Discard any leading OWS from input_string.
   2. If the first character of input_string is not ";", exit the loop.
   3. Consume a ";" character from the beginning of input_string.
   4. Discard any leading OWS from input_string.
   5. let param_name be the result of Parsing a Identifier from Text ({{parse-identifier}}) from input_string.
   6. If param_name is already present in parameters, fail parsing.
   7. Let param_value be a null value.
   8. If the first character of input_string is "=":
      1. Consume the "=" character at the beginning of input_string.
      2. Let param_value be the result of Parsing an Item from Text ({{parse-item}}) from input_string.
   9. If parameters has more than 255 members, fail parsing.
   0. Insert (param_name, param_value) into parameters.
4. Return the tuple (primary_identifier, parameters).


## Items {#item}

An item is can be a integer ({{integer}}), float ({{float}}), string ({{string}}), identifier ({{identifier}}) or binary content ({{binary}}).

~~~ abnf
item = integer / float / string / identifier / binary
~~~


### Parsing an Item from Text {#parse-item}

Given an ASCII string input_string, return an item. input_string is modified to remove the parsed value.

1. Discard any leading OWS from input_string.
2. If the first character of input_string is a "-" or a DIGIT, process input_string as a number ({{parse-number}}) and return the result.
3. If the first character of input_string is a DQUOTE, process input_string as a string ({{parse-string}}) and return the result.
4. If the first character of input_string is "*", process input_string as binary content ({{parse-binary}}) and return the result.
5. If the first character of input_string is an lcalpha, process input_string as a identifier ({{parse-identifier}}) and return the result.
6. Otherwise, fail parsing.



## Integers {#integer}

Abstractly, integers have a range of −9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 inclusive (i.e., a 64-bit signed integer).

~~~ abnf
integer   = ["-"] 1*19DIGIT
~~~

Parsers that encounter an integer outside the range defined above MUST fail parsing. Therefore, the value "9223372036854775808" would be invalid. Likewise, values that do not conform to the ABNF above are invalid, and MUST fail parsing.

For example, a header whose value is defined as a integer could look like:

~~~ example
ExampleIntegerHeader: 42
~~~

### Parsing a Number from Text {#parse-number}

NOTE: This algorithm parses both Integers and Floats {{float}}, and returns the corresponding structure.

1. If the first character of input_string is not "-" or a DIGIT, fail parsing.
2. Let input_number be the result of consuming input_string up to (but not including) the first character that is not in DIGIT, "-", and ".".
3. If input_number contains ".", parse it as a floating point number and let output_number be the result.
4. Otherwise, parse input_number as an integer and let output_number be the result.
5. Return output_number.


## Floats {#float}

Abstractly, floats are integers with a fractional part. They have a maximum of fifteen digits available to be used in both of the parts, as reflected in the ABNF below; this allows them to be stored as IEEE 754 double precision numbers (binary64) ({{IEEE754}}).

The textual HTTP serialisation of floats allows a maximum of fifteen digits between the integer and fractional part, with at least one required on each side, along with an optional "-" indicating negative numbers.

~~~ abnf
float    = ["-"] (
             DIGIT "." 1*14DIGIT /
            2DIGIT "." 1*13DIGIT /
            3DIGIT "." 1*12DIGIT /
            4DIGIT "." 1*11DIGIT /
            5DIGIT "." 1*10DIGIT /
            6DIGIT "." 1*9DIGIT /
            7DIGIT "." 1*8DIGIT /
            8DIGIT "." 1*7DIGIT /
            9DIGIT "." 1*6DIGIT /
           10DIGIT "." 1*5DIGIT /
           11DIGIT "." 1*4DIGIT /
           12DIGIT "." 1*3DIGIT /
           13DIGIT "." 1*2DIGIT /
           14DIGIT "." 1DIGIT )
~~~

Values that do not conform to the ABNF above are invalid, and MUST fail parsing.

For example, a header whose value is defined as a float could look like:

~~~ example
ExampleFloatHeader: 4.5
~~~

See {{parse-number}} for the parsing algorithm for floats.


## Strings {#string}

Abstractly, strings are up to 1024 printable ASCII {{!RFC0020}} characters (i.e., the range 0x20 to 0x7E). Note that this excludes tabs, newlines, carriage returns, etc.

The textual HTTP serialisation of strings uses a backslash ("\\") to escape double quotes and backslashes in strings.

~~~ abnf
string    = DQUOTE 0*1024(char) DQUOTE
char      = unescaped / escape ( DQUOTE / "\" )
unescaped = %x20-21 / %x23-5B / %x5D-7E
escape    = "\"
~~~

For example, a header whose value is defined as a string could look like:

~~~ example
ExampleStringHeader: "hello world"
~~~

Note that strings only use DQUOTE as a delimiter; single quotes do not delimit strings. Furthermore, only DQUOTE and "\\" can be escaped; other sequences MUST cause parsing to fail.

Unicode is not directly supported in Structured Headers, because it causes a number of interoperability issues, and -- with few exceptions -- header values do not require it.

When it is necessary for a field value to convey non-ASCII string content, binary content ({{binary}}) SHOULD be specified, along with a character encoding (preferably, UTF-8).


### Parsing a String from Text {#parse-string}

Given an ASCII string input_string, return an unquoted string. input_string is modified to remove the parsed value.

1. Let output_string be an empty string.
2. If the first character of input_string is not DQUOTE, fail parsing.
3. Discard the first character of input_string.
4. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is a backslash ("\\"):
      1. If input_string is now empty, fail parsing.
      2. Else:
         1. Let next_char be the result of removing the first character of input_string.
         2. If next_char is not DQUOTE or "\\", fail parsing.
         3. Append next_char to output_string.
   3. Else, if char is DQUOTE, return output_string.
   4. Else, append char to output_string.
   5. If output_string contains more than 1024 characters, fail parsing.
6. Otherwise, fail parsing.


## Identifiers {#identifier}

Identifiers are short (up to 256 characters) textual identifiers; their abstract model is identical to their expression in the textual HTTP serialisation.

~~~ abnf
identifier = lcalpha 0*255( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
lcalpha    = %x61-7A ; a-z
~~~

Note that identifiers can only contain lowercase letters.

For example, a header whose value is defined as a identifier could look like:

~~~ example
ExampleIdHeader: foo/bar
~~~


### Parsing a Identifier from Text {#parse-identifier}

Given an ASCII string input_string, return a identifier. input_string is modified to remove the parsed value.

1. If the first character of input_string is not lcalpha, fail parsing.
2. Let output_string be an empty string.
3. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is not one of lcalpha, DIGIT, "_", "-", "*" or "/":
      1. Prepend char to input_string.
      2. Return output_string.
   3. Append char to output_string.
   1. If output_string contains more than 256 characters, fail parsing.
4. Return output_string.


## Binary Content {#binary}

Arbitrary binary content up to 16384 bytes in size can be conveyed in Structured Headers.

The textual HTTP serialisation encodes the data using Base 64 Encoding {{!RFC4648}}, Section 4, and surrounds it with a pair of asterisks ("*") to delimit from other content.

The encoded data is required to be padded with "=", as per {{!RFC4648}}, Section 3.2. It is
RECOMMENDED that parsers reject encoded data that is not properly padded, although this might
not be possible with some base64 implementations.

Likewise, encoded data is required to have pad bits set to zero, as per {{!RFC4648}}, Section 3.5.
It is RECOMMENDED that parsers fail on encoded data that has non-zero pad bits, although this might
not be possible with some base64 implementations.

This specification does not relax the requirements in {{!RFC4648}}, Section 3.1 and 3.3; therefore, parsers MUST fail on characters outside the base64 alphabet, and on line feeds in encoded data.

~~~ abnf
binary = "*" 0*21846(base64) "*"
base64 = ALPHA / DIGIT / "+" / "/" / "="
~~~

For example, a header whose value is defined as binary content could look like:

~~~ example
ExampleBinaryHeader: *cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==*
~~~


### Parsing Binary Content from Text {#parse-binary}

Given an ASCII string input_string, return binary content. input_string is modified to remove the parsed value.

1. If the first character of input_string is not "\*", fail parsing.
2. Discard the first character of input_string.
3. Let b64_content be the result of removing content of input_string up to but not including the first instance of the character "\*". If there is not a "\*" character before the end of input_string, fail parsing.
4. Consume the "\*" character at the beginning of input_string.
5. If b64_content is has more than 21846 characters, fail parsing.
6. Let binary_content be the result of Base 64 Decoding {{!RFC4648}} b64_content, synthesising padding if necessary (note the requirements about recipient behaviour in {{binary}}).
7. Return binary_content.




# IANA Considerations

This draft has no actions for IANA.

# Security Considerations

TBD


--- back



# Changes

## Since draft-ietf-httpbis-header-structure-03

* Strengthen language around failure handling.


## Since draft-ietf-httpbis-header-structure-02

* Split Numbers into Integers and Floats.
* Define number parsing.
* Tighten up binary parsing and give it an explicit end delimiter.
* Clarify that mappings are unordered.
* Allow zero-length strings.
* Improve string parsing algorithm.
* Improve limits in algorithms.
* Require parsers to combine header fields before processing.
* Throw an error on trailing garbage.

## Since draft-ietf-httpbis-header-structure-01

* Replaced with draft-nottingham-structured-headers.

## Since draft-ietf-httpbis-header-structure-00

* Added signed 64bit integer type.
* Drop UTF8, and settle on BCP137 ::EmbeddedUnicodeChar for h1-unicode-string.
* Change h1_blob delimiter to ":" since "'" is valid t_char
