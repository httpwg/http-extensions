---
title: Structured Headers for HTTP
docname: draft-ietf-httpbis-header-structure-latest
date: 2017
category: std
ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft

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
    target: http://grouper.ieee.org/groups/754/
    title: IEEE Standard for Floating-Point Arithmetic
    author:
    -
      organization: IEEE
    date: 2008


--- abstract

This document describes Structured Headers, a way of simplifying HTTP header field definition and parsing. It is intended for use by new HTTP header fields.


--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

*RFC EDITOR: please remove this section before publication*

Working Group information can be found at <https://httpwg.github.io/>; source code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/header-structure>.

--- middle

# Introduction

Specifying the syntax of new HTTP header fields is an onerous task; even with the guidance in {{?RFC7231}}, Section 8.3.1, there are many decisions -- and pitfalls -- for a prospective HTTP header field author.

Likewise, bespoke parsers often need to be written for specific HTTP headers, because each has slightly different handling of what looks like common syntax.

This document introduces structured HTTP header field values (hereafter, Structured Headers) to address these problems. Structured Headers define a generic, abstract model for data, along with a concrete serialisation for expressing that model in textual HTTP headers, as used by HTTP/1 {{?RFC7230}} and HTTP/2 {{?RFC7540}}.

HTTP headers that are defined as Structured Headers use the types defined in this specification to define their syntax and basic handling rules, thereby simplifying both their definition and parsing.

Additionally, future versions of HTTP can define alternative serialisations of the abstract model of Structured Headers, allowing headers that use it to be transmitted more efficiently without being redefined.

Note that it is not a goal of this document to redefine the syntax of existing HTTP headers; the mechanisms described herein are only intended to be used with headers that explicitly opt into them.

To specify a header field that uses Structured Headers, see {{specify}}.

{{types}} defines a number of abstract data types that can be used in Structured Headers, of which only three are allowed at the "top" level: lists, dictionaries, or items.

Those abstract types can be serialised into textual headers -- such as those used in HTTP/1 and HTTP/2 -- using the algorithms described in {{text}}.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as
described in BCP 14 {{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals, as
shown here.

This document uses the Augmented Backus-Naur Form (ABNF) notation of {{!RFC5234}}, including the DIGIT, ALPHA and DQUOTE rules from that document. It also includes the OWS rule from {{!RFC7230}}.


# Specifying Structured Headers {#specify}

HTTP headers that use Structured Headers need to be defined to do so explicitly; recipients and generators need to know that the requirements of this document are in effect. The simplest way to do that is by referencing this document in its definition.

The field's definition will also need to specify the field-value's allowed syntax, in terms of the types described in {{types}}, along with their associated semantics.

Field definitions MUST NOT relax or otherwise modify the requirements of this specification; doing so would preclude handling by generic software.

However, field definitions are encouraged to clearly state additional constraints upon the syntax, as well as the consequences when those constraints are violated.

For example:

~~~
# FooExample Header

The FooExample HTTP header field conveys a list of numbers about how
much Foo the sender has.

FooExample is a Structured header [RFCxxxx]. Its value MUST be a
dictionary ([RFCxxxx], Section Y.Y).

The dictionary MUST contain:

* A member whose key is "foo", and whose value is an integer
  ([RFCxxxx], Section Y.Y), indicating the number of foos in
  the message.
* A member whose key is "bar", and whose value is a string
  ([RFCxxxx], Section Y.Y), conveying the characteristic bar-ness
  of the message.

If the parsed header field does not contain both, it MUST be ignored.
~~~

Note that empty header field values are not allowed by the syntax, and therefore will be considered errors.


# Parsing Requirements for Textual Headers {#text}

When a receiving implementation parses textual HTTP header fields (e.g., in HTTP/1 or HTTP/2) that are known to be Structured Headers, it is important that care be taken, as there are a number of edge cases that can cause interoperability or even security problems. This section specifies the algorithm for doing so.

Given an ASCII string input_string that represents the chosen header's field-value, return the parsed header value. Note that input_string may incorporate multiple header lines combined into one comma-separated field-value, as per {{?RFC7230}}, Section 3.2.2.

1. Discard any OWS from the beginning of input_string.
2. If the field-value is defined to be a dictionary, return the result of Parsing a Dictionary from Textual headers ({{dictionary}}).
3. If the field-value is defined to be a list, return the result of Parsing a List from Textual Headers ({{list}}).
4. If the field-value is defined to be a parameterised label, return the result of Parsing a Parameterised Label from Textual headers ({{param}}).
5. Otherwise, return the result of Parsing an Item from Textual Headers ({{item}}).

Note that in the case of lists and dictionaries, this has the effect of combining multiple instances of the header field into one. However, for singular items and parameterised labels, it has the effect of selecting the first value and ignoring any subsequent instances of the field, as well as extraneous text afterwards.

Additionally, note that the effect of the parsing algorithms as specified is generally intolerant of syntax errors; if one is encountered, the typical response is to throw an error, thereby discarding the entire header field value. This includes any non-ASCII characters in input_string.


# Structured Header Data Types {#types}

This section defines the abstract value types that can be composed into Structured Headers, along with the textual HTTP serialisations of them.

## Numbers {#number}

Abstractly, numbers are integers with an optional fractional part. They have a maximum of fifteen digits available to be used in one or both of the parts, as reflected in the ABNF below; this allows them to be stored as IEEE 754 double precision numbers (binary64) ({{IEEE754}}).

The textual HTTP serialisation of numbers allows a maximum of fifteen digits between the integer and fractional part, along with an optional "-" indicating negative numbers.

~~~ abnf
number   = ["-"] ( "." 1*15DIGIT /
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
           14DIGIT "." 1DIGIT /
           15DIGIT )

integer  = ["-"] 1*15DIGIT
unsigned = 1*15DIGIT
~~~

integer and unsigned are defined as conveniences to specification authors; if their use is specified and their ABNF is not matched, a parser MUST consider it to be invalid.

For example, a header whose value is defined as a number could look like:

~~~
ExampleNumberHeader: 4.5
~~~


### Parsing Numbers from Textual Headers

TBD


## Strings {#string}

Abstractly, strings are ASCII strings {{!RFC0020}}, excluding control characters (i.e., the range 0x20 to 0x7E). Note that this excludes tabs, newlines and carriage returns. They may be at most 1024 characters long.

The textual HTTP serialisation of strings uses a backslash ("\") to escape double quotes and backslashes in strings.

~~~ abnf
string    = DQUOTE 1*1024(char) DQUOTE
char      = unescaped / escape ( DQUOTE / "\" )
unescaped = %x20-21 / %x23-5B / %x5D-7E
escape    = "\"
~~~

For example, a header whose value is defined as a string could look like:

~~~
ExampleStringHeader: "hello world"
~~~

Note that strings only use DQUOTE as a delimiter; single quotes do not delimit strings. Furthermore, only DQUOTE and "\" can be escaped; other sequences MUST generate an error.

Unicode is not directly supported in Structured Headers, because it causes a number of interoperability issues, and -- with few exceptions -- header values do not require it.

When it is necessary for a field value to convey non-ASCII string content, binary content ({{binary}}) SHOULD be specified, along with a character encoding (most likely, UTF-8).


### Parsing a String from Textual Headers

Given an ASCII string input_string, return an unquoted string. input_string is modified to remove the parsed value.

1. Let output_string be an empty string.
2. If the first character of input_string is not DQUOTE, throw an error.
3. Discard the first character of input_string.
4. If input_string contains more than 1025 characters, throw an error.
5. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is a backslash ("\\"):
      1. If input_string is now empty, throw an error.
      2. Else:
         1. Let next_char be the result of removing the first character of input_string.
         2. If next_char is not DQUOTE or "\\", throw an error.
         3. Append next_char to output_string.
   3. Else, if char is DQUOTE, remove the first character of input_string and return output_string.
   4. Else, append char to output_string.
6. Otherwise, throw an error.


## Labels {#label}

Labels are short (up to 256 characters) textual identifiers; their abstract model is identical to their expression in the textual HTTP serialisation.

~~~ abnf
label = lcalpha *255( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
lcalpha = %x61-7A ; a-z
~~~

Note that labels can only contain lowercase letters.

For example, a header whose value is defined as a label could look like:

~~~
ExampleLabelHeader: foo/bar
~~~


### Parsing a Label from Textual Headers

Given an ASCII string input_string, return a label. input_string is modified to remove the parsed value.

1. If input_string contains more than 256 characters, throw an error.
2. If the first character of input_string is not lcalpha, throw an error.
3. Let output_string be an empty string.
4. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is not one of lcalpha, DIGIT, "_", "-", "*" or "/":
      1. Prepend char to input_string.
      2. Return output_string.
   3. Append char to output_string.
5. Return output_string.


## Parameterised Labels {#param}

Parameterised Labels are labels ({{label}}) with up to 256 parameters; each parameter has a label and an optional value that is an item ({{item}}). Ordering between parameters is not significant, and duplicate parameters MUST be considered an error.

The textual HTTP serialisation uses semicolons (";") to delimit the parameters from each other, and equals ("=") to delimit the parameter name from its value.

~~~ abnf
parameterised = label *256( OWS ";" OWS label [ "=" item ] )
~~~

For example,

~~~
ExampleParamHeader: abc; a=1; b=2; c
~~~

### Parsing a Parameterised Label from Textual Headers

Given an ASCII string input_string, return a label with an mapping of parameters. input_string is modified to remove the parsed value.

1. Let primary_label be the result of Parsing a Label from Textual Headers ({{label}}) from input_string.
2. Let parameters be an empty mapping.
3. In a loop:
   1. Consume any OWS from the beginning of input_string.
   2. If the first character of input_string is not ";", exit the loop.
   3. Consume a ";" character from the beginning of input_string.
   4. Consume any OWS from the beginning of input_string.
   5. let param_name be the result of Parsing a Label from Textual Headers ({{label}}) from input_string.
   6. If param_name is already present in parameters, throw an error.
   7. Let param_value be a null value.
   8. If the first character of input_string is "=":
      1. Consume the "=" character at the beginning of input_string.
      2. Let param_value be the result of Parsing an Item from Textual Headers ({{item}}) from input_string.
   9. If parameters has more than 255 members, throw an error.
   0. Add param_name to parameters with the value param_value.
4. Return the tuple (primary_label, parameters).


## Binary Content {#binary}

Arbitrary binary content up to 16K in size can be conveyed in Structured Headers.

The textual HTTP serialisation indicates their presence by a leading "*", with the data encoded using Base 64 Encoding {{!RFC4648}}, without padding (as "=" might be confused with the use of dictionaries).

~~~ abnf
binary = "*" 1*21846(base64)
base64 = ALPHA / DIGIT / "+" / "/"
~~~

For example, a header whose value is defined as binary content could look like:

~~~
ExampleBinaryHeader: *cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg
~~~

### Parsing Binary Content from Textual Headers

Given an ASCII string input_string, return binary content. input_string is modified to remove the parsed value.

1. If the first character of input_string is not "*", throw an error.
2. Discard the first character of input_string.
3. Let b64_content be the result of removing content of input_string up to but not including the first character that is not in ALPHA, DIGIT, "+" or "/".
4. Let binary_content be the result of Base 64 Decoding {{!RFC4648}} b64_content, synthesising padding if necessary. If an error is encountered, throw it.
5. Return binary_content.


## Items {#item}

An item is can be a number ({{number}}), string ({{string}}), label ({{label}}) or binary content ({{binary}}).

~~~ abnf
item = number / string / label / binary
~~~


### Parsing an Item from Textual Headers

Given an ASCII string input_string, return an item. input_string is modified to remove the parsed value.

1. Discard any OWS from the beginning of input_string.
2. If the first character of input_string is a "-" or a DIGIT, process input_string as a number ({{number}}) and return the result, throwing any errors encountered.
3. If the first character of input_string is a DQUOTE, process input_string as a string ({{string}}) and return the result, throwing any errors encountered.
4. If the first character of input_string is "*", process input_string as binary content ({{binary}}) and return the result, throwing any errors encountered.
5. If the first character of input_string is an lcalpha, process input_string as a label ({{label}}) and return the result, throwing any errors encountered.
5. Otherwise, throw an error.


## Dictionaries {#dictionary}

Dictionaries are unordered maps of key-value pairs, where the keys are labels ({{label}}) and the values are items ({{item}}). There can be between 1 and 1024 members, and keys are required to be unique.

In the textual HTTP serialisation, keys and values are separated by "=" (without whitespace), and key/value pairs are separated by a comma with optional whitespace.

~~~ abnf
dictionary = label "=" item *1023( OWS "," OWS label "=" item )
~~~

For example, a header field whose value is defined as a dictionary could look like:

~~~
ExampleDictHeader: foo=1.23, da="Applepie", en=*w4ZibGV0w6ZydGUK
~~~

Typically, a header field specification will define the semantics of individual keys, as well as whether their presence is required or optional. Recipients MUST ignore keys that are undefined or unknown, unless the header field's specification specifically disallows them.


### Parsing a Dictionary from Textual Headers

Given an ASCII string input_string, return a mapping of (label, item). input_string is modified to remove the parsed value.

1. Let dictionary be an empty mapping.
2. While input_string is not empty:
   1. Let this_key be the result of running Parse Label from Textual Headers ({{label}}) with input_string. If an error is encountered, throw it.
   2. If dictionary already contains this_key, raise an error.
   2. Consume a "=" from input_string; if none is present, raise an error.
   3. Let this_value be the result of running Parse Item from Textual Headers ({{item}}) with input_string. If an error is encountered, throw it.
   4. Add key this_key with value this_value to dictionary.
   3. Discard any leading OWS from input_string.
   4. If input_string is empty, return dictionary.
   5. Consume a COMMA from input_string; if no comma is present, raise an error.
   6. Discard any leading OWS from input_string.
3. Return dictionary.


## Lists {#list}

Lists are arrays of items ({{item}}) or parameterised labels ({{param}}, with one to 1024 members.

In the textual HTTP serialisation, each member is separated by a comma and optional whitespace.

~~~ abnf
list = list_member 1*1024( OWS "," OWS list_member )
list_member = item / parameterised
~~~

For example, a header field whose value is defined as a list of labels could look like:

~~~
ExampleLabelListHeader: foo, bar, baz_45
~~~

and a header field whose value is defined as a list of parameterised labels could look like:

~~~
ExampleParamListHeader: abc/def; g="hi";j, klm/nop
~~~


### Parsing a List from Textual Headers

Given an ASCII string input_string, return a list of items. input_string is modified to remove the parsed value.

1. Let items be an empty array.
2. While input_string is not empty:
   1. Let item be the result of running Parse Item from Textual Headers ({{item}}) with input_string. If an error is encountered, throw it.
   2. Append item to items.
   3. Discard any leading OWS from input_string.
   4. If input_string is empty, return items.
   5. Consume a COMMA from input_string; if no comma is present, raise an error.
   6. Discard any leading OWS from input_string.
3. Return items.



# IANA Considerations

This draft has no actions for IANA.

# Security Considerations

TBD


--- back



# Changes

## Since draft-ietf-httpbis-header-structure-01

Replaced with draft-nottingham-structured-headers.

## Since draft-ietf-httpbis-header-structure-00

Added signed 64bit integer type.

Drop UTF8, and settle on BCP137 ::EmbeddedUnicodeChar for
h1-unicode-string.

Change h1_blob delimiter to ":" since "'" is valid t_char
