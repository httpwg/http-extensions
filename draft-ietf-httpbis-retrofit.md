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

entity:
  SELF: "RFC nnnn"

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
  HTTP: RFC9110
  STRUCTURED-FIELDS: I-D.ietf-httpbis-sfbis
  COOKIES: I-D.ietf-httpbis-rfc6265bis

informative:


--- abstract

This specification nominates a selection of existing HTTP fields as having syntax that is compatible with Structured Fields, so that they can be handled as such (subject to certain caveats).

To accommodate some additional fields whose syntax is not compatible, it also defines mappings of their semantics into new Structured Fields. It does not specify how to negotiate their use.

--- middle

# Introduction

Structured Field Values for HTTP {{STRUCTURED-FIELDS}} introduced a data model with associated parsing and serialization algorithms for use by new HTTP field values. Fields that are defined as Structured Fields can realise a number of benefits, including:

* Improved interoperability and security: precisely defined parsing and serialisation algorithms are typically not available for fields defined with just ABNF and/or prose.
* Reuse of common implementations: many parsers for other fields are specific to a single field or a small family of fields.
* Canonical form: because a deterministic serialisation algorithm is defined for each type, Structure Fields have a canonical representation.
* Enhanced API support: a regular data model makes it easier to expose field values as a native data structure in implementations.
* Alternative serialisations: While {{STRUCTURED-FIELDS}} defines a textual serialisation of that data model, other, more efficient serialisations of the underlying data model are also possible.

However, a field needs to be defined as a Structured Field for these benefits to be realised. Many existing fields are not, making up the bulk of header and trailer fields seen in HTTP traffic on the internet.

This specification defines how a selection of existing HTTP fields can be handled as Structured Fields, so that these benefits can be realised -- thereby making them Retrofit Structured Fields.

It does so using two techniques. {{compatible}} lists compatible fields -- those that can be handled as if they were Structured Fields due to the similarity of their defined syntax to that in Structured Fields. {{mapped}} lists mapped fields -- those whose syntax needs to be transformed into an underlying data model which is then mapped into that defined by Structured Fields.

Note that while implementations can parse and serialise compatible fields as Structured Fields subject to the caveats in {{compatible}}, a sender cannot generate mapped fields from {{mapped}} and expect them to be understood and acted upon by the recipient without prior negotiation. This specification does not define such a mechanism.


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
| DNT                              | Item            |
| Expect                           | Dictionary      |
| Expect-CT                        | Dictionary      |
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
| Upgrade-Insecure-Requests        | Item            |
| Vary                             | List            |
| X-Content-Type-Options           | Item            |
| X-Frame-Options                  | Item            |
| X-XSS-Protection                 | List            |
{:id="compatible-fields" title="Compatible Fields"}

Note the following caveats regarding compatibility:

Error handling:
: Parsing algorithms specified (or just widely implemented) for current HTTP headers may differ from those in Structured Fields in details such as error handling. For example, HTTP specifies that repeated directives in the Cache-Control header field have a different precedence than that assigned by a Dictionary structured field (which Cache-Control is mapped to).

Parameter and Dictionary keys:
: HTTP parameter names are case-insensitive (per {{Section 5.6.6 of HTTP}}), but Structured Fields require them to be all-lowercase. Although the vast majority of parameters seen in typical traffic are all-lowercase, compatibility can be improved by force-lowercasing parameters when parsing.
Likewise, many Dictionary-based fields (e.g., Cache-Control, Expect-CT, Pragma, Prefer, Preference-Applied, Surrogate-Control) have case-insensitive keys, and compatibility can be improved by force-lowercasing them when parsing.

Parameter delimitation:
: The parameters rule in HTTP (see {{Section 5.6.6 of HTTP}}) allows whitespace before the ";" delimiter, but Structured Fields does not. Compatibility can be improved by allowing such whitespace when parsing.

String quoting:
: {{Section 5.6.4 of HTTP}} allows backslash-escaping most characters in quoted strings, whereas Structured Field Strings only escape "\\" and DQUOTE. Compatibility can be improved by unescaping other characters before parsing.

Token limitations:
: In Structured Fields, tokens are required to begin with an alphabetic character or "\*", whereas HTTP tokens allow a wider range of characters. This prevents use of mapped values that begin with one of these characters. For example, media types, field names, methods, range-units, character and transfer codings that begin with a number or special character other than "*" might be valid HTTP protocol elements, but will not be able to be represented as Structured Field Tokens.

Integer limitations:
: Structured Fields Integers can have at most 15 digits; larger values will not be able to be represented in them.

IPv6 Literals:
: Fields whose values contain IPv6 literal addresses (such as CDN-Loop, Host, and Origin) are not able to be represented as Structured Fields Tokens, because the brackets used to delimit them are not allowed in Tokens.

Empty Field Values:
: Empty and whitespace-only field values are considered errors in Structured Fields. For compatible fields, an empty field indicates that the field should be silently ignored.

Alt-Svc:
: Some ALPN tokens (e.g., `h3-Q43`) do not conform to key's syntax, and therefore cannot be represented as a Token. Since the final version of HTTP/3 uses the `h3` token, this shouldn't be a long-term issue, although future tokens may again violate this assumption.

Content-Length:
: Note that Content-Length is defined as a List because it is not uncommon for implementations to mistakenly send multiple values. See {{Section 8.6 of HTTP}} for handling requirements.

Retry-After:
: Only the delta-seconds form of Retry-After can be represented; a Retry-After value containing a http-date will need to be converted into delta-seconds to be conveyed as a Structured Field Value.


# Mapped Fields {#mapped}

Some HTTP field values have syntax that cannot be successfully parsed as Structured Fields. Instead, it is necessary to map them into a separate Structured Field with an alternative name.

For example, the Date HTTP header field carries a date:

~~~ http-message
Date: Sun, 06 Nov 1994 08:49:37 GMT
~~~

Its value would be mapped to:

~~~ http-message-new
SF-Date: @784111777
~~~

As in {{compatible}}, these fields are unable to carry values that are not valid Structured Fields, and so an application using this specification will need to how to support such values. Typically, handling them using the original field name is sufficient.

Each field name listed below indicates a replacement field name and a means of mapping its original value into a Structured Field.


## URLs

The field names in {{url-fields}} (paired with their mapped field names) have values that can be mapped into Structured Fields by treating the original field's value as a String.

| Field Name       | Mapped Field Name   |
|------------------|---------------------|
| Content-Location | SF-Content-Location |
| Location         | SF-Location         |
| Referer          | SF-Referer          |
{:id="url-fields" title="URL Fields"}

For example, this Location field

~~~ http-message
Location: https://example.com/foo
~~~

could be mapped as:

~~~ http-message
SF-Location: "https://example.com/foo"
~~~


## Dates

The field names in {{date-fields}} (paired with their mapped field names) have values that can be mapped into Structured Fields by parsing their payload according to {{Section 5.6.7 of HTTP}} and representing the result as a Date.

| Field Name          | Mapped Field Name      |
|---------------------|------------------------|
| Date                | SF-Date                |
| Expires             | SF-Expires             |
| If-Modified-Since   | SF-If-Modified-Since   |
| If-Unmodified-Since | SF-If-Unmodified-Since |
| Last-Modified       | SF-Last-Modified       |
{:id="date-fields" title="Date Fields"}

For example, an Expires field could be mapped as:

~~~ http-message-new
SF-Expires: @1659578233
~~~

## ETags

The field value of the ETag header field can be mapped into the SF-ETag Structured Field by representing the entity-tag as a String, and the weakness flag as a Boolean "w" parameter on it, where true indicates that the entity-tag is weak; if 0 or unset, the entity-tag is strong.

For example, this:

~~~ http-message
ETag: W/"abcdef"
~~~

~~~ http-message
SF-ETag: "abcdef"; w
~~~

If-None-Match's field value can be mapped into the SF-If-None-Match Structured Field, which is a List of the structure described above. When a field value contains "*", it is represented as a Token.

Likewise, If-Match's field value can be mapped into the SF-If-Match Structured Field in the same manner.


For example:

~~~ http-message
SF-If-None-Match: "abcdef"; w, "ghijkl", *
~~~


## Links

The field value of the Link header field {{!RFC8288}} can be mapped into the SF-Link List Structured Field by considering the URI-Reference as a String, and link-param as Parameters.

For example, this:

~~~ http-message
Link: </terms>; rel="copyright"; anchor="#foo"
~~~

can be mapped to:

~~~ http-message
SF-Link: "/terms"; rel="copyright"; anchor="#foo"
~~~


## Cookies

The field values of the Cookie and Set-Cookie fields {{COOKIES}} can be mapped into the SF-Cookie Structured Field (a List) and SF-Set-Cookie Structured Field (a List), respectively.

In each case, a cookie is represented as an Inner List containing two Items; the cookie name and value. The cookie name is always a String; the cookie value is a String, unless it can be successfully parsed as the textual representation of another, bare Item structured type (e.g., Byte Sequence, Decimal, Integer, Token, or Boolean).

Cookie attributes map to Parameters on the Inner List, with the parameter name being forced to lowercase. Cookie attribute values are Strings unless a specific type is defined for them. This specification defines types for existing cookie attributes in {{cookie-params}}.

| Parameter Name      | Structured Type     |
|---------------------|---------------------|
| Domain              | String              |
| HttpOnly            | Boolean             |
| Expires             | Date                |
| Max-Age             | Integer             |
| Path                | String              |
| Secure              | Boolean             |
| SameSite            | Token               |
{:id="cookie-params" title="Set-Cookie Parameter Types"}

The Expires attribute is mapped to a Date representation of parsed-cookie-date (see {{Section 5.1.1 of COOKIES}}).

For example, these unstructured fields:

~~~ http-message
Set-Cookie: lang=en-US; Expires=Wed, 09 Jun 2021 10:18:14 GMT;
               samesite=Strict; secure
Cookie: SID=31d4d96e407aad42; lang=en-US
~~~

can be mapped into:

~~~ http-message-new
SF-Set-Cookie: ("lang" "en-US"); expires=@1623233894;
               samesite=Strict; secure
SF-Cookie: ("SID" "31d4d96e407aad42"), ("lang" "en-US")
~~~


# IANA Considerations

Please add the following note to the "Hypertext Transfer Protocol (HTTP) Field Name Registry":

> A prefix of "*" in the Structured Type column indicates that it is a retrofit type (i.e., not
> natively Structured); see {{&SELF}}.

Then, add a new column, "Structured Type", with the values from {{compatible}} assigned to the nominated registrations, prefixing each with "*" to indicate that it is a retrofit type.

Then, add the field names in {{new-fields}}, with the corresponding Structured Type as indicated, a status of "permanent" and referring to this document.

| Field Name             | Structured Type |
|------------------------|-----------------|
| SF-Content-Location    | Item            |
| SF-Cookie              | List            |
| SF-Date                | Item            |
| SF-ETag                | Item            |
| SF-Expires             | Item            |
| SF-If-Match            | List            |
| SF-If-Modified-Since   | Item            |
| SF-If-None-Match       | List            |
| SF-If-Unmodified-Since | Item            |
| SF-Link                | List            |
| SF-Last-Modified       | Item            |
| SF-Location            | Item            |
| SF-Referer             | Item            |
| SF-Set-Cookie          | List            |
{:id="new-fields" title="New Fields"}

Finally, add a new column to the "Cookie Attribute Registry" established by {{COOKIES}} with the title "Structured Type", using information from {{cookie-params}}.


# Security Considerations

{{compatible}} identifies existing HTTP fields that can be parsed and serialised with the algorithms defined in {{STRUCTURED-FIELDS}}. Variances from existing parser behavior might be exploitable, particularly if they allow an attacker to target one implementation in a chain (e.g., an intermediary). However, given the considerable variance in parsers already deployed, convergence towards a single parsing algorithm is likely to have a net security benefit in the longer term.

{{mapped}} defines alternative representations of existing fields. Because downstream consumers might interpret the message differently based upon whether they recognise the alternative representation, implementations are prohibited from generating such fields unless they have negotiated support for them with their peer. This specification does not define such a mechanism, but any such definition needs to consider the implications of doing so carefully.


--- back








