---
title: Retrofit Structured Fields for HTTP
abbrev: Retrofit Structured Fields
docname: draft-ietf-httpbis-retrofit-latest
date: {DATE}
category: std

ipr: trust200902
keyword:
 - structured fields
 - http

stand_alone: yes
smart_quotes: no
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/retrofit
github-issue-label: retrofit

author:
 -
    name: Mark Nottingham
    organization:
    postal:
      - Prahran
    country: Australia
    email: mnot@mnot.net
    uri: https://www.mnot.net/

normative:
  RFC2119:
  HTTP: I-D.ietf-httpbis-semantics
  STRUCTURED-FIELDS: RFC8941

informative:


--- abstract

This specification defines how a selection of existing HTTP fields can be handled as Structured Fields.


--- middle

# Introduction

Structured Field Values for HTTP {{STRUCTURED-FIELDS}} introduced a data model with associated parsing and serialization algorithms for use by new HTTP field values. Header fields that are defined as Structured Fields can realise a number of benefits, including:

* Improved interoperability and security: precisely defined parsing and serialisation algorithms are typically not available for fields defined with just ABNF and/or prose.
* Reuse of common implementations: many parsers for other fields are specific to a single field or a small family of fields
* Canonical form: because a deterministic serialisation algorithm is defined for each type, Structure Fields have a canonical representation
* Enhanced API support: a regular data model makes it easier to expose field values as a native data structure in implementations
* Alternative serialisations: While {{STRUCTURED-FIELDS}} defines a textual serialisation of that data model, other, more efficient serialisations of the underlying data model are also possible.

However, a field needs to be defined as a Structured Field for these benefits to be realised. Many existing fields are not, making up the bulk of header and trailer fields seen in HTTP traffic on the internet.

This specification defines how a selection of existing HTTP fields can be handled as Structured Fields, so that these benefits can be realised -- thereby making them Retrofit Structured Fields.

It does so using two techniques. {{compatible}} lists compatible fields -- those that can be handled as if they were Structured Fields due to the similarity of their defined syntax to that in Structured Fields. {{mapped}} lists mapped fields -- those whose syntax needs to be transformed into an underlying data model which is then mapped into that defined by Structured Fields.

While implementations can parse and serialise compatible fields as Structured Fields subject to the caveats in {{compatible}}, a sender cannot generate mapped fields from {{mapped}} and expect them to be understood and acted upon by the recipient without prior negotiation. This specification does not define such a mechanism.


## Notational Conventions

{::boilerplate bcp14-tagged}


# Compatible Fields {#compatible}

The HTTP fields listed in {{compatible-fields}} can usually have their values handled as Structured Fields according to the listed parsing and serialisation algorithms in {{STRUCTURED-FIELDS}}, subject to the listed caveats.

The listed types are chosen for compatibility with the defined syntax of the field as well as with actual internet traffic. However, not all instances of these fields will successfully parse. This might be because the field value is clearly invalid, or it might be because it is valid but not parseable as a Structured Field.

An application using this specification will need to consider how to handle such field values. Depending on its requirements, it might be advisable to reject such values, treat them as opaque strings, or attempt to recover a structured value from them in an ad hoc fashion.

| Field Name                       | Structured Type |
|----------------------------------|-----------------|
| Accept                           | List            |
| Accept-Encoding                  | List            |
| Accept-Language                  | List            |
| Accept-Patch                     | List            |
| Accept-Post                      | List            |
| Accept-Ranges                    | List            |
| Access-Control-Allow-Credentials | Item            |
| Access-Control-Allow-Headers     | List            |
| Access-Control-Allow-Methods     | List            |
| Access-Control-Allow-Origin      | Item            |
| Access-Control-Expose-Headers    | List            |
| Access-Control-Max-Age           | Item            |
| Access-Control-Request-Headers   | List            |
| Access-Control-Request-Method    | Item            |
| Age                              | Item            |
| Allow                            | List            |
| ALPN                             | List            |
| Alt-Svc                          | Dictionary      |
| Alt-Used                         | Item            |
| Cache-Control                    | Dictionary      |
| CDN-Loop                         | List            |
| Clear-Site-Data                  | List            |
| Connection                       | List            |
| Content-Encoding                 | List            |
| Content-Language                 | List            |
| Content-Length                   | List            |
| Content-Type                     | Item            |
| Cross-Origin-Resource-Policy     | Item            |
| Expect                           | Dictionary      |
| Expect-CT                        | Dictionary      |
| Forwarded                        | Dictionary      |
| Host                             | Item            |
| Keep-Alive                       | Dictionary      |
| Max-Forwards                     | Item            |
| Origin                           | Item            |
| Pragma                           | Dictionary      |
| Prefer                           | Dictionary      |
| Preference-Applied               | Dictionary      |
| Retry-After                      | Item            |
| Sec-WebSocket-Extensions         | List            |
| Sec-WebSocket-Protocol           | List            |
| Sec-WebSocket-Version            | Item            |
| Server-Timing                    | List            |
| Surrogate-Control                | Dictionary      |
| TE                               | List            |
| Timing-Allow-Origin              | List            |
| Trailer                          | List            |
| Transfer-Encoding                | List            |
| Vary                             | List            |
| X-Content-Type-Options           | Item            |
| X-Frame-Options                  | Item            |
| X-XSS-Protection                 | List            |
{:id="compatible-fields" title="Compatible Fields"}

Note the following caveats regarding compatibility:

Parameter and Dictionary keys:
: HTTP parameter names are case-insensitive (per {{Section 5.6.6 of HTTP}}), but Structured Fields require them to be all-lowercase. Although the vast majority of parameters seen in typical traffic are all-lowercase, compatibility can be improved by force-lowercasing parameters when encountered.
Likewise, many Dictionary-based fields (e.g., Cache-Control, Expect-CT, Pragma, Prefer, Preference-Applied, Surrogate-Control) have case-insensitive keys, and compatibility can be improved by force-lowercasing them.

Parameter delimitation:
: The parameters rule in HTTP (see {{Section 5.6.6 of HTTP}}) allows whitespace before the ";" delimiter, but Structured Fields does not. Compatibility can be improved by allowing such whitespace.

String quoting:
: {{Section 5.6.4 of HTTP}} allows backslash-escaping most characters in quoted strings, whereas Structured Field Strings only escapes "\\" and DQUOTE. Compatibility can be improved by unescaping other characters before processing as Strings.

Token limitations:
: In Structured Fields, tokens are required to begin with an alphabetic character or "\*", whereas HTTP tokens allow a wider range of characters. This prevents use of mapped values that begin with one of these characters. For example, media types, field names, methods, range-units, character and transfer codings that begin with a number or special character other than "*" might be valid HTTP protocol elements, but will not be able to be parsed as Structured Field Tokens.

Integer limitations:
: Structured Fields Integers can have at most 15 digits; larger values will not be able to be represented in them.

IPv6 Literals:
: Fields whose values can contain IPv6 literal addresses (such as CDN-Loop, Host, and Origin) are not compatible when those values are parsed as Structured Fields Tokens, because the brackets used to delimit them are not allowed in Tokens.

Empty Field Values:
: Empty and whitespace-only field values are considered errors in Structured Fields. For compatible fields, an empty field indicates that the field should be silently ignored.

Alt-Svc:
: Some ALPN tokens (e.g., `h3-Q43`) do not conform to key's syntax. Since the final version of HTTP/3 uses the `h3` token, this shouldn't be a long-term issue, although future tokens may again violate this assumption.

Content-Length:
: Content-Length is defined as a List because it is not uncommon for implementations to mistakenly send multiple values. See {{Section 8.6 of HTTP}} for handling requirements.

Retry-After:
: Only the delta-seconds form of Retry-After is supported; a Retry-After value containing a http-date will need to be either converted into delta-seconds or represented as a raw value.


# Mapped Fields {#mapped}

Some HTTP fields can have their values represented in Structured Fields by mapping them into its data types and then serialising the result using an alternative field name.

For example, the Date HTTP header field carries a string representing a date:

~~~ http-message
Date: Sun, 06 Nov 1994 08:49:37 GMT
~~~

Its value is more efficiently represented as an integer number of delta seconds from the Unix epoch (00:00:00 UTC on 1 January 1970, minus leap seconds). Thus, the example above would be mapped as:

~~~ http-message
SF-Date: 784072177
~~~

As in {{compatible}}, these fields are unable to represent values that are not parseable, and so an application using this specification will need to how to support such values. Typically, handling them using the original field name is sufficient.

Each field name listed below indicates a replacement field name and a means of mapping its original value into a Structured Field.


## URLs

The field names in {{url-fields}} (paired with their mapped field names) have values that can be represented as Structured Fields by considering the original field's value as a string.

| Field Name       | Mapped Field Name   |
|------------------|---------------------|
| Content-Location | SF-Content-Location |
| Location         | SF-Location         |
| Referer          | SF-Referer          |
{:id="url-fields" title="URL Fields"}

For example, a Location field could be represented as:

~~~ http-message
SF-Location: "https://example.com/foo"
~~~


## Dates

The field names in {{date-fields}} (paired with their mapped field names) have values that can be represented as Structured Fields by parsing their payload according to {{Section 5.6.7 of HTTP}} and representing the result as an integer number of seconds delta from the Unix Epoch (00:00:00 UTC on 1 January 1970, minus leap seconds).

| Field Name          | Mapped Field Name   |
|---------------------|---------------------|
| Date                | SF-Date             |
| Expires             | SF-Expires          |
| If-Modified-Since   | SF-IMS              |
| If-Unmodified-Since | SF-IUS              |
| Last-Modified       | SF-LM               |
{:id="date-fields" title="Date Fields"}

For example, an Expires field could be represented as:

~~~ http-message
SF-Expires: 1571965240
~~~

## ETags

The field value of the ETag header field can be represented as a String Structured Field by representing the entity-tag as a string, and the weakness flag as a boolean "w" parameter on it, where true indicates that the entity-tag is weak; if 0 or unset, the entity-tag is strong.

For example:

~~~ http-message
SF-ETag: "abcdef"; w=?1
~~~

If-None-Match's field value can be represented as SF-INM, which is a List of the structure described above.

For example:

~~~ http-message
SF-INM: "abcdef"; w=?1, "ghijkl"
~~~


## Links

The field value of the Link header field {{!RFC8288}} can be represented in the SF-Link List Structured Field by representing the URI-Reference as a string, and link-param as parameters.

For example:

~~~ http-message
SF-Link: "/terms"; rel="copyright"; anchor="#foo"
~~~


## Cookies

The field values of the Cookie and Set-Cookie fields {{!RFC6265}} can be represented in the SF-Cookie Structured Field (a List) and SF-Set-Cookie Structured Field (a Dictionary), respectively.

In each case, cookie names are serialized as tokens, whereas their values are serialised as Strings, unless they can be represented accurately and unambiguously using the textual representation of another structured types (e.g., an Integer or Decimal).

Set-Cookie parameters map to parameters on the appropriate SF-Set-Cookie member, with the parameter name being forced to lowercase. Set-Cookie parameter values are Strings unless a specific type is defined. This specification defines the parameter types in {{cookie-params}}.

| Parameter Name      | Structured Type     |
|---------------------|---------------------|
| Max-Age             | Integer             |
| Secure              | Boolean             |
| HttpOnly            | Boolean             |
| SameSite            | Token               |
{:id="cookie-params" title="Cookie Parameter Types"}

Note that cookies in both fields are separated by commas, not semicolons, and multiple cookies can appear in each field.

For example:

~~~ http-message
SF-Set-Cookie: lang=en-US; expires="Wed, 09 Jun 2021 10:18:14 GMT";
               samesite=Strict
SF-Cookie: SID=31d4d96e407aad42, lang=en-US
~~~


# IANA Considerations

Please add the following note to the "Hypertext Transfer Protocol (HTTP) Field Name Registry":

> The "Structured Type" column indicates the type of the field (per RFC8941), if any, and may be
> "Dictionary", "List" or "Item". A prefix of "*" indicates that it is a retrofit type (i.e., not
> natively Structured); see \[this specification].
>
> Note that field names beginning with characters other than ALPHA or "*" will not be able to be
> represented as a Structured Fields Token, and therefore may be incompatible with being mapped into
> fields that refer to it; see \[this specification].

Then, add a new column, "Structured Type", with the values from {{compatible}} assigned to the nominated registrations, prefixing each with "*" to indicate that it is a retrofit type.

Then, add the field names in {{new-fields}}, with the corresponding Structured Type as indicated, a status of "permanent" and referring to this document.

| Field Name          | Structured Type |
|---------------------|-----------------|
| SF-Content-Location | String          |
| SF-Location         | String          |
| SF-Referer          | String          |
| SF-Date             | Item            |
| SF-Expires          | Item            |
| SF-IMS              | Item            |
| SF-IUS              | Item            |
| SF-LM               | Item            |
| SF-ETag             | Item            |
| SF-INM              | List            |
| SF-Link             | List            |
| SF-Set-Cookie       | Dictionary      |
| SF-Cookie           | List            |
{:id="new-fields" title="New Fields"}

Finally, add the indicated Structured Type for each existing registry entry listed in {{existing-fields}}.

| Field Name                                | Structured Type |
|-------------------------------------------|-----------------|
| Accept-CH                                 | List            |
| Cache-Status                              | List            |
| CDN-Cache-Control                         | Dictionary      |
| Cross-Origin-Opener-Policy                | Item            |
| Cross-Origin-Opener-Policy-Report-Only    | Item            |
| Cross-Origin-Embedder-Policy              | Item            |
| Cross-Origin-Embedder-Policy-Report-Only  | Item            |
| Origin-Agent-Cluster                      | Item            |
| Priority                                  | Dictionary      |
| Proxy-Status                              | List            |
{:id="existing-fields" title="Existing Fields"}


# Security Considerations

{{compatible}} identifies existing HTTP fields that can be parsed and serialised with the algorithms defined in {{STRUCTURED-FIELDS}}. Variances from other implementations might be exploitable, particularly if they allow an attacker to target one implementation in a chain (e.g., an intermediary). However, given the considerable variance in parsers already deployed, convergence towards a single parsing algorithm is likely to have a net security benefit in the longer term.

{{mapped}} defines alternative representations of existing fields. Because downstream consumers might interpret the message differently based upon whether they recognise the alternative representation, implementations are prohibited from generating such fields unless they have negotiated support for them with their peer. This specification does not define such a mechanism, but any such definition needs to consider the implications of doing so carefully.


--- back



