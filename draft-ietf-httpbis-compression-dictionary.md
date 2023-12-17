---
title: Compression Dictionary Transport
abbrev: compression-dictionary
docname: draft-ietf-httpbis-compression-dictionary-latest
category: std

consensus: true
v: 3
area: ART
workgroup: HTTP
keyword:
 - compression dictionary
 - shared brotli
 - zstandard dictionary
 - delta compression

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/compression-dictionary
github-issue-label: compression-dictionary

author:
  -
    ins: P. Meenan
    name: Patrick Meenan
    role: editor
    organization: Google LLC
    email: pmeenan@google.com
  -
    ins: Y. Weiss
    name: Yoav Weiss
    role: editor
    organization: Google LLC
    email: yoavweiss@google.com

normative:
  FOLDING: RFC8792
  HTTP: RFC9110

informative:
  Origin: RFC6454
  STRUCTURED-FIELDS: RFC8941
  SHA-256: RFC6234
  RFC7932:  # Brotli
  RFC8878:  # Zstandard

--- abstract

This specification defines a mechanism for using designated {{HTTP}} responses
as an external dictionary for future HTTP responses for compression schemes
that support using external dictionaries (e.g., Brotli {{RFC7932}} and
Zstandard {{RFC8878}}).

--- middle

# Introduction

This specification defines a mechanism for using designated {{HTTP}} responses
as an external dictionary for future HTTP responses for compression schemes
that support using external dictionaries (e.g., Brotli {{RFC7932}} and
Zstandard {{RFC8878}}).

This document describes the HTTP headers used for negotiating dictionary usage
and registers media types for content encoding Brotli and Zstandard using a
negotiated dictionary.

This document uses the line folding strategies described in [FOLDING].

# Dictionary Negotiation

## Use-As-Dictionary

When responding to a HTTP Request, a server can advertise that the response can
be used as a dictionary for future requests for URLs that match the rules
specified in the Use-As-Dictionary response header.

The Use-As-Dictionary response header is a Structured Field
{{STRUCTURED-FIELDS}} sf-dictionary with values for "match", "match-dest",
"ttl", "id", and "type".

### match

The "match" value of the Use-As-Dictionary header is a sf-string value
that provides the URLPattern to use for request matching
(https://urlpattern.spec.whatwg.org/).

The URLPattern used for matching does not support using Regular expressions.

The following algorithm will return TRUE for a valid match pattern and FALSE
for an invalid pattern that MUST NOT be used:

1. Let MATCH be the value of "match" for the given dictionary.
1. Let URL be the URL of the dictionary request.
1. Let PATTERN be a URLPattern constructed by setting input=MATCH,
and baseURL=URL (https://urlpattern.spec.whatwg.org/).
1. If PATTERN has regexp groups then return FALSE
(https://urlpattern.spec.whatwg.org/#urlpattern-has-regexp-groups).
1. Return True.

The "match" value is required and MUST be included in the
Use-As-Dictionary sf-dictionary for the dictionary to be considered valid.

### match-dest

The "match-dest" value of the Use-As-Dictionary header is a sf-string value
that provides a request destination
(https://fetch.spec.whatwg.org/#concept-request-destination).

An empty string for "match-dest" MUST match all destinations.

For clients that do not support request destinations or if the value of
"match-dest" is a value that is not supported by the client then the client
MUST treat it as an empty string and match all destinations.

The "match-dest" value is optional and defaults to the empty string.

### ttl

The "ttl" value of the Use-As-Dictionary header is a sf-integer value that
provides the time in seconds that the dictionary is valid for (time to live).

The "ttl" is independent of the cache lifetime of the resource being used for
the dictionary. If the underlying resource is evicted from cache then it is
also removed but this allows for setting an explicit time to live for use as a
dictionary independent of the underlying resource in cache. Expired resources
can still be useful as dictionaries while they are in cache and can be used for
fetching updates of the expired resource. It can also be useful to artificially
limit the life of a dictionary in cases where the dictionary is updated
frequently which can help limit the number of possible incoming dictionary
variations.

The "ttl" value is optional and defaults to 1209600 (14 days).

### id

The "id" value of the Use-As-Dictionary header is a sf-string value that
specifies a server identifier for the dictionary. If an "id" value is present
then it MUST be sent to the server in a "Dictionary-ID" request header when
the dictionary is advertised as being available.

The server identifier MUST be treated as an opaque string by the client.

The server identifier MUST NOT be relied upon by the server to guarantee the
contents of the dictionary. The dictionary hash MUST be validated before use.

The "id" value string length (after any decoding) supports up to 1024
characters.

The "id" value is optional.

### type

The "type" value of the Use-As-Dictionary header is a sf-string value that
describes the file format of the supplied dictionary.

"raw" is the only defined dictionary format which represents an unformatted
blob of bytes suitable for any compression scheme to use.

If a client receives a dictionary with a type that it does not understand, it
MUST NOT use the dictionary.

The "type" value is optional and defaults to "raw".

### Examples

#### Path Prefix

A response that contained a response header:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Use-As-Dictionary: \
  match="/product/*", match-dest="document", ttl=604800
~~~

Would specify matching any document request for a URL with a path prefix of
/product/ on the same {{Origin}} as the original request, and expiring as a
dictionary in 7 days independent of the cache lifetime of the resource.

#### Versioned Directories

A response that contained a response header:

~~~ http-message
Use-As-Dictionary: match="/app/*/main.js"
~~~

Would match main.js in any directory under /app/ and expiring as a dictionary
in one year.

## Available-Dictionary

When a HTTP client makes a request for a resource for which it has an
appropriate dictionary, it can add a "Available-Dictionary" request header
to the request to indicate to the server that it has a dictionary available to
use for compression.

The "Available-Dictionary" request header is a Structured Field
{{STRUCTURED-FIELDS}} sf-binary {{SHA-256}} hash of the contents of a single
available dictionary.

The client MUST only send a single "Available-Dictionary" request header
with a single hash value for the best available match that it has available.

For example:

~~~ http-message
Available-Dictionary: :pZGm1Av0IEBKARczz7exkNYsZb8LzaMrV7J32a2fFG4=:
~~~

### Dictionary freshness requirement

To be considered as a match, the dictionary must not yet be expired as a
dictionary. When iterating through dictionaries looking for a match, the
expiration time of the dictionary is calculated by taking the last time the
dictionary was fetched and adding the "ttl" seconds from the
"Use-As-Dictionary" response. If the current time is beyond the expiration time
of the dictionary, it MUST be ignored.

### Dictionary URL matching

When a dictionary is stored as a result of a "Use-As-Dictionary" directive, it
includes "match" and "match-dest" strings that are used to match an outgoing
request from a client to the available dictionaries.

Dictionaries MUST have been served from the same {Origin} as the outgoing
request to match.

To see if an outbound request matches a given dictionary, the following
algorithm will return TRUE for a successful match and FALSE for no-match:

1. If the current client supports request destinations:
    * Let DEST be the value of "match-dest" for the given dictionary.
    * Let REQUEST_DEST be the value of the destination for the current
    request.
    * If DEST is not an empty string and If DEST and REQUEST_DEST are not the
    same value, return FALSE
1. Let BASEURL be the URL of the dictionary request.
1. Let URL represent the URL of the outbound request being checked.
1. If the {Origin} of BASEURL and the {Origin} of URL are not the same, return
FALSE.
1. Let MATCH be the value of "match" for the given dictionary.
1. Let PATTERN be a URLPattern constructed by setting input=MATCH,
and baseURL=BASEURL (https://urlpattern.spec.whatwg.org/).
1. Return the result of running the "test" method of PATTERN with input=URL
(https://urlpattern.spec.whatwg.org/#ref-for-dom-urlpattern-test)

### Multiple matching dictionaries

When there are multiple dictionaries that match a given request URL, the client
MUST pick a single dictionary using the following rules:
1. For clients that support request destinations, a dictionary that specifies
and matches a "match-dest" takes precedence over a match that does not use a
destination.
1. Given equivalent destination precedence, the dictionary with the longest
"match" takes precedence.
1. Given equivalent destination and match length precedence, the most recently
fetched dictionary takes precedence.

## Dictionary-ID

When a HTTP client makes a request for a resource for which it has an
appropriate dictionary and the dictionary was stored with a server-provided
"id" in the Use-As-Dictionary response then the client MUST echo the stored
"id" in a "Dictionary-ID" request header.

The "Dictionary-ID" request header is a Structured Field {{STRUCTURED-FIELDS}}
sf-string of up to 1024 characters (after any decoding) and MUST be identical
to the server-provided "id".

For example:

~~~ http-message
Available-Dictionary: :pZGm1Av0IEBKARczz7exkNYsZb8LzaMrV7J32a2fFG4=:
Dictionary-ID: "/v1/main.js 33a64df551425fcc55e4d42a148795d9f25f89d4"
~~~

## Content-Dictionary

When a HTTP server responds with a resource that is encoded with a dictionary
the server MUST send the hash of the dictionary that was used in the
"Content-Dictionary" response header.

The "Content-Dictionary" response header is a Structured Field
{{STRUCTURED-FIELDS}} sf-dictionary {{SHA-256}} hash of the contents of the
dictionary that was used to encode the response.

If the HTTP response contains a "Content-Dictionary" response header with the
hash of a dictionary that the client does not have available then the client
cannot decode or use the HTTP response.

For example:

~~~ http-message
Content-Dictionary: :pZGm1Av0IEBKARczz7exkNYsZb8LzaMrV7J32a2fFG4=:
~~~

# Negotiating the compression algorithm

When a compression dictionary is available for use for a given request, the
algorithm to be used is negotiated through the regular mechanism for
negotiating content encoding in HTTP.

This document introduces two new content encoding algorithms:

|------------------|----------------------------------------------------|
| Content-Encoding | Description                                        |
|------------------|----------------------------------------------------|
| br-d             | Brotli using an external compression dictionary    |
| zstd-d           | Zstandard using an external compression dictionary |
|------------------|----------------------------------------------------|

The dictionary to use is negotiated separately and advertised in the
"Available-Dictionary" request header.

## Accept-Encoding

The client adds the algorithms that it supports to the "Accept-Encoding"
request header. e.g.:

~~~ http-message
Accept-Encoding: gzip, deflate, br, zstd, br-d, zstd-d
~~~

## Content-Encoding

If a server supports one of the dictionary algorithms advertised by the client
and chooses to compress the content of the response using the dictionary that
the client has advertised then it sets the "Content-Encoding" response header
to the appropriate value for the algorithm selected. e.g.:

~~~ http-message
Content-Encoding: br-d
~~~

If the response is cacheable, it MUST include a "Vary" header to prevent caches
serving dictionary-compressed resources to clients that don't support them or
serving the response compressed with the wrong dictionary:

~~~ http-message
Vary: accept-encoding, available-dictionary
~~~

# IANA Considerations

## Content Encoding

IANA is asked to update the "HTTP Content Coding Registry" registry
({{HTTP}}) according to the table below:

|--------|---------------------------------------------------------------------------------------|-------------|
| Name   | Description                                                                           | Reference   |
|--------|---------------------------------------------------------------------------------------|-------------|
| br-d   | A stream of bytes compressed using the Brotli protocol with an external dictionary    | {{RFC7932}} |
| zstd-d | A stream of bytes compressed using the Zstandard protocol with an external dictionary | {{RFC8878}} |
|--------|---------------------------------------------------------------------------------------|-------------|

## Header Field Registration

IANA is asked to update the
"Hypertext Transfer Protocol (HTTP) Field Name Registry" registry
({{HTTP}}) according to the table below:

|----------------------|-----------|-------------------------------------------|
| Field Name           | Status    |                 Reference                 |
|----------------------|-----------|-------------------------------------------|
| Use-As-Dictionary    | permanent | {{use-as-dictionary}} of this document    |
| Available-Dictionary | permanent | {{available-dictionary}} of this document |
| Dictionary-ID        | permanent | {{dictionary-id}} of this document        |
| Content-Dictionary   | permanent | {{content-dictionary}} of this document   |
|----------------------|-----------|-------------------------------------------|

# Compatibility Considerations

To minimize the risk of middle-boxes incorrectly processing
dictionary-compressed responses, compression dictionary transport MUST only
be used in secure contexts (HTTPS).

# Security Considerations

The security considerations for Brotli {{RFC7932}} and Zstandard
{{RFC8878}} apply to the dictionary-based versions of the respective
algorithms.

## Changing content

The dictionary must be treated with the same security precautions as
the content, because a change to the dictionary can result in a
change to the decompressed content.

The dictionary is validated using a SHA-256 hash of the content to make sure
that the client and server are both using the same dictionary. The strength
of the SHA-256 hash algorithm isn't explicitly needed to counter attacks
since the dictionary is being served from the same origin as the content. That
said, if a weakness is discovered in SHA-256 and it is determined that the
dictionary negotiation should use a different hash algorithm, the
"Use-As-Dictionary" response header can be extended to specify a different
algorithm and the server would just ignore any "Available-Dictionary" requests
that do not use the updated hash.

## Reading content

The CRIME attack shows that it's a bad idea to compress data from
mixed (e.g. public and private) sources -- the data sources include
not only the compressed data but also the dictionaries. For example,
if you compress secret cookies using a public-data-only dictionary,
you still leak information about the cookies.

Not only can the dictionary reveal information about the compressed
data, but vice versa, data compressed with the dictionary can reveal
the contents of the dictionary when an adversary can control parts of
data to compress and see the compressed size. On the other hand, if
the adversary can control the dictionary, the adversary can learn
information about the compressed data.

## Security Mitigations

If any of the mitigations do not pass, the client MUST drop the response and
return an error.

### Cross-origin protection

To make sure that a dictionary can only impact content from the same origin
where the dictionary was served, the URLPattern used for matching a
dictionary to requests is guaranteed to be for the same origin that the
dictionary is served from.

### Response readability

For clients, like web browsers, that provide additional protection against the
readability of the payload of a response and against user tracking, additional
protections MUST be taken to make sure that the use of dictionary-based
compression does not reveal information that would not otherwise be available.

In these cases, dictionary compression MUST only be used when both the
dictionary and the compressed response are fully readable by the client.

In browser terms, that means that both are either same-origin to the context
they are being fetched from or that the response is cross-origin and passes
the CORS check (https://fetch.spec.whatwg.org/#cors-check).

#### Same-Origin

On the client-side, same-origin determination is defined in the fetch spec (https://html.spec.whatwg.org/multipage/browsers.html#origin).

On the server-side, a request with a "Sec-Fetch-Site:" request header with a value of "same-origin" is to be considered a same-origin request.

* For any request that is same-origin:
    * Response MAY be used as a dictionary.
    * Response MAY be compressed by an available dictionary.

#### Cross-Origin

For requests that are not same-origin ({{same-origin}}), the "mode" of the request can be used to determine the readability of the response.

For clients that conform to the fetch spec, the mode of the request is stored in the RequestMode attribute of the request (https://fetch.spec.whatwg.org/#requestmode).

For servers responding to clients that expose the request mode information, the value of the mode is sent in the "Sec-Fetch-Mode" request header.

If a "Sec-Fetch-Mode" request header is not present, the server SHOULD allow for the dictionary compression to be used.

1. If the mode is "navigate" or "same-origin":
    * Response MAY be used as a dictionary.
    * Response MAY be compressed by an available dictionary.
1. If the mode is "cors":
    * For clients, apply the CORS check from the fetch spec (https://fetch.spec.whatwg.org/#cors-check) which includes credentials checking restrictions that may not be possible to check on the server.
        * If the CORS check passes:
            * Response MAY be used as a dictionary.
            * Response MAY be compressed by an available dictionary.
        * Else:
            * Response MUST NOT be used as a dictionary.
            * Response MUST NOT be compressed by an available dictionary.
    * For servers:
        * If the response does not include an "Access-Control-Allow-Origin" response header:
            * Response MUST NOT be used as a dictionary.
            * Response MUST NOT be compressed by an available dictionary.
        * If the request does not include an "Origin" request header:
            * Response MUST NOT be used as a dictionary.
            * Response MUST NOT be compressed by an available dictionary.
        * If the value of the "Access-Control-Allow-Origin" response header is "*":
            * Response MAY be used as a dictionary.
            * Response MAY be compressed by an available dictionary.
        * If the value of the "Access-Control-Allow-Origin" response header matches the value of the "Origin" request header:
            * Response MAY be used as a dictionary.
            * Response MAY be compressed by an available dictionary.
1. If the mode is any other value (including "no-cors"):
    * Response MUST NOT be used as a dictionary.
    * Response MUST NOT be compressed by an available dictionary.

# Privacy Considerations

Since dictionaries are advertised in future requests using the hash of the
content of the dictionary, it is possible to abuse the dictionary to turn it
into a tracking cookie.

To mitigate any additional tracking concerns, clients MUST treat dictionaries
in the same way that they treat cookies. This includes partitioning the storage
as cookies are partitioned as well as clearing the dictionaries whenever
cookies are cleared.

--- back

