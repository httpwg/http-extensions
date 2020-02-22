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
  tocdepth: 3


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
    target: https://ieeexplore.ieee.org/document/8766229
    title: IEEE Standard for Floating-Point Arithmetic
    author:
    -
      organization: IEEE
    date: 2019-07
    seriesinfo:
      IEEE: 754-2019
      DOI:  10.1109/IEEESTD.2019.8766229
      ISBN: 978-1-5044-5924-2

  UTF-8:
    title: UTF-8, a transformation format of ISO 10646
    author:
    - ins: F. Yergeau
      name: F. Yergeau
    date: 2003-11
    seriesinfo:
      STD: 63
      RFC: 3629
      DOI: 10.17487/RFC3629
    target: http://www.rfc-editor.org/info/std63


--- abstract

This document describes a set of data types and associated algorithms that are intended to make it easier and safer to define and handle HTTP header and trailer fields. It is intended for use by specifications of new HTTP fields that wish to use a common syntax that is more restrictive than traditional HTTP field values.


--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.github.io/>; source code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/header-structure>.

Tests for implementations are collected at <https://github.com/httpwg/structured-header-tests>.

Implementations are tracked at <https://github.com/httpwg/wiki/wiki/Structured-Headers>.

--- middle

# Introduction

Specifying the syntax of new HTTP header (and trailer) fields is an onerous task; even with the guidance in Section 8.3.1 of {{?RFC7231}}, there are many decisions -- and pitfalls -- for a prospective HTTP field author.

Once a field is defined, bespoke parsers and serializers often need to be written, because each field value has slightly different handling of what looks like common syntax.

This document introduces a set of common data structures for use in definitions of new HTTP field values to address these problems. In particular, it defines a generic, abstract model for them, along with a concrete serialisation for expressing that model in HTTP {{?RFC7230}} header and trailer fields.

HTTP headers and trailers that are defined as "Structured Headers" (or "Structured Trailers", respectively) use the types defined in this specification to define their syntax and basic handling rules, thereby simplifying both their definition by specification writers and handling by implementations.

Additionally, future versions of HTTP can define alternative serialisations of the abstract model of these structures, allowing fields that use it to be transmitted more efficiently without being redefined.

Note that it is not a goal of this document to redefine the syntax of existing HTTP fields; the mechanisms described herein are only intended to be used with those that explicitly opt into them.

{{specify}} describes how to specify a Structured Header.

{{types}} defines a number of abstract data types that can be used in Structured Headers. Those abstract types can be serialized into and parsed from HTTP field values using the algorithms described in {{text}}.


## Intentionally Strict Processing {#strict}

This specification intentionally defines strict parsing and serialisation behaviours using step-by-step algorithms; the only error handling defined is to fail the operation altogether.

It is designed to encourage faithful implementation and therefore good interoperability. Therefore, an implementation that tried to be "helpful" by being more tolerant of input would make interoperability worse, since that would create pressure on other implementations to implement similar (but likely subtly different) workarounds.

In other words, strict processing is an intentional feature of this specification; it allows non-conformant input to be discovered and corrected by the producer early, and avoids both interoperability and security issues that might otherwise result.

Note that as a result of this strictness, if a field is appended to by multiple parties (e.g., intermediaries, or different components in the sender), an error in one party's value is likely to cause the entire field value to fail parsing.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as
described in BCP 14 {{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals, as
shown here.

This document uses algorithms to specify parsing and serialisation behaviours, and the Augmented Backus-Naur Form (ABNF) notation of {{!RFC5234}} to illustrate expected syntax in HTTP header fields. In doing so, uses the VCHAR, SP, DIGIT, ALPHA and DQUOTE rules from {{!RFC5234}}. It also includes the tchar rule from {{!RFC7230}}.

When parsing from HTTP fields, implementations MUST follow the algorithms, but MAY vary in implementation so as the behaviours are indistinguishable from specified behaviour. If there is disagreement between the parsing algorithms and ABNF, the specified algorithms take precedence. In some places, the algorithms are "greedy" with whitespace, but this should not affect conformance.

For serialisation to HTTP fields, the ABNF illustrates the range of acceptable wire representations with as much fidelity as possible, and the algorithms define the recommended way to produce them. Implementations MAY vary from the specified behaviour so long as the output still matches the ABNF.


# Defining New Structured Headers {#specify}

To specify a HTTP field as a Structured Header (or Structured Trailer), its authors needs to:

* Reference this specification. Recipients and generators of the field need to know that the requirements of this document are in effect.

* Specify the type of the field value; either Dictionary ({{dictionary}}), List ({{list}}), or Item ({{item}}).

* Define the semantics of those structures.

* Specify any additional constraints upon the structures used, as well as the consequences when those constraints are violated.

Typically, this means that a field definition will specify the top-level type -- Dictionary, List or Item -- and then define its allowable types, and constraints upon them. For example, a header defined as a List might have all Integer members, or a mix of types; a header defined as an Item might allow only Strings, and additionally only strings beginning with the letter "Q". Likewise, inner lists are only valid when a field definition explicitly allows them.

When Structured Headers parsing fails, the field is ignored (see {{text-parse}}); in most situations, violating field-specific constraints should have the same effect. Thus, if a header is defined as an Item and required to be an Integer, but a String is received, it will by default be ignored. If the field requires different error handling, this should be explicitly specified.

However, both items and inner lists allow parameters as an extensibility mechanism; this means that values can later be extended to accommodate more information, if need be. As a result, field specifications are discouraged from defining the presence of an unrecognised parameter as an error condition.

To help assure that this extensibility is available in the future, and to encourage consumers to use a fully capable Structured Headers parser, a field definition can specify that "grease" parameters be added by senders. For example, a specification could stipulate that all parameters beginning with the letter 'q' are reserved for this use.

Note that a field definition cannot relax the requirements of this specification because doing so would preclude handling by generic software; they can only add additional constraints (for example, on the numeric range of integers and decimals, the format of strings and tokens, the types allowed in a dictionary's values, or the number of items in a list). Likewise, field definitions can only use Structured Headers for the entire field value, not a portion thereof.

This specification defines minimums for the length or number of various structures supported by Structured Headers implementations. It does not specify maximum sizes in most cases, but authors should be aware that HTTP implementations do impose various limits on the size of individual fields, the total number of fields, and/or the size of the entire header or trailer section.

Specifications can refer to a Structured Header's field name as a "structured header name" and its field value as a "structured header value" as necessary. Field definitions are encouraged to use the ABNF rules beginning with "sh-" defined in this specification; other rules in this specification are not intended for their use.

For example, a fictitious Foo-Example header field might be specified as:

~~~ example
42. Foo-Example Header

The Foo-Example HTTP header field conveys information about how
much Foo the message has.

Foo-Example is a Item Structured Header [RFCxxxx]. Its value MUST be
an Integer (Section Y.Y of [RFCxxxx]). Its ABNF is:

  Foo-Example = sh-integer

Its value indicates the amount of Foo in the message, and MUST
be between 0 and 10, inclusive; other values MUST cause
the entire header to be ignored.

The following parameters are defined:
* A parameter whose name is "fooUrl", and whose value is a string
  (Section Y.Y of [RFCxxxx]), conveying the Foo URLs
  for the message. See below for processing requirements.

"fooUrl" contains a URI-reference (Section 4.1 of
[RFC3986], Section 4.1). If its value is not a valid URI-reference,
that URL MUST be ignored. If its value is a relative reference
(Section 4.2 of [RFC3986]), it MUST be resolved (Section 5 of
[RFC3986]) before being used.

For example:

  Foo-Example: 2; foourl="https://foo.example.com/"
~~~


# Structured Data Types {#types}

This section defines the abstract value types that can be composed into Structured Headers. The ABNF provided represents the on-wire format in HTTP field values.

In summary:

* There are three top-level types that a HTTP header or trailer field can be defined as; Lists, Dictionaries, and Items.

* Lists and Dictionaries are containers; their members can be Items or Inner Lists (which are themselves lists of items).

* Both Items and Inner Lists can be parameterised with key/value pairs.


## Lists {#list}

Lists are arrays of zero or more members, each of which can be an item ({{item}}) or an inner list ({{inner-list}}), both of which can be parameterised ({{param}}).

The ABNF for lists in HTTP fields is:

~~~ abnf
sh-list       = list-member *( *SP "," *SP list-member )
list-member   = sh-item / inner-list
~~~

Each member is separated by a comma and optional whitespace. For example, a header field whose value is defined as a list of strings could look like:

~~~ example
Example-StrListHeader: "foo", "bar", "It was the best of times."
~~~

An empty list is denoted by not serialising the header at all.

Note that lists can have their members split across multiple lines inside a header or trailer section, as per Section 3.2.2 of {{?RFC7230}}; for example, the following are equivalent:

~~~ example
Example-Hdr: foo, bar
~~~

and

~~~ example
Example-Hdr: foo
Example-Hdr: bar
~~~

However, individual members of a list cannot be safely split between across lines; see {{text-parse}} for details.

Parsers MUST support lists containing at least 1024 members. Field specifications can constrain the types and cardinality of individual list values as they require.


### Inner Lists {#inner-list}

An inner list is an array of zero or more items ({{item}}). Both the individual items and the inner-list itself can be parameterised ({{param}}).

The ABNF for inner-lists is:

~~~ abnf
inner-list    = "(" *SP [ sh-item *( 1*SP sh-item ) *SP ] ")"
                *parameter
~~~

Inner lists are denoted by surrounding parenthesis, and have their values delimited by a single space. A header field whose value is defined as a list of inner-lists of strings could look like:

~~~ example
Example-StrListListHeader: ("foo" "bar"), ("baz"), ("bat" "one"), ()
~~~

Note that the last member in this example is an empty inner list.

A header field whose value is defined as a list of inner-lists with parameters at both levels could look like:

~~~ example
Example-ListListParam: ("foo"; a=1;b=2);lvl=5, ("bar" "baz");lvl=1
~~~

Parsers MUST support inner-lists containing at least 256 members. Field specifications can constrain the types and cardinality of individual inner-list members as they require.


### Parameters {#param}

Parameters are an ordered map of key-values pairs that are associated with an item ({{item}}) or inner-list ({{inner-list}}). The keys are unique within the scope of a map of parameters, and the values are bare items (i.e., they themselves cannot be parameterised; see {{item}}).

The ABNF for parameters is:

~~~ abnf
parameter     = ";" *SP param-name [ "=" param-value ]
param-name    = key
key           = lcalpha *( lcalpha / DIGIT / "_" / "-" / "." / "*" )
lcalpha       = %x61-7A ; a-z
param-value   = bare-item
~~~

Parameters are separated from their item or inner-list and each other by semicolons. For example:

~~~ example
Example-ParamListHeader: abc;a=1;b=2; cde_456, (ghi;jk=4 l);q="9";r=w
~~~

Parameters whose value is Boolean true MUST omit that value when serialised. For example:

~~~ example
Example-IntHeader: 1; a; b=?0
~~~

Note that this requirement is only on serialisation; parsers are still required to correctly handle the true value when it appears in parameters.

Parsers MUST support at least 256 parameters on an item or inner-list, and support parameter keys with at least 64 characters. Field specifications can constrain the types and cardinality of individual parameter names and values as they require.


## Dictionaries {#dictionary}

Dictionaries are ordered maps of name-value pairs, where the names are short, textual strings and the values are items ({{item}}) or arrays of items, both of which can be parameterised ({{param}}). There can be zero or more members, and their names are unique in the scope of the dictionary they occur within.

Implementations MUST provide access to dictionaries both by index and by name. Specifications MAY use either means of accessing the members.

The ABNF for dictionaries is:

~~~ abnf
sh-dictionary  = dict-member *( *SP "," *SP dict-member )
dict-member    = member-name [ "=" member-value ]
member-name    = key
member-value   = sh-item / inner-list
~~~

Members are separated by a comma with optional whitespace, while names and values are separated by "=" (without whitespace). For example:

~~~ example
Example-DictHeader: en="Applepie", da=:w4ZibGV0w6ZydGU=:
~~~

Members whose value is Boolean true MUST omit that value when serialised, unless it has parameters. For example, here both "b" and "c" are true, but "c"'s value is serialised because it has parameters:

~~~ example
Example-DictHeader: a=?0, b, c=?1; foo=bar
~~~

Note that this requirement is only on serialisation; parsers are still required to correctly handle the true value when it appears in dictionary values.

A dictionary with a member whose value is an inner-list of tokens:

~~~ example
Example-DictListHeader: rating=1.5, feelings=(joy sadness)
~~~

A dictionary with a mix of singular and list values, some with parameters:

~~~ example
Example-MixDict: a=(1 2), b=3, c=4;aa=bb, d=(5 6);valid
~~~

As with lists, an empty dictionary is represented by omitting the entire header field.

Typically, a field specification will define the semantics of dictionaries by specifying the allowed type(s) for individual member names, as well as whether their presence is required or optional. Recipients MUST ignore names that are undefined or unknown, unless the field's specification specifically disallows them.

Note that dictionaries can have their members split across multiple lines inside a header or trailer section; for example, the following are equivalent:

~~~ example
Example-Hdr: foo=1, bar=2
~~~

and

~~~ example
Example-Hdr: foo=1
Example-Hdr: bar=2
~~~

However, individual members of a dictionary cannot be safely split between lines; see {{text-parse}} for details.

Parsers MUST support dictionaries containing at least 1024 name/value pairs, and names with at least 64 characters.


## Items {#item}

An item can be a integer ({{integer}}), decimal ({{decimal}}), string ({{string}}), token ({{token}}), byte sequence ({{binary}}), or Boolean ({{boolean}}). It can have associated parameters ({{param}}).

The ABNF for items is:

~~~ abnf
sh-item   = bare-item *parameter
bare-item = sh-integer / sh-decimal / sh-string / sh-token / sh-binary
            / sh-boolean
~~~

For example, a header field that is defined to be an Item that is an integer might look like:

~~~ example
Example-IntItemHeader: 5
~~~

or with parameters:

~~~ example
Example-IntItemHeader: 5; foo=bar
~~~


### Integers {#integer}

Integers have a range of −999,999,999,999,999 to 999,999,999,999,999 inclusive (i.e., up to fifteen digits, signed), for IEEE 754 compatibility ({{IEEE754}}).

The ABNF for integers is:

~~~ abnf
sh-integer = ["-"] 1*15DIGIT
~~~

For example:

~~~ example
Example-IntegerHeader: 42
~~~

Note that commas in integers are used in this section's prose only for readability; they are not valid in the wire format.


### Decimals {#decimal}

Decimals are numbers with an integer and a fractional component. The Integer component has at most 12 digits; the fractional component has at most three digits.


The ABNF for decimals is:


~~~ abnf
sh-decimal  = ["-"] 1*12DIGIT "." 1*3DIGIT
~~~

For example, a header whose value is defined as a decimal could look like:

~~~ example
Example-DecimalHeader: 4.5
~~~


### Strings {#string}

Strings are zero or more printable ASCII {{!RFC0020}} characters (i.e., the range %x20 to %x7E). Note that this excludes tabs, newlines, carriage returns, etc.

The ABNF for strings is:

~~~ abnf
sh-string = DQUOTE *(chr) DQUOTE
chr       = unescaped / escaped
unescaped = %x20-21 / %x23-5B / %x5D-7E
escaped   = "\" ( DQUOTE / "\" )
~~~

Strings are delimited with double quotes, using a backslash ("\\") to escape double quotes and backslashes. For example:

~~~ example
Example-StringHeader: "hello world"
~~~

Note that strings only use DQUOTE as a delimiter; single quotes do not delimit strings. Furthermore, only DQUOTE and "\\" can be escaped; other characters after "\\" MUST cause parsing to fail.

Unicode is not directly supported in strings, because it causes a number of interoperability issues, and -- with few exceptions -- field values do not require it.

When it is necessary for a field value to convey non-ASCII content, a byte sequence ({{binary}}) SHOULD be specified, along with a character encoding (preferably {{UTF-8}}).

Parsers MUST support strings (after any decoding) with at least 1024 characters.


### Tokens {#token}

Tokens are short textual words; their abstract model is identical to their expression in the HTTP field value serialisation.

The ABNF for tokens is:

~~~ abnf
sh-token = ( ALPHA / "\*" ) *( tchar / ":" / "/" )
~~~

Parsers MUST support tokens with at least 512 characters.

Note that a Structured Header token allows the characters as the "token" ABNF rule defined in {{?RFC7230}}, with the exceptions that the first character is required to be either ALPHA or "\*", and ":" and "/" are also allowed in subsequent characters.


### Byte Sequences {#binary}

Byte sequences can be conveyed in Structured Headers.

The ABNF for a byte sequence is:

~~~ abnf
sh-binary = ":" *(base64) ":"
base64    = ALPHA / DIGIT / "+" / "/" / "="
~~~

A byte sequence is delimited with colons and encoded using base64 ({{!RFC4648}}, Section 4). For example:

~~~ example
Example-BinaryHdr: :cHJldGVuZCB0aGlzIGlzIGJpbmFyeSBjb250ZW50Lg==:
~~~

Parsers MUST support byte sequences with at least 16384 octets after decoding.


### Booleans {#boolean}

Boolean values can be conveyed in Structured Headers.

The ABNF for a Boolean is:

~~~ abnf
sh-boolean = "?" boolean
boolean    = "0" / "1"
~~~

A boolean is indicated with a leading "?" character followed by a "1" for a true value or "0" for false. For example:

~~~ example
Example-BoolHdr: ?1
~~~


# Working With Structured Headers in HTTP {#text}

This section defines how to serialize and parse Structured Headers in field values, and protocols compatible with them (e.g., in HTTP/2 {{?RFC7540}} before HPACK {{?RFC7541}} is applied).

## Serializing Structured Headers {#text-serialize}

Given a structure defined in this specification, return an ASCII string suitable for use in a HTTP field value.

1. If the structure is a Dictionary or List and its value is empty (i.e., it has no members), do not serialize the field at all (i.e., omit both the field-name and field-value).
2. If the structure is a Dictionary, let output_string be the result of running Serializing a Dictionary ({{ser-dictionary}}) with the structure.
3. Else if the structure is a List, let output_string be the result of running Serializing a List ({{ser-list}}) with the structure.
4. Else if the structure is an Item, let output_string be the result of running Serializing an Item ({{ser-item}}) with the structure.
5. Else, fail serialisation.
6. Return output_string converted into an array of bytes, using ASCII encoding {{!RFC0020}}.



### Serializing a List {#ser-list}

Given an array of (member_value, parameters) tuples as input_list, return an ASCII string suitable for use in a HTTP field value.

1. Let output be an empty string.
2. For each (member_value, parameters) of input_list:
   1. If member_value is an array, append the result of running Serialising an Inner List ({{ser-innerlist}}) with (member_value, parameters) to output.
   2. Otherwise, append the result of running Serializing an Item ({{ser-item}}) with (member_value, parameters) to output.
   3. If more member_values remain in input_list:
      1. Append "," to output.
      2. Append a single SP to output.
3. Return output.

#### Serialising an Inner List {#ser-innerlist}

Given an array of (member_value, parameters) tuples as inner_list, and parameters as list_parameters, return an ASCII string suitable for use in a HTTP field value.

1. Let output be the string "(".
2. For each (member_value, parameters) of inner_list:
   1. Append the result of running Serializing an Item ({{ser-item}}) with (member_value, parameters) to output.
   2. If more values remain in inner_list, append a single SP to output.
3. Append ")" to output.
4. Append the result of running Serializing Parameters {{ser-params}} with list_parameters to output.
5. Return output.

#### Serializing Parameters {#ser-params}

Given an ordered dictionary as input_parameters (each member having a param_name and a param_value), return an ASCII string suitable for use in a HTTP field value.

0. Let output be an empty string.
1. For each parameter-name with a value of param_value in input_parameters:
   1. Append ";" to output.
   2. Append the result of running Serializing a Key ({{ser-key}}) with param_name to output.
   4. If param_value is not Boolean true:
      1. Append "=" to output.
      2. Append the result of running Serializing a bare Item ({{ser-bare-item}}) with param_value to output.
2. Return output.


#### Serializing a Key {#ser-key}

Given a key as input_key, return an ASCII string suitable for use in a HTTP field value.

0. Convert input_key into a sequence of ASCII characters; if conversion fails, fail serialization.
1. If input_key contains characters not in lcalpha, DIGIT, "\_", "-", ".", or "\*" fail serialisation.
2. If the first character of input_key is not lcalpha, fail parsing.
3. Let output be an empty string.
4. Append input_key to output.
5. Return output.


### Serializing a Dictionary {#ser-dictionary}

Given an ordered dictionary as input_dictionary (each member having a member_name and a tuple value of (member_value, parameters)), return an ASCII string suitable for use in a HTTP field value.

1. Let output be an empty string.
2. For each member_name with a value of (member_value, parameters) in input_dictionary:
   1. Append the result of running Serializing a Key ({{ser-key}}) with member's member_name to output.
3. If member_value is not Boolean true or parameters is not empty:
   1. Append "=" to output.
      2. If member_value is an array, append the result of running Serialising an Inner List ({{ser-innerlist}}) with (member_value, parameters) to output.
      3. Otherwise, append the result of running Serializing an Item ({{ser-item}}) with (member_value, parameters) to output.
4. If more members remain in input_dictionary:
      1. Append "," to output.
      2. Append a single SP to output.
3. Return output.


### Serializing an Item {#ser-item}

Given an item bare_item and parameters item_parameters as input, return an ASCII string suitable for use in a HTTP field value.

1. Let output be an empty string.
2. Append the result of running Serializing a Bare Item {{ser-bare-item}} with bare_item to output.
3. Append the result of running Serializing Parameters {{ser-params}} with item_parameters to output.
4. Return output.


#### Serialising a Bare Item {#ser-bare-item}

Given an item as input_item, return an ASCII string suitable for use in a HTTP field value.

1. If input_item is an integer, return the result of running Serializing an Integer ({{ser-integer}}) with input_item.
2. If input_item is a decimal, return the result of running Serializing a Decimal ({{ser-decimal}}) with input_item.
3. If input_item is a string, return the result of running Serializing a String ({{ser-string}}) with input_item.
4. If input_item is a token, return the result of running Serializing a Token ({{ser-token}}) with input_item.
5. If input_item is a Boolean, return the result of running Serializing a Boolean ({{ser-boolean}}) with input_item.
6. If input_item is a byte sequence, return the result of running Serializing a Byte Sequence ({{ser-binary}}) with input_item.
7. Otherwise, fail serialisation.


### Serializing an Integer {#ser-integer}

Given an integer as input_integer, return an ASCII string suitable for use in a HTTP field value.

0. If input_integer is not an integer in the range of −999,999,999,999,999 to 999,999,999,999,999 inclusive, fail serialisation.
1. Let output be an empty string.
2. If input_integer is less than (but not equal to) 0, append "-" to output.
3. Append input_integer's numeric value represented in base 10 using only decimal digits to output.
4. Return output.


### Serializing a Decimal {#ser-decimal}

Given a decimal number as input_decimal, return an ASCII string suitable for use in a HTTP field value.

1. If input_decimal is not a decimal number, fail serialisation.
2. If input_decimal has more than three significant digits to the right of the decimal point, round it to three decimal places, rounding the final digit to the nearest value, or to the even value if it is equidistant.
3. If input_decimal has more than 12 significant digits to the left of the decimal point after rounding, fail serialisation.
4. Let output be an empty string.
5. If input_decimal is less than (but not equal to) 0, append "-" to output.
6. Append input_decimal's integer component represented in base 10 (using only decimal digits) to output; if it is zero, append "0".
7. Append "." to output.
8. If input_decimal's fractional component is zero, append "0" to output.
9. Otherwise, append the significant digits of input_decimal's fractional component represented in base 10 (using only decimal digits) to output.
10. Return output.


### Serializing a String {#ser-string}

Given a string as input_string, return an ASCII string suitable for use in a HTTP field value.

0. Convert input_string into a sequence of ASCII characters; if conversion fails, fail serialization.
1. If input_string contains characters in the range %x00-1f or %x7f (i.e., not in VCHAR or SP), fail serialisation.
2. Let output be an empty string.
3. Append DQUOTE to output.
4. For each character char in input_string:
   1. If char is "\\" or DQUOTE:
      1. Append "\\" to output.
   2. Append char to output.
5. Append DQUOTE to output.
6. Return output.


### Serializing a Token {#ser-token}

Given a token as input_token, return an ASCII string suitable for use in a HTTP field value.

0. Convert input_token into a sequence of ASCII characters; if conversion fails, fail serialization.
1. If the first character of input_token is not ALPHA or "\*", or the remaining portion contains a character not in tchar, ":" or "/", fail serialisation.
2. Let output be an empty string.
3. Append input_token to output.
4. Return output.


### Serializing a Byte Sequence {#ser-binary}

Given a byte sequence as input_bytes, return an ASCII string suitable for use in a HTTP field value.

0. If input_bytes is not a sequence of bytes, fail serialisation.
1. Let output be an empty string.
2. Append ":" to output.
3. Append the result of base64-encoding input_bytes as per {{!RFC4648}}, Section 4, taking account of the requirements below.
4. Append ":" to output.
5. Return output.

The encoded data is required to be padded with "=", as per {{!RFC4648}}, Section 3.2.

Likewise, encoded data SHOULD have pad bits set to zero, as per {{!RFC4648}}, Section 3.5, unless it is not possible to do so due to implementation constraints.


### Serializing a Boolean {#ser-boolean}

Given a Boolean as input_boolean, return an ASCII string suitable for use in a HTTP field value.

0. If input_boolean is not a boolean, fail serialisation.
1. Let output be an empty string.
2. Append "?" to output.
3. If input_boolean is true, append "1" to output.
4. If input_boolean is false, append "0" to output.
5. Return output.


## Parsing Fields into Structured Headers {#text-parse}

When a receiving implementation parses HTTP fields that are known to be Structured Headers, it is important that care be taken, as there are a number of edge cases that can cause interoperability or even security problems. This section specifies the algorithm for doing so.

Given an array of bytes input_bytes that represents the chosen field's field-value (which is empty if that field is not present), and field_type (one of "dictionary", "list", or "item"), return the parsed header value.

0. Convert input_bytes into an ASCII string input_string; if conversion fails, fail parsing.
1. Discard any leading SP characters from input_string.
2. If field_type is "list", let output be the result of running Parsing a List ({{parse-list}}) with input_string.
3. If field_type is "dictionary", let output be the result of running Parsing a Dictionary ({{parse-dictionary}}) with input_string.
4. If field_type is "item", let output be the result of running Parsing an Item ({{parse-item}}) with input_string.
5. Discard any leading SP characters from input_string.
6. If input_string is not empty, fail parsing.
7. Otherwise, return output.

When generating input_bytes, parsers MUST combine all lines in the same section (header or trailer) that case-insensitively match the field name into one comma-separated field-value, as per {{?RFC7230}}, Section 3.2.2; this assures that the entire field value is processed correctly.

For Lists and Dictionaries, this has the effect of correctly concatenating all of the field's lines, as long as individual members of the top-level data structure are not split across multiple header instances.

Strings split across multiple field lines will have unpredictable results, because comma(s) and whitespace inserted upon combination will become part of the string output by the parser. Since concatenation might be done by an upstream intermediary, the results are not under the control of the serializer or the parser.

Tokens, Integers, Decimals and Byte Sequences cannot be split across multiple field lines because the inserted commas will cause parsing to fail.

If parsing fails -- including when calling another algorithm -- the entire field value MUST be ignored (i.e., treated as if the field were not present in the section). This is intentionally strict, to improve interoperability and safety, and specifications referencing this document are not allowed to loosen this requirement.

Note that this requirement does not apply to an implementation that is not parsing the field; for example, an intermediary is not required to strip a failing header field from a message before forwarding it.


### Parsing a List {#parse-list}

Given an ASCII string as input_string, return an array of (item_or_inner_list, parameters) tuples. input_string is modified to remove the parsed value.

1. Let members be an empty array.
2. While input_string is not empty:
   1. Append the result of running Parsing an Item or Inner List ({{parse-item-or-list}}) with input_string to members.
   2. Discard any leading SP characters from input_string.
   3. If input_string is empty, return members.
   4. Consume the first character of input_string; if it is not ",", fail parsing.
   5. Discard any leading SP characters from input_string.
   6. If input_string is empty, there is a trailing comma; fail parsing.
3. No structured data has been found; return members (which is empty).


#### Parsing an Item or Inner List {#parse-item-or-list}

Given an ASCII string as input_string, return the tuple (item_or_inner_list, parameters), where item_or_inner_list can be either a single bare item, or an array of (bare_item, parameters) tuples. input_string is modified to remove the parsed value.

1. If the first character of input_string is "(", return the result of running Parsing an Inner List ({{parse-innerlist}}) with input_string.
2. Return the result of running Parsing an Item ({{parse-item}}) with input_string.


#### Parsing an Inner List {#parse-innerlist}

Given an ASCII string as input_string, return the tuple (inner_list, parameters), where inner_list is an array of (bare_item, parameters) tuples. input_string is modified to remove the parsed value.

1. Consume the first character of input_string; if it is not "(", fail parsing.
2. Let inner_list be an empty array.
3. While input_string is not empty:
   1. Discard any leading SP characters from input_string.
   2. If the first character of input_string is ")":
      1. Consume the first character of input_string.
      2. Let parameters be the result of running Parsing Parameters ({{parse-param}}) with input_string.
      2. Return the tuple (inner_list, parameters).
   3. Let item be the result of running Parsing an Item ({{parse-item}}) with input_string.
   4. Append item to inner_list.
   5. If the first character of input_string is not SP or ")", fail parsing.
4. The end of the inner list was not found; fail parsing.


### Parsing a Dictionary {#parse-dictionary}

Given an ASCII string as input_string, return an ordered map whose values are (item_or_inner_list, parameters) tuples. input_string is modified to remove the parsed value.

1. Let dictionary be an empty, ordered map.
2. While input_string is not empty:
   1. Let this_key be the result of running Parsing a Key ({{parse-key}}) with input_string.
   2. If the first character of input_string is "=":
       1. Consume the first character of input_string.
       2. Let member be the result of running Parsing an Item or Inner List ({{parse-item-or-list}}) with input_string.
   3. Otherwise:
      1. Let value be Boolean true.
      2. Let parameters be an empty, ordered map.
      3. Let member be the tuple (value, parameters).
   4. Add name this_key with value member to dictionary. If dictionary already contains a name this_key (comparing character-for-character), overwrite its value.
   5. Discard any leading SP characters from input_string.
   6. If input_string is empty, return dictionary.
   7. Consume the first character of input_string; if it is not ",", fail parsing.
   8. Discard any leading SP characters from input_string.
   9. If input_string is empty, there is a trailing comma; fail parsing.
3. No structured data has been found; return dictionary (which is empty).


### Parsing an Item {#parse-item}

Given an ASCII string as input_string, return a (bare_item, parameters) tuple. input_string is modified to remove the parsed value.

1. Let bare_item be the result of running Parsing a Bare Item ({{parse-bare-item}}) with input_string.
2. Let parameters be the result of running Parsing Parameters ({{parse-param}}) with input_string.
3. Return the tuple (bare_item, parameters).


#### Parsing a Bare Item {#parse-bare-item}

Given an ASCII string as input_string, return a bare item. input_string is modified to remove the parsed value.

1. If the first character of input_string is a "-" or a DIGIT, return the result of running Parsing a Number ({{parse-number}}) with input_string.
2. If the first character of input_string is a DQUOTE, return the result of running Parsing a String ({{parse-string}}) with input_string.
3. If the first character of input_string is ":", return the result of running Parsing a Byte Sequence ({{parse-binary}}) with input_string.
4. If the first character of input_string is "?", return the result of running Parsing a Boolean ({{parse-boolean}}) with input_string.
5. If the first character of input_string is an ALPHA or "\*", return the result of running Parsing a Token ({{parse-token}}) with input_string.
6. Otherwise, the item type is unrecognized; fail parsing.

#### Parsing Parameters {#parse-param}

Given an ASCII string as input_string, return an ordered map whose values are bare items. input_string is modified to remove the parsed value.

1. Let parameters be an empty, ordered map.
2. While input_string is not empty:
   1. If the first character of input_string is not ";", exit the loop.
   2. Consume a ";" character from the beginning of input_string.
   3. Discard any leading SP characters from input_string.
   4. let param_name be the result of running Parsing a Key ({{parse-key}}) with input_string.
   5. Let param_value be Boolean true.
   6. If the first character of input_string is "=":
      1. Consume the "=" character at the beginning of input_string.
      2. Let param_value be the result of running Parsing a Bare Item ({{parse-bare-item}}) with input_string.
   7. Append key param_name with value param_value to parameters. If parameters already contains a name param_name (comparing character-for-character), overwrite its value.
3. Return parameters.

#### Parsing a Key {#parse-key}

Given an ASCII string as input_string, return a key. input_string is modified to remove the parsed value.

1. If the first character of input_string is not lcalpha, fail parsing.
2. Let output_string be an empty string.
3. While input_string is not empty:
   1. If the first character of input_string is not one of lcalpha, DIGIT, "\_", "-", ".", or "\*", return output_string.
   2. Let char be the result of removing the first character of input_string.
   3. Append char to output_string.
4. Return output_string.


### Parsing a Number {#parse-number}

Given an ASCII string as input_string, return a number. input_string is modified to remove the parsed value.

NOTE: This algorithm parses both Integers ({{integer}}) and Decimals ({{decimal}}), and returns the corresponding structure.

1. Let type be "integer".
2. Let sign be 1.
3. Let input_number be an empty string.
4. If the first character of input_string is "-", consume it and set sign to -1.
5. If input_string is empty, there is an empty integer; fail parsing.
6. If the first character of input_string is not a DIGIT, fail parsing.
7. While input_string is not empty:
   1. Let char be the result of consuming the first character of input_string.
   2. If char is a DIGIT, append it to input_number.
   3. Else, if type is "integer" and char is ".":
      1. If input_number contains more than 12 characters, fail parsing.
      2. Otherwise, append char to input_number and set type to "decimal".
   4. Otherwise, prepend char to input_string, and exit the loop.
   5. If type is "integer" and input_number contains more than 15 characters, fail parsing.
   6. If type is "decimal" and input_number contains more than 16 characters, fail parsing.
8. If type is "integer":
   1. Parse input_number as an integer and let output_number be the product of the result and sign.
   2. If output_number is outside the range −999,999,999,999,999 to 999,999,999,999,999 inclusive, fail parsing.
9. Otherwise:
   1. If the final character of input_number is ".", fail parsing.
   2. If the number of characters after "." in input_number is greater than three, fail parsing.
   2. Parse input_number as a decimal number and let output_number be the product of the result and sign.
0. Return output_number.


### Parsing a String {#parse-string}

Given an ASCII string as input_string, return an unquoted string. input_string is modified to remove the parsed value.

1. Let output_string be an empty string.
2. If the first character of input_string is not DQUOTE, fail parsing.
3. Discard the first character of input_string.
4. While input_string is not empty:
   1. Let char be the result of consuming the first character of input_string.
   2. If char is a backslash ("\\"):
      1. If input_string is now empty, fail parsing.
      2. Let next_char be the result of consuming the first character of input_string.
      3. If next_char is not DQUOTE or "\\", fail parsing.
      4. Append next_char to output_string.
   3. Else, if char is DQUOTE, return output_string.
   4. Else, if char is in the range %x00-1f or %x7f (i.e., is not in VCHAR or SP), fail parsing.
   5. Else, append char to output_string.
5. Reached the end of input_string without finding a closing DQUOTE; fail parsing.


### Parsing a Token {#parse-token}

Given an ASCII string as input_string, return a token. input_string is modified to remove the parsed value.

1. If the first character of input_string is not ALPHA or "\*", fail parsing.
2. Let output_string be an empty string.
3. While input_string is not empty:
   1. If the first character of input_string is not in tchar, ":" or "/", return output_string.
   2. Let char be the result of consuming the first character of input_string.
   3. Append char to output_string.
4. Return output_string.


### Parsing a Byte Sequence {#parse-binary}

Given an ASCII string as input_string, return a byte sequence. input_string is modified to remove the parsed value.

1. If the first character of input_string is not ":", fail parsing.
2. Discard the first character of input_string.
3. If there is not a ":" character before the end of input_string, fail parsing.
4. Let b64_content be the result of consuming content of input_string up to but not including the first instance of the character ":".
5. Consume the ":" character at the beginning of input_string.
6. If b64_content contains a character not included in ALPHA, DIGIT, "+", "/" and "=", fail parsing.
7. Let binary_content be the result of Base 64 Decoding {{!RFC4648}} b64_content, synthesizing padding if necessary (note the requirements about recipient behaviour below).
8. Return binary_content.

Because some implementations of base64 do not allow reject of encoded data that is not properly "=" padded (see {{!RFC4648}}, Section 3.2), parsers SHOULD NOT fail when it is not present, unless they cannot be configured to do so.

Because some implementations of base64 do not allow rejection of encoded data that has non-zero pad bits (see {{!RFC4648}}, Section 3.5), parsers SHOULD NOT fail when it is present, unless they cannot be configured to do so.

This specification does not relax the requirements in {{!RFC4648}}, Section 3.1 and 3.3; therefore, parsers MUST fail on characters outside the base64 alphabet, and on line feeds in encoded data.


### Parsing a Boolean {#parse-boolean}

Given an ASCII string as input_string, return a Boolean. input_string is modified to remove the parsed value.

1. If the first character of input_string is not "?", fail parsing.
2. Discard the first character of input_string.
3. If the first character of input_string matches "1", discard the first character, and return true.
4. If the first character of input_string matches "0", discard the first character, and return false.
5. No value has matched; fail parsing.


# IANA Considerations

This draft has no actions for IANA.

# Security Considerations

The size of most types defined by Structured Headers is not limited; as a result, extremely large fields could be an attack vector (e.g., for resource consumption). Most HTTP implementations limit the sizes of individual fields as well as the overall header or trailer section size to mitigate such attacks.

It is possible for parties with the ability to inject new HTTP fields to change the meaning
of a Structured Header. In some circumstances, this will cause parsing to fail, but it is not possible to reliably fail in all such circumstances.

--- back

# Acknowledgements

Many thanks to Matthew Kerwin for his detailed feedback and careful consideration during the development of this specification.


# Frequently Asked Questions {#faq}

## Why not JSON?

Earlier proposals for Structured Headers were based upon JSON {{?RFC8259}}. However, constraining its use to make it suitable for HTTP header fields required senders and recipients to implement specific additional handling.

For example, JSON has specification issues around large numbers and objects with duplicate members. Although advice for avoiding these issues is available (e.g., {{?RFC7493}}), it cannot be relied upon.

Likewise, JSON strings are by default Unicode strings, which have a number of potential interoperability issues (e.g., in comparison). Although implementers can be advised to avoid non-ASCII content where unnecessary, this is difficult to enforce.

Another example is JSON's ability to nest content to arbitrary depths. Since the resulting memory commitment might be unsuitable (e.g., in embedded and other limited server deployments), it's necessary to limit it in some fashion; however, existing JSON implementations have no such limits, and even if a limit is specified, it's likely that some field definition will find a need to violate it.

Because of JSON's broad adoption and implementation, it is difficult to impose such additional constraints across all implementations; some deployments would fail to enforce them, thereby harming interoperability. In short, if it looks like JSON, people will be tempted to use a JSON parser / serialiser on field values.

Since a major goal for Structured Headers is to improve interoperability and simplify implementation, these concerns led to a format that requires a dedicated parser and serializer.

Additionally, there were widely shared feelings that JSON doesn't "look right" in HTTP fields.

## Structured Headers don't "fit" my data.

Structured Headers intentionally limits the complexity of data structures, to assure that it can be processed in a performant manner with little overhead. This means that work is necessary to fit some data types into them.

Sometimes, this can be achieved by creating limited substructures in field values, and/or using more than one field. For example, consider:

~~~ example
Example-Thing: name="Widget", cost=89.2, descriptions=(foo bar)
Example-Description: foo; url="https://example.net"; context=123,
                     bar; url="https://example.org"; context=456
~~~

Since the description contains an array of key/value pairs, we use a List to represent them, with the token for each item in the array used to identify it in the "descriptions" member of the Example-Thing dictionary header.

When specifying more than one field, it's important to remember to describe what a processor's behaviour should be when one of the fields is missing.

If you need to fit arbitrarily complex data into a field value, Structured Headers is probably a poor fit for your use case.

# Implementation Notes

A generic implementation of this specification should expose the top-level parse ({{text-parse}}) and serialize ({{text-serialize}}) functions. They need not be functions; for example, it could be implemented as an object, with methods for each of the different top-level types.

For interoperability, it's important that generic implementations be complete and follow the algorithms closely; see {{strict}}. To aid this, a common test suite is being maintained by the community at <https://github.com/httpwg/structured-header-tests>.

Implementers should note that dictionaries and parameters are order-preserving maps. Some fields may not convey meaning in the ordering of these data types, but it should still be exposed so that applications which need to use it will have it available.

Likewise, implementations should note that it's important to preserve the distinction between tokens and strings. While most programming languages have native types that map to the other types well, it may be necessary to create a wrapper "token" object or use a parameter on functions to assure that these types remain separate.

The serialisation algorithm is defined in a way that it is not strictly limited to the data types defined in {{types}} in every case. For example, Decimals are designed to take broader input and round to allowed values.


# Changes

_RFC Editor: Please remove this section before publication._

## Since draft-ietf-httpbis-header-structure-15

* Editorial improvements.
* Use HTTP field terminology more consistently, in line with recent changes to HTTP-core.
* String length requirements apply to decoded strings (#1051).
* Correctly round decimals in serialisation (#1043).
* Clarify input to serialisation algorithms (#1055).


## Since draft-ietf-httpbis-header-structure-14

* Editorial improvements.
* Allow empty dictionary values (#992).
* Change value of omitted parameter value to True (#995).
* Explain more about splitting dictionaries and lists across header instances (#997).
* Disallow HTAB, replace OWS with spaces (#998).
* Change byte sequence delimiters from "\*" to ":" (#991).
* Allow tokens to start with "\*" (#991).
* Change Floats to fixed-precision Decimals (#982).
* Round the fractional component of decimal, rather than truncating it (#982).
* Handle duplicate dictionary and parameter keys by overwriting their values, rather than failing (#997).
* Allow "." in key (#1027).
* Check first character of key in serialisation (#1037).
* Talk about greasing headers (#1015).


## Since draft-ietf-httpbis-header-structure-13

* Editorial improvements.
* Define "structured header name" and "structured header value" terms (#908).
* Corrected text about valid characters in strings (#931).
* Removed most instances of the word "textual", as it was redundant (#915).
* Allowed parameters on Items and Inner Lists (#907).
* Expand the range of characters in token (#961).
* Disallow OWS before ";" delimiter in parameters (#961).

## Since draft-ietf-httpbis-header-structure-12

* Editorial improvements.
* Reworked float serialisation (#896).
* Don't add a trailing space in inner-list (#904).


## Since draft-ietf-httpbis-header-structure-11

* Allow \* in key (#844).
* Constrain floats to six digits of precision (#848).
* Allow dictionary members to have parameters (#842).


## Since draft-ietf-httpbis-header-structure-10

* Update abstract (#799).
* Input and output are now arrays of bytes (#662).
* Implementations need to preserve difference between token and string (#790).
* Allow empty dictionaries and lists (#781).
* Change parameterized lists to have primary items (#797).
* Allow inner lists in both dictionaries and lists; removes lists of lists (#816).
* Subsume Parameterised Lists into Lists (#839).


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
