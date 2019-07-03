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

This document describes a set of data types and associated algorithms associated with them that are intended to make it easier and safer to define and handle HTTP header fields. It is intended for use by specifications of new HTTP header fields that wish to use a common syntax that is more restrictive than traditional HTTP/1.x field values.


--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.github.io/>; source code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/header-structure>.

Tests for implementations are collected at <https://github.com/httpwg/structured-header-tests>.

Implementations are tracked at <https://github.com/httpwg/wiki/wiki/Structured-Headers>.

--- middle

# Introduction

Specifying the syntax of new HTTP header fields is an onerous task; even with the guidance in {{?RFC7231}}, Section 8.3.1, there are many decisions -- and pitfalls -- for a prospective HTTP header field author.

Once a header field is defined, bespoke parsers and serializers often need to be written, because each header has slightly different handling of what looks like common syntax.

This document introduces a set of common data structures for use in definitions of new HTTP header field values to address these problems. In particular, it defines a generic, abstract model for header field values, along with a concrete serialisation for expressing that model in HTTP/1 {{?RFC7230}} header fields.

HTTP headers that are defined as "Structured Headers" use the types defined in this specification to define their syntax and basic handling rules, thereby simplifying both their definition by specification writers and handling by implementations.

Additionally, future versions of HTTP can define alternative serialisations of the abstract model of these structures, allowing headers that use it to be transmitted more efficiently without being redefined.

Note that it is not a goal of this document to redefine the syntax of existing HTTP headers; the mechanisms described herein are only intended to be used with headers that explicitly opt into them.

To specify a header field that is a Structured Header, see {{specify}}.

{{types}} defines a number of abstract data types that can be used in Structured Headers.

Those abstract types can be serialized into and parsed from textual headers -- such as those used in HTTP/1 -- using the algorithms described in {{text}}.


## Intentionally Strict Processing {#strict}

This specification intentionally defines strict parsing and serialisation behaviours using step-by-step algorithms; the only error handling defined is to fail the operation altogether.

This is designed to encourage faithful implementation and therefore good interoperability. Therefore, implementations that try to be "helpful" by being more tolerant of input are doing a disservice to the overall community, since it will encourage other implementations to implement similar (but likely subtly different) workarounds.

In other words, strict processing is an intentional feature of this specification; it allows non-conformant input to be discovered and corrected early, and avoids both interoperability and security issues that might otherwise result.

Note that as a result of this strictness, if a header field is appended to by multiple parties (e.g., intermediaries, or different components in the sender), it could be that an error in one party's value causes the entire header field to fail parsing.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as
described in BCP 14 {{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals, as
shown here.

This document uses the Augmented Backus-Naur Form (ABNF) notation of {{!RFC5234}}, including the VCHAR, SP, DIGIT, ALPHA and DQUOTE rules from that document. It also includes the OWS rule from {{!RFC7230}}.

This document uses algorithms to specify parsing and serialisation behaviours, and ABNF to illustrate expected syntax in HTTP/1-style header fields.

For parsing from HTTP/1 header fields, implementations MUST follow the algorithms, but MAY vary in implementation so as the behaviours are indistinguishable from specified behaviour. If there is disagreement between the parsing algorithms and ABNF, the specified algorithms take precedence. In some places, the algorithms are "greedy" with whitespace, but this should not affect conformance.

For serialisation to HTTP/1 header fields, the ABNF illustrates the range of acceptable wire representations with as much fidelity as possible, and the algorithms define the recommended way to produce them. Implementations MAY vary from the specified behaviour so long as the output still matches the ABNF.


# Defining New Structured Headers {#specify}

To define a HTTP header as a structured header, its specification needs to:

* Reference this specification. Recipients and generators of the header need to know that the requirements of this document are in effect.

* Specify the header field's allowed syntax for values, in terms of the types described in {{types}}, along with their associated semantics. Syntax definitions are encouraged to use the ABNF rules beginning with "sh-" defined in this specification.

* Specify any additional constraints upon the syntax of the structured used, as well as the consequences when those constraints are violated. When Structured Headers parsing fails, the header is discarded (see {{text-parse}}); in most situations, header-specific constraints should do likewise.

Note that a header field definition cannot relax the requirements of a structure or its processing because doing so would preclude handling by generic software; they can only add additional constraints. Likewise, header field definitions should use Structured Headers for the entire header field value, not a portion thereof.

For example:

~~~ example
2. Foo-Example Header

The Foo-Example HTTP header field conveys information about how
much Foo the message has.

Foo-Example is a Structured Header [RFCxxxx]. Its value MUST be a
dictionary ([RFCxxxx], Section Y.Y). Its ABNF is:

  Foo-Example = sh-dictionary

The dictionary MUST contain:

* Exactly one member whose key is "foo", and whose value is an
  integer ([RFCxxxx], Section Y.Y), indicating the number of foos
  in the message.
* Exactly one member whose key is "barUrls", and whose value is a
  string ([RFCxxxx], Section Y.Y), conveying the Bar URLs for the
  message. See below for processing requirements.

If the parsed header field does not contain both, it MUST be
ignored.

"foo" MUST be between 0 and 10, inclusive; other values MUST cause
the header to be ignored.

"barUrls" contains a space-separated list of URI-references
([RFC3986], Section 4.1):

   barURLs = URI-reference *( 1*SP URI-reference )

If a member of barURLs is not a valid URI-reference, it MUST cause
that value to be ignored.

If a member of barURLs is a relative reference ([RFC3986],
Section 4.2), it MUST be resolved ([RFC3986], Section 5) before
being used.
~~~

This specification defines minimums for the length or number of various structures supported by Structured Headers implementations. It does not specify maximum sizes in most cases, but header authors should be aware that HTTP implementations do impose various limits on the size of individual header fields, the total number of fields, and/or the size of the entire header block.


# Structured Header Data Types {#types}

This section defines the abstract value types that can be composed into Structured Headers. The ABNF provided represents the on-wire format in HTTP/1.


## Dictionaries {#dictionary}

Dictionaries are ordered maps of key-value pairs, where the keys are short, textual strings and the values are items ({{item}}). There can be one or more members, and keys are required to be unique.

Implementations MUST provide access to dictionaries both by index and by key. Specifications MAY use either means of accessing the members.

The ABNF for dictionaries in HTTP/1 headers is:

~~~ abnf
sh-dictionary  = dict-member *( OWS "," OWS dict-member )
dict-member    = member-name "=" member-value
member-name    = key
member-value   = sh-item
key            = lcalpha *( lcalpha / DIGIT / "_" / "-" )
lcalpha        = %x61-7A ; a-z
~~~

In HTTP/1, keys and values are separated by "=" (without whitespace), and key/value pairs are separated by a comma with optional whitespace. For example:

~~~ example
Example-DictHeader: en="Applepie", da=*w4ZibGV0w6ZydGU=*
~~~

Typically, a header field specification will define the semantics of individual keys, as well as whether their presence is required or optional. Recipients MUST ignore keys that are undefined or unknown, unless the header field's specification specifically disallows them.

Parsers MUST support dictionaries containing at least 1024 key/value pairs, and dictionary keys with at least 64 characters.


## Lists {#list}

Lists are arrays of items ({{item}}) with one or more members.

The ABNF for lists in HTTP/1 headers is:

~~~ abnf
sh-list     = list-member *( OWS "," OWS list-member )
list-member = sh-item
~~~

In HTTP/1, each member is separated by a comma and optional whitespace. For example, a header field whose value is defined as a list of strings could look like:

~~~ example
Example-StrListHeader: "foo", "bar", "It was the best of times."
~~~

Header specifications can constrain the types of individual values if necessary.

Parsers MUST support lists containing at least 1024 members.


## Lists of Lists {#listlist}

Lists of Lists are arrays of arrays containing items ({{item}}).

The ABNF for lists of lists in HTTP/1 headers is:

~~~ abnf
sh-listlist = inner-list *( OWS "," OWS inner-list )
inner-list  = list-member *( OWS ";" OWS list-member )
~~~

In HTTP/1, each inner-list is separated by a comma and optional whitespace, and members of the inner-list are separated by semicolons and optional whitespace. For example, a header field whose value is defined as a list of lists of strings could look like:

~~~ example
Example-StrListListHeader: "foo";"bar", "baz", "bat"; "one"
~~~

Header specifications can constrain the types of individual inner-list values if necessary.

Parsers MUST support lists of lists containing at least 1024 members, and inner-lists containing at least 256 members.


## Parameterized Lists {#param}

Parameterized Lists are arrays of parameterized identifiers, with one or more members.

A parameterized identifier is a primary identifier (a {{token}}}) with associated parameters, an ordered map of key-value pairs where the keys are short, textual strings and the values are items ({{item}}). There can be zero or more parameters, and keys are required to be unique.

The ABNF for parameterized lists in HTTP/1 headers is:

~~~ abnf
sh-param-list = param-item *( OWS "," OWS param-item )
param-item    = primary-id *parameter
primary-id    = sh-token
parameter     = OWS ";" OWS param-name [ "=" param-value ]
param-name    = key
param-value   = sh-item
~~~

In HTTP/1, each param-id is separated by a comma and optional whitespace (as in Lists), and the parameters are separated by semicolons. For example:

~~~ example
Example-ParamListHeader: abc_123;a=1;b=2; cdef_456, ghi;q="9";r="w"
~~~

Parsers MUST support parameterized lists containing at least 1024 members, support members with at least 256 parameters, and support parameter keys with at least 64 characters.


## Items {#item}

An item is can be a integer ({{integer}}), float ({{float}}), string ({{string}}), token ({{token}}), byte sequence ({{binary}}), or Boolean ({{boolean}}).

The ABNF for items in HTTP/1 headers is:

~~~ abnf
sh-item = sh-integer / sh-float / sh-string / sh-token / sh-binary
          / sh-boolean
~~~


## Integers {#integer}

Integers have a range of −999,999,999,999,999 to 999,999,999,999,999 inclusive (i.e., up to fifteen digits, signed), for IEEE 754 compatibility ({{IEEE754}}).

The ABNF for integers in HTTP/1 headers is:

~~~ abnf
sh-integer = ["-"] 1*15DIGIT
~~~

For example:

~~~ example
Example-IntegerHeader: 42
~~~


## Floats {#float}

Floats are integers with a fractional part, that can be stored as IEEE 754 double precision numbers (binary64) ({{IEEE754}}).

The ABNF for floats in HTTP/1 headers is:

~~~ abnf
sh-float    = ["-"] (
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

For example, a header whose value is defined as a float could look like:

~~~ example
Example-FloatHeader: 4.5
~~~


## Strings {#string}

Strings are zero or more printable ASCII {{!RFC0020}} characters (i.e., the range 0x20 to 0x7E). Note that this excludes tabs, newlines, carriage returns, etc.

The ABNF for strings in HTTP/1 headers is:

~~~ abnf
sh-string = DQUOTE *(chr) DQUOTE
chr       = unescaped / escaped
unescaped = %x20-21 / %x23-5B / %x5D-7E
escaped   = "\" ( DQUOTE / "\" )
~~~

In HTTP/1 headers, strings are delimited with double quotes, using a backslash ("\\") to escape double quotes and backslashes. For example:

~~~ example
Example-StringHeader: "hello world"
~~~

Note that strings only use DQUOTE as a delimiter; single quotes do not delimit strings. Furthermore, only DQUOTE and "\\" can be escaped; other sequences MUST cause parsing to fail.

Unicode is not directly supported in this document, because it causes a number of interoperability issues, and -- with few exceptions -- header values do not require it.

When it is necessary for a field value to convey non-ASCII string content, a byte sequence ({{binary}}) SHOULD be specified, along with a character encoding (preferably UTF-8).

Parsers MUST support strings with at least 1024 characters.


## Tokens {#token}

Tokens are short textual words; their abstract model is identical to their expression in the textual HTTP serialisation.

The ABNF for tokens in HTTP/1 headers is:

~~~ abnf
sh-token = ALPHA
           *( ALPHA / DIGIT / "_" / "-" / "." / ":" / "%"
              / "*" / "/" )
~~~

Parsers MUST support tokens with at least 512 characters.

Note that a Structured Header token is not the same as the "token" ABNF rule defined in
{{?RFC7230}}.


## Byte Sequences {#binary}

Byte sequences can be conveyed in Structured Headers.

The ABNF for a byte sequence in HTTP/1 headers is:

~~~ abnf
sh-binary = "*" *(base64) "*"
base64    = ALPHA / DIGIT / "+" / "/" / "="
~~~

In HTTP/1 headers, a byte sequence is delimited with asterisks and encoded using base64 ({{!RFC4648}}, Section 4). For example:

~~~ example
Example-BinaryHdr: *cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==*
~~~

Parsers MUST support byte sequences with at least 16384 octets after decoding.


## Booleans {#boolean}

Boolean values can be conveyed in Structured Headers.

The ABNF for a Boolean in HTTP/1 headers is:

~~~ abnf
sh-boolean = "?" boolean
boolean    = "0" / "1"
~~~

In HTTP/1 headers, a boolean is indicated with a leading "?" character. For example:

~~~ example
Example-BoolHdr: ?1
~~~


# Structured Headers in HTTP/1 {#text}

This section defines how to serialize and parse Structured Headers in HTTP/1 textual header fields, and protocols compatible with them (e.g., in HTTP/2 {{?RFC7540}} before HPACK {{?RFC7541}} is applied).

## Serializing Structured Headers into HTTP/1 {#text-serialize}

Given a structured defined in this specification:

1. If the structure is a dictionary, let output_string be the result of Serializing a Dictionary ({{ser-dictionary}}).
2. Else if the structure is a parameterized list, let output_string be the result of Serializing a Parameterized List ({{ser-param-list}}).
3. Else if the structure is a list of lists, let output_string be the result of Serializing a List of Lists ({ser-listlist}).
4. Else if the structure is a list, let output_string be the result of Serializing a List {{ser-list}}.
5. Else if the structure is an item, let output_string be the result of Serializing an Item ({{ser-item}}).
6. Else, fail serialisation.
7. Return output_string converted in to an array of bytes, using ASCII encoding {{!RFC0020}}.


### Serializing a Dictionary {#ser-dictionary}

Given a dictionary as input_dictionary:

1. Let output be an empty string.
2. For each member mem of input_dictionary:
   1. Let name be the result of applying Serializing a Key ({{ser-key}}) to mem's member-name.
   2. Append name to output.
   3. Append "=" to output.
   4. Let value be the result of applying Serializing an Item ({{ser-item}}) to mem's member-value.
   5. Append value to output.
   6. If more members remain in input_dictionary:
      1. Append a COMMA to output.
      2. Append a single WS to output.
3. Return output.

#### Serializing a Key {#ser-key}

Given a key as input_key:

0. If input_key is not a sequence of characters, or contains characters not allowed in the ABNF for key, fail serialisation.
1. Let output be an empty string.
2. Append input_key to output.
3. Return output.


### Serializing a List {#ser-list}

Given a list as input_list:

1. Let output be an empty string.
2. For each member mem of input_list:
   1. Let value be the result of applying Serializing an Item ({{ser-item}}) to mem.
   2. Append value to output.
   3. If more members remain in input_list:
      1. Append a COMMA to output.
      2. Append a single WS to output.
3. Return output.


### Serializing a List of Lists {#ser-listlist}

Given a list of lists of items as input_list:

1. Let output be an empty string.
2. For each member inner_list of input_list:
   1. If inner_list is not a list, fail serialisation.
   2. If inner_list is empty, fail serialisation.
   3. For each inner_mem of inner_list:
      1. Let value be the result of applying Serializing an Item ({{ser-item}}) to inner_mem.
      2. Append value to output.
      3. If more members remain in inner_list:
         1. Append a ";" to output.
         2. Append a single WS to output.
   4. If more members remain in input_list:
      1. Append a COMMA to output.
      2. Append a single WS to output.
3. Return output.


### Serializing a Parameterized List {#ser-param-list}

Given a parameterized list as input_plist:

1. Let output be an empty string.
2. For each member mem of input_plist:
   1. Let id be the result of applying Serializing a Token ({{ser-token}}) to mem's token.
   2. Append id to output.
   3. For each parameter in mem's parameters:
      1. Append ";" to output.
      2. Let name be the result of applying Serializing a Key ({{ser-key}}) to parameter's param-name.
      3. Append name to output.
      4. If parameter has a param-value:
         1. Let value be the result of applying Serializing an Item ({{ser-item}}) to parameter's param-value.
         2. Append "=" to output.
         3. Append value to output.
   4. If more members remain in input_plist:
      1. Append a COMMA to output.
      2. Append a single WS to output.
3. Return output.


### Serializing an Item {#ser-item}

Given an item as input_item:

1. If input_item is an integer, return the result of applying Serializing an Integer ({{ser-integer}}) to input_item.
2. If input_item is a float, return the result of applying Serializing a Float ({{ser-float}}) to input_item.
3. If input_item is a string, return the result of applying Serializing a String ({{ser-string}}) to input_item.
4. If input_item is a token, return the result of Serializing a Token ({{ser-token}}) to input_item.
5. If input_item is a Boolean, return the result of applying Serializing a Boolean ({{ser-boolean}}) to input_item.
6. If input_item is a byte sequence, return the result of applying Serializing a Byte Sequence ({{ser-binary}}) to input_item.
7. Otherwise, fail serialisation.


### Serializing an Integer {#ser-integer}

Given an integer as input_integer:

0. If input_integer is not an integer in the range of −999,999,999,999,999 to 999,999,999,999,999 inclusive, fail serialisation.
1. Let output be an empty string.
2. If input_integer is less than (but not equal to) 0, append "-" to output.
3. Append input_integer's numeric value represented in base 10 using only decimal digits to output.
4. Return output.


### Serializing a Float {#ser-float}

Given a float as input_float:

0. If input_float is not a IEEE 754 double precision number, fail serialisation.
1. Let output be an empty string.
2. If input_float is less than (but not equal to) 0, append "-" to output.
3. Append input_float's integer component represented in base 10 using only decimal digits to output; if it is zero, append "0".
4. Append "." to output.
5. Append input_float's decimal component represented in base 10 using only decimal digits to output; if it is zero, append "0".
6. Return output.


### Serializing a String {#ser-string}

Given a string as input_string:

0. If input_string is not a sequence of characters, or contains characters outside the range allowed by VCHAR or SP, fail serialisation.
1. Let output be an empty string.
2. Append DQUOTE to output.
3. For each character char in input_string:
   1. If char is "\\" or DQUOTE:
      1. Append "\\" to output.
   2. Append char to output.
4. Append DQUOTE to output.
5. Return output.


### Serializing a Token {#ser-token}

Given a token as input_token:

0. If input_token is not a sequence of characters, or contains characters not allowed in {{token}}}, fail serialisation.
1. Let output be an empty string.
2. Append input_token to output.
3. Return output.


### Serializing a Byte Sequence {#ser-binary}

Given a byte sequence as input_bytes:

0. If input_bytes is not a sequence of bytes, fail serialisation.
1. Let output be an empty string.
2. Append "\*" to output.
3. Append the result of base64-encoding input_bytes as per {{!RFC4648}}, Section 4, taking account of the requirements below.
4. Append "\*" to output.
5. Return output.

The encoded data is required to be padded with "=", as per {{!RFC4648}}, Section 3.2.

Likewise, encoded data SHOULD have pad bits set to zero, as per {{!RFC4648}}, Section 3.5, unless it is not possible to do so due to implementation constraints.


### Serializing a Boolean {#ser-boolean}

Given a Boolean as input_boolean:

0. If input_boolean is not a boolean, fail serialisation.
1. Let output be an empty string.
2. Append "?" to output.
3. If input_boolean is true, append "1" to output.
4. If input_boolean is false, append "0" to output.
5. Return output.


## Parsing HTTP/1 Header Fields into Structured Headers {#text-parse}

When a receiving implementation parses textual HTTP header fields (e.g., in HTTP/1 or HTTP/2) that are known to be Structured Headers, it is important that care be taken, as there are a number of edge cases that can cause interoperability or even security problems. This section specifies the algorithm for doing so.

Given an array of bytes input_bytes that represents the chosen header's field-value, and header_type (one of "dictionary", "list", "list-list", "param-list", or "item"), return the parsed header value.

0. Convert input_bytes into an ASCII string input_string; if conversion fails, fail parsing.
1. Discard any leading OWS from input_string.
2. If header_type is "dictionary", let output be the result of Parsing a Dictionary from Text ({{parse-dictionary}}).
3. If header_type is "list", let output be the result of Parsing a List from Text ({{parse-list}}).
4. If header_type is "list-list", let output be the result of Parsing a List of Lists from Text ({{parse-listlist}}).
4. If header_type is "param-list", let output be the result of Parsing a Parameterized List from Text ({{parse-param-list}}).
5. If header_type is "item", let output be the result of Parsing an Item from Text ({{parse-item}}).
6. Discard any leading OWS from input_string.
7. If input_string is not empty, fail parsing.
8. Otherwise, return output.

When generating input_bytes, parsers MUST combine all instances of the target header field into one comma-separated field-value, as per {{?RFC7230}}, Section 3.2.2; this assures that the header is processed correctly.

For Lists, Lists of Lists, Parameterized Lists and Dictionaries, this has the effect of correctly concatenating all instances of the header field, as long as individual individual members of the top-level data structure are not split across multiple header instances.

Strings split across multiple header instances will have unpredictable results, because comma(s) and whitespace inserted upon combination will become part of the string output by the parser. Since concatenation might be done by an upstream intermediary, the results are not under the control of the serializer or the parser.

Integers, Floats and Byte Sequences cannot be split across multiple headers because the inserted commas will cause parsing to fail.

If parsing fails -- including when calling another algorithm -- the entire header field's value MUST be discarded. This is intentionally strict, to improve interoperability and safety, and specifications referencing this document cannot loosen this requirement.


### Parsing a Dictionary from Text {#parse-dictionary}

Given an ASCII string input_string, return an ordered map of (key, item). input_string is modified to remove the parsed value.

1. Let dictionary be an empty, ordered map.
2. While input_string is not empty:
   1. Let this_key be the result of running Parse a Key from Text ({{parse-key}}) with input_string.
   2. If dictionary already contains this_key, fail parsing.
   3. Consume the first character of input_string; if it is not "=", fail parsing.
   4. Let this_value be the result of running Parse Item from Text ({{parse-item}}) with input_string.
   5. Add key this_key with value this_value to dictionary.
   6. Discard any leading OWS from input_string.
   7. If input_string is empty, return dictionary.
   8. Consume the first character of input_string; if it is not COMMA, fail parsing.
   9. Discard any leading OWS from input_string.
   0. If input_string is empty, fail parsing.
3. No structured data has been found; fail parsing.


### Parsing a Key from Text {#parse-key}

Given an ASCII string input_string, return a key. input_string is modified to remove the parsed value.

1. If the first character of input_string is not lcalpha, fail parsing.
2. Let output_string be an empty string.
3. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is not one of lcalpha, DIGIT, "\_", or "-":
      1. Prepend char to input_string.
      2. Return output_string.
   3. Append char to output_string.
4. Return output_string.


### Parsing a List from Text {#parse-list}

Given an ASCII string input_string, return a list of items. input_string is modified to remove the parsed value.

1. Let items be an empty array.
2. While input_string is not empty:
   1. Let item be the result of running Parse Item from Text ({{parse-item}}) with input_string.
   2. Append item to items.
   3. Discard any leading OWS from input_string.
   4. If input_string is empty, return items.
   5. Consume the first character of input_string; if it is not COMMA, fail parsing.
   6. Discard any leading OWS from input_string.
   7. If input_string is empty, fail parsing.
3. No structured data has been found; fail parsing.


### Parsing a List of Lists from Text {#parse-listlist}

Given an ASCII string input_string, return a list of lists of items. input_string is modified to remove the parsed value.

1. let top_list be an empty array.
2. Let inner_list be an empty array.
3. While input_string is not empty:
   1. Let item be the result of running Parse Item from Text ({{parse-item}}) with input_string.
   2. Append item to inner_list.
   3. Discard any leading OWS from input_string.
   4. If input_string is empty, append inner_list to top_list and return top_list.
   5. Let char be the result of consuming the first character of input_string.
   6. If char is COMMA:
      1. Append inner_list to top_list.
      2. Let inner_list be an empty array.
   7. Else if char is not ";", fail parsing.
   8. Discard any leading OWS from input_string.
   9. If input_string is empty, fail parsing.
4. No structured data has been found; fail parsing.


### Parsing a Parameterized List from Text {#parse-param-list}

Given an ASCII string input_string, return a list of parameterized identifiers. input_string is modified to remove the parsed value.

1. Let items be an empty array.
2. While input_string is not empty:
   1. Let item be the result of running Parse Parameterized Identifier from Text ({{parse-param-id}}) with input_string.
   2. Append item to items.
   3. Discard any leading OWS from input_string.
   4. If input_string is empty, return items.
   5. Consume the first character of input_string; if it is not COMMA, fail parsing.
   6. Discard any leading OWS from input_string.
   7. If input_string is empty, fail parsing.
3. No structured data has been found; fail parsing.


### Parsing a Parameterized Identifier from Text {#parse-param-id}

Given an ASCII string input_string, return an token with an unordered map of parameters. input_string is modified to remove the parsed value.

1. Let primary_identifier be the result of Parsing a Token from Text ({{parse-token}}) from input_string.
2. Let parameters be an empty, ordered map.
3. In a loop:
   1. Discard any leading OWS from input_string.
   2. If the first character of input_string is not ";", exit the loop.
   3. Consume a ";" character from the beginning of input_string.
   4. Discard any leading OWS from input_string.
   5. let param_name be the result of Parsing a key from Text ({{parse-key}}) from input_string.
   6. If param_name is already present in parameters, fail parsing.
   7. Let param_value be a null value.
   8. If the first character of input_string is "=":
      1. Consume the "=" character at the beginning of input_string.
      2. Let param_value be the result of Parsing an Item from Text ({{parse-item}}) from input_string.
   9. Add key param_name with value param_value to parameters.
4. Return the tuple (primary_identifier, parameters).


### Parsing an Item from Text {#parse-item}

Given an ASCII string input_string, return an item. input_string is modified to remove the parsed value.

1. If the first character of input_string is a "-" or a DIGIT, process input_string as a number ({{parse-number}}) and return the result.
2. If the first character of input_string is a DQUOTE, process input_string as a string ({{parse-string}}) and return the result.
3. If the first character of input_string is "\*", process input_string as a byte sequence ({{parse-binary}}) and return the result.
4. If the first character of input_string is "?", process input_string as a Boolean ({{parse-boolean}}) and return the result.
5. If the first character of input_string is an ALPHA, process input_string as a token ({{parse-token}}) and return the result.
6. Otherwise, fail parsing.


### Parsing a Number from Text {#parse-number}

Given an ASCII string input_string, return a number. input_string is modified to remove the parsed value.

NOTE: This algorithm parses both Integers {{integer}} and Floats {{float}}, and returns the corresponding structure.

1. Let type be "integer".
2. Let sign be 1.
3. Let input_number be an empty string.
4. If the first character of input_string is "-", remove it from input_string and set sign to -1.
5. If input_string is empty, fail parsing.
6. If the first character of input_string is not a DIGIT, fail parsing.
7. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is a DIGIT, append it to input_number.
   3. Else, if type is "integer" and char is ".", append char to input_number and set type to "float".
   4. Otherwise, prepend char to input_string, and exit the loop.
   5. If type is "integer" and input_number contains more than 15 characters, fail parsing.
   6. If type is "float" and input_number contains more than 16 characters, fail parsing.
8. If type is "integer":
   1. Parse input_number as an integer and let output_number be the product of the result and sign.
   2. If output_number is outside the range defined in {{integer}}, fail parsing.
9. Otherwise:
   1. If the final character of input_number is ".", fail parsing.
   2. Parse input_number as a float and let output_number be the product of the result and sign.
0. Return output_number.


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
   4. Else, if char is in the range %x00-1f or %x7f (i.e., is not in VCHAR or SP), fail parsing.
   4. Else, append char to output_string.
6. Reached the end of input_string without finding a closing DQUOTE; fail parsing.


### Parsing a Token from Text {#parse-token}

Given an ASCII string input_string, return a token. input_string is modified to remove the parsed value.

1. If the first character of input_string is not ALPHA, fail parsing.
2. Let output_string be an empty string.
3. While input_string is not empty:
   1. Let char be the result of removing the first character of input_string.
   2. If char is not one of ALPHA, DIGIT, "\_", "-", ".", ":", "%", "\*" or "/":
      1. Prepend char to input_string.
      2. Return output_string.
   3. Append char to output_string.
4. Return output_string.


### Parsing a Byte Sequence from Text {#parse-binary}

Given an ASCII string input_string, return a byte sequence. input_string is modified to remove the parsed value.

1. If the first character of input_string is not "\*", fail parsing.
2. Discard the first character of input_string.
3. If there is not a "\*" character before the end of input_string, fail parsing.
4. Let b64_content be the result of removing content of input_string up to but not including the first instance of the character "\*".
5. Consume the "\*" character at the beginning of input_string.
6. If b64_content contains a character not included in ALPHA, DIGIT, "+", "/" and "=", fail parsing.
7. Let binary_content be the result of Base 64 Decoding {{!RFC4648}} b64_content, synthesizing padding if necessary (note the requirements about recipient behaviour below).
8. Return binary_content.

Because some implementations of base64 do not allow reject of encoded data that is not properly "=" padded (see {{!RFC4648}}, Section 3.2), parsers SHOULD NOT fail when it is not present, unless they cannot be configured to do so.

Because some implementations of base64 do not allow rejection of encoded data that has non-zero pad bits (see {{!RFC4648}}, Section 3.5), parsers SHOULD NOT fail when it is present, unless they cannot be configured to do so.

This specification does not relax the requirements in {{!RFC4648}}, Section 3.1 and 3.3; therefore, parsers MUST fail on characters outside the base64 alphabet, and on line feeds in encoded data.


### Parsing a Boolean from Text {#parse-boolean}

Given an ASCII string input_string, return a Boolean. input_string is modified to remove the parsed value.

1. If the first character of input_string is not "?", fail parsing.
2. Discard the first character of input_string.
3. If the first character of input_string matches "1", discard the first character, and return true.
4. If the first character of input_string matches "0", discard the first character, and return false.
5. No value has matched; fail parsing.


# IANA Considerations

This draft has no actions for IANA.

# Security Considerations

The size of most types defined by Structured Headers is not limited; as a result, extremely large header fields could be an attack vector (e.g., for resource consumption). Most HTTP implementations limit the sizes of individual header fields as well as the overall header block size to mitigate such attacks.

It is possible for parties with the ability to inject new HTTP header fields to change the meaning
of a Structured Header. In some circumstances, this will cause parsing to fail, but it is not possible to reliably fail in all such circumstances.

--- back

# Acknowledgements

Many thanks to Matthew Kerwin for his detailed feedback and careful consideration during the development of this specification.


# Frequently Asked Questions {#faq}

## Why not JSON?

Earlier proposals for structured headers were based upon JSON {{?RFC8259}}. However, constraining its use to make it suitable for HTTP header fields required senders and recipients to implement specific additional handling.

For example, JSON has specification issues around large numbers and objects with duplicate members. Although advice for avoiding these issues is available (e.g., {{?RFC7493}}), it cannot be relied upon.

Likewise, JSON strings are by default Unicode strings, which have a number of potential interoperability issues (e.g., in comparison). Although implementers can be advised to avoid non-ASCII content where unnecessary, this is difficult to enforce.

Another example is JSON's ability to nest content to arbitrary depths. Since the resulting memory commitment might be unsuitable (e.g., in embedded and other limited server deployments), it's necessary to limit it in some fashion; however, existing JSON implementations have no such limits, and even if a limit is specified, it's likely that some header field definition will find a need to violate it.

Because of JSON's broad adoption and implementation, it is difficult to impose such additional constraints across all implementations; some deployments would fail to enforce them, thereby harming interoperability.

Since a major goal for Structured Headers is to improve interoperability and simplify implementation, these concerns led to a format that requires a dedicated parser and serializer.

Additionally, there were widely shared feelings that JSON doesn't "look right" in HTTP headers.

## Structured Headers don't "fit" my data.

Structured headers intentionally limits the complexity of data structures, to assure that it can be processed in a performant manner with little overhead. This means that work is necessary to fit some data types into them.

Sometimes, this can be achieved by creating limited substructures in values, and/or using more than one header. For example, consider:

~~~
Example-Thing: name="Widget", cost=89.2, descriptions="foo bar"
Example-Description: foo; url="https://example.net"; context=123,
                     bar; url="https://example.org"; context=456
~~~

Since the description contains a list of key/value pairs, we use a Parameterized List to represent them, with the token for each item in the list used to identify it in the "descriptions" member of the Example-Thing header.

When specifying more than one header, it's important to remember to describe what a processor's behaviour should be when one of the headers is missing.

If you need to fit arbitrarily complex data into a header, Structured Headers is probably a poor fit for your use case.

# Implementation Notes

A generic implementation of this specification should expose the top-level parse ({{text-parse}}) and serialize ({{text-serialize}}) functions. They need not be functions; for example, it could be implemented as an object, with methods for each of the different top-level types.

For interoperability, it's important that generic implementations be complete and follow the algorithms closely; see {{strict}}. To aid this, a common test suite is being maintained by the community; see <https://github.com/httpwg/structured-header-tests>.

Implementers should note that dictionaries and parameters are order-preserving maps. Some headers may not convey meaning in the ordering of these data types, but it should still be exposed so that applications which need to use it will have it available.

Likewise, implementations should note that it's important to preserve the distinction between tokens and strings. While most programming languages have native types that map to the other types well, it may be necessary to create a wrapper "token" object or use a parameter on functions to assure that these types remain separate.


# Changes

_RFC Editor: Please remove this section before publication._


## Since draft-ietf-httpbis-header-structure-10

* Update abstract (#799).
* Input and output are now arrays of bytes (#662).
* Implementations need to preserve difference between token and string (#790).


## Since draft-ietf-httpbis-header-structure-09

* Changed Boolean from T/F to 1/0 (#784).
* Parameters are now ordered maps (#765).
* Clamp integers to 15 digits (#737).


## Since draft-ietf-httpbis-header-structure-08

* Disallow whitespace before items properly (#703).
* Created "key" for use in dictionaries and parameters, rather than relying on identifier (#702). Identifiers have a separate minimum supported size.
* Expanded the range of special characters allowed in identifier to include all of ALPHA, ".", ":", and "%" (#702).
* Use "?" instead of "!" to indicate a Boolean (#719).
* Added "Intentionally Strict Processing" (#684).
* Gave better names for referring specs to use in Parameterised Lists (#720).
* Added Lists of Lists (#721).
* Rename Identifier to Token (#725).
* Add implementation guidance (#727).


## Since draft-ietf-httpbis-header-structure-07

* Make Dictionaries ordered mappings (#659).
* Changed "binary content" to "byte sequence" to align with Infra specification (#671).
* Changed "mapping" to "map" for #671.
* Don't fail if byte sequences aren't "=" padded (#658).
* Add Booleans (#683).
* Allow identifiers in items again (#629).
* Disallowed whitespace before items (#703).
* Explain the consequences of splitting a string across multiple headers (#686).


## Since draft-ietf-httpbis-header-structure-06

* Add a FAQ.
* Allow non-zero pad bits.
* Explicitly check for integers that violate constraints.


## Since draft-ietf-httpbis-header-structure-05

* Reorganise specification to separate parsing out.
* Allow referencing specs to use ABNF.
* Define serialisation algorithms.
* Refine relationship between ABNF, parsing and serialisation algorithms.


## Since draft-ietf-httpbis-header-structure-04

* Remove identifiers from item.
* Remove most limits on sizes.
* Refine number parsing.


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
