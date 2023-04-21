---
title: Retrofit Structured Fields for HTTP
abbrev: Retrofit Structured Fields
docname: draft-ietf-httpbis-retrofit-latest
date: {DATE}
category: std
area: Applications and Real-Time
workgroup: HTTP

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
  HTTP: RFC9110
  STRUCTURED-FIELDS: I-D.ietf-httpbis-sfbis
  COOKIES: I-D.ietf-httpbis-rfc6265bis

informative:


--- abstract

This specification nominates a selection of existing HTTP fields whose values are compatible with Structured Fields syntax, so that they can be handled as such (subject to certain caveats).

To accommodate some additional fields whose syntax is not compatible, it also defines mappings of their semantics into Structured Fields. It does not specify how to convey them in HTTP messages.

--- middle

# Introduction

Structured Field Values for HTTP {{STRUCTURED-FIELDS}} introduced a data model with associated parsing and serialization algorithms for use by new HTTP field values. Fields that are defined as Structured Fields can bring advantages that include:

* Improved interoperability and security: precisely defined parsing and serialisation algorithms are typically not available for fields defined with just ABNF and/or prose.
* Reuse of common implementations: many parsers for other fields are specific to a single field or a small family of fields.
* Canonical form: because a deterministic serialisation algorithm is defined for each type, Structure Fields have a canonical representation.
* Enhanced API support: a regular data model makes it easier to expose field values as a native data structure in implementations.
* Alternative serialisations: While {{STRUCTURED-FIELDS}} defines a textual serialisation of that data model, other, more efficient serialisations of the underlying data model are also possible.

However, a field needs to be defined as a Structured Field for these benefits to be realised. Many existing fields are not, making up the bulk of header and trailer fields seen in HTTP traffic on the internet.

This specification defines how a selection of existing HTTP fields can be handled as Structured Fields, so that these benefits can be realised -- thereby making them Retrofit Structured Fields.

It does so using two techniques. {{compatible}} lists compatible fields -- those that can be handled as if they were Structured Fields due to the similarity of their defined syntax to that in Structured Fields. {{mapped}} lists mapped fields -- those whose syntax needs to be transformed into an underlying data model which is then mapped into that defined by Structured Fields.

Note that this specification does not enable use of Retrofit Structured Fields in the HTTP protocol "on the wire" or in APIs; it only establishes handling for specific fields that might be used by such applications in the future.


## Using Retrofit Structured Fields

Retrofitting data structures onto existing and widely-deployed HTTP fields requires careful handling to assure interoperability and security. This section highlights considerations for applications that use Retrofit Structured Fields.

While the majority of field values seen in HTTP traffic should be able to be parsed or mapped successfully, some will not. An application using Retrofit Structured Fields will need to define how unsuccessful values will be handled.

For example, an API that exposes field values using Structured Fields data types might make the field value available as a string in cases where the field did not successfully parse or map.

The mapped field values described in {{mapped}} are not compatible with the original syntax of their fields, and so cannot be used unless parties processing them have explicitly indicated their support for that form of the field value. An application using Retrofit Structured Fields will need to define how to negotiate support for them.

For example, an alternative serialization of fields that takes advantage of Structured Fields would need to establish an explicit negotiation mechanism to assure that both peers would handle that serialization appropriately before using it.

See also the security considerations in {{security}}.


## Notational Conventions

{::boilerplate bcp14-tagged}


# Compatible Fields {#compatible}

The HTTP fields listed in {{compatible-fields}} have values that can be handled as Structured Field Values according to the parsing and serialisation algorithms in {{STRUCTURED-FIELDS}} corresponding to the listed top-level type, subject to the caveats in {{compatible-caveats}}.

The top-level types are chosen for compatibility with the defined syntax of the field as well as with actual internet traffic. However, not all instances of these fields will successfully parse as a Structured Field Value. This might be because the field value is clearly invalid, or it might be because it is valid but not parseable as a Structured Field.

An application using this specification will need to consider how to handle such field values. Depending on its requirements, it might be advisable to reject such values, treat them as opaque strings, or attempt to recover a Structured Field Value from them in an ad hoc fashion.


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


## Caveats {#compatible-caveats}

Note the following caveats regarding compatibility:

Parsing differences:
: Some values may fail to parse as Structured Fields, even though they are valid according to their originally specified syntax. For example, HTTP parameter names are case-insensitive (per {{Section 5.6.6 of HTTP}}), but Structured Fields require them to be all-lowercase.
Likewise, many Dictionary-based fields (e.g., Cache-Control, Expect-CT, Pragma, Prefer, Preference-Applied, Surrogate-Control) have case-insensitive keys.
Similarly, the parameters rule in HTTP (see {{Section 5.6.6 of HTTP}}) allows whitespace before the ";" delimiter, but Structured Fields does not.
And, {{Section 5.6.4 of HTTP}} allows backslash-escaping most characters in quoted strings, whereas Structured Field Strings only escape "\\" and DQUOTE. The vast majority of fields seen in typical traffic do not exhibit these behaviors.

Error handling:
: Parsing algorithms specified (or just widely implemented) for current HTTP headers may differ from those in Structured Fields in details such as error handling. For example, HTTP specifies that repeated directives in the Cache-Control header field have a different precedence than that assigned by a Dictionary structured field (which Cache-Control is mapped to).

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

Some HTTP field values have syntax that cannot be successfully parsed as Structured Field values. Instead, it is necessary to map them into a Structured Field value.

For example, the Date HTTP header field carries a date:

~~~ http-message
Date: Sun, 06 Nov 1994 08:49:37 GMT
~~~

Its value would be mapped to:

~~~ http-message-new
@784111777
~~~

Unlike those listed in {{compatible}}, these representations are not compatible with the original fields' syntax, and MUST NOT be used unless they are explicitly supported. For example, this means that sending them to a next-hop recipient in HTTP requires prior negotiation. This specification does not define how to do so.


## URLs

The field names in {{url-fields}} have values that can be mapped into Structured Field values by treating the original field's value as a String.

| Field Name       |
|------------------|
| Content-Location |
| Location         |
| Referer          |
{:id="url-fields" title="URL Fields"}

For example, this Location field:

~~~ http-message
Location: https://example.com/foo
~~~

would have a mapped value of:

~~~
"https://example.com/foo"
~~~


## Dates

The field names in {{date-fields}} have values that can be mapped into Structured Field values by parsing their payload according to {{Section 5.6.7 of HTTP}} and representing the result as a Date.

| Field Name          |
|---------------------|
| Date                |
| Expires             |
| If-Modified-Since   |
| If-Unmodified-Since |
| Last-Modified       |
{:id="date-fields" title="Date Fields"}

For example, an Expires field's value could be mapped as:

~~~ http-message-new
@1659578233
~~~

## ETags

The field value of the ETag header field can be mapped into a Structured Field value by representing the entity-tag as a String, and the weakness flag as a Boolean "w" parameter on it, where true indicates that the entity-tag is weak; if 0 or unset, the entity-tag is strong.

For example, this ETag header field:

~~~ http-message
ETag: W/"abcdef"
~~~

would have a mapped value of:

~~~
"abcdef"; w
~~~

If-None-Match's field value can be mapped into a Structured Field value which is a List of the structure described above. When a field value contains "*", it is represented as a Token.

Likewise, If-Match's field value can be mapped into a Structured Field value in the same manner.

For example, this If-None-Match field:

~~~ http-message
If-None-Match: "abcdef"; w, "ghijkl", *
~~~

would have a mapped value of:

~~~
"abcdef"; w, "ghijkl", *
~~~


## Cookies

The field values of the Cookie and Set-Cookie fields {{COOKIES}} can be mapped into Structured Fields Lists.

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

For example, this Set-Cookie field:

~~~ http-message
Set-Cookie: lang=en-US; Expires=Wed, 09 Jun 2021 10:18:14 GMT;
               samesite=Strict; secure
~~~

would have a mapped value of:

~~~ http-message-new
("lang" "en-US"); expires=@1623233894;
               samesite=Strict; secure
~~~

And this Cookie field:

~~~ http-message
Cookie: SID=31d4d96e407aad42; lang=en-US
~~~

would have a mapped value of:

~~~ http-message-new
("SID" "31d4d96e407aad42"), ("lang" "en-US")
~~~


# IANA Considerations

Please add the following note to the "Hypertext Transfer Protocol (HTTP) Field Name Registry":

> A prefix of "*" in the Structured Type column indicates that it is a retrofit type (i.e., not
> natively Structured); see {{&SELF}}.

Then, add a new column, "Structured Type", with the values from {{compatible}} assigned to the nominated registrations, prefixing each with "*" to indicate that it is a retrofit type.

Finally, add a new column to the "Cookie Attribute Registry" established by {{COOKIES}} with the title "Structured Type", using information from {{cookie-params}}.


# Security Considerations {#security}

{{compatible}} identifies existing HTTP fields that can be parsed and serialised with the algorithms defined in {{STRUCTURED-FIELDS}}. Variances from existing parser behavior might be exploitable, particularly if they allow an attacker to target one implementation in a chain (e.g., an intermediary). However, given the considerable variance in parsers already deployed, convergence towards a single parsing algorithm is likely to have a net security benefit in the longer term.

{{mapped}} defines alternative representations of existing fields. Because downstream consumers might interpret the message differently based upon whether they recognise the alternative representation, implementations are prohibited from generating such values unless they have negotiated support for them with their peer. This specification does not define such a mechanism, but any such definition needs to consider the implications of doing so carefully.


--- back








