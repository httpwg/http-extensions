---
title: Digest Headers
abbrev:
docname: draft-ietf-httpbis-digest-headers-latest
category: std

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Digest

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline, docmapping]

author:
 -
    ins: R. Polli
    name: Roberto Polli
    org: Team Digitale, Italian Government
    email: robipolli@gmail.com
 -
    ins: L. Pardue
    name: Lucas Pardue
    org: Cloudflare
    email: lucaspardue.24.7@gmail.com

normative:
  RFC1321:
  RFC3174:
  RFC1950:
  RFC3230:
  RFC3309:
  RFC2119:
  RFC5843:
  RFC4648:
  RFC5234:
  RFC6234:
  RFC7405:
  RFC8174:
  UNIX:
    title: The Single UNIX Specification, Version 2 - 6 Vol Set for UNIX 98
    author:
      org: The Open Group
    date: 1997-02
  NIST800-32:
    title: Introduction to Public Key Technology and the Federal PKI Infrastructure
    author:
      org: National Institute of Standards and Technology, U.S. Department of Commerce
    date: 2001-02
    target: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-32.pdf
  CMU-836068:
    title: MD5 Vulnerable to collision attacks
    author:
      org: Carnagie Mellon University, Software Engineering Institute
    date: 2008-12-31
    target: https://www.kb.cert.org/vuls/id/836068/
  IACR-2020-014:
    title: SHA-1 is a Shambles
    author:
      -
         ins: G. Leurent
         org: Inria, France
      -
         ins: T. Peyrin
         org: Nanyang Technological University, Singapore; Temasek Laboratories, Singapore
    date: 2020-01-05
    target: https://eprint.iacr.org/2020/014.pdf

informative:
  RFC2818:
  RFC7231:
  RFC7396:
  SRI:
    title: "Subresource Integrity"
    date: 2016-06-23
    author:
      - ins: D. Akhawe
      - ins: F. Braun
      - ins: F. Marier
      - ins: J. Weinberger
    seriesinfo:
      W3C Recommendation: REC-SRI-20160623
    target: https://www.w3.org/TR/2016/REC-SRI-20160623/

--- abstract

This document defines the HTTP Digest and Want-Digest fields, thus allowing
client and server to negotiate an integrity checksum of the exchanged resource
representation data.

This document obsoletes RFC 3230. It replaces the term "instance" with
"representation", which makes it consistent with the HTTP Semantic and Context
defined in draft-ietf-httpbis-semantics.


--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at
<https://lists.w3.org/Archives/Public/ietf-http-wg/>.

The source code and issues list for this draft can be found at
<https://github.com/httpwg/http-extensions>.


--- middle

# Introduction

The core specification of HTTP does not define a means to protect the integrity
of resources. When HTTP messages are transferred between endpoints, the protocol
might choose to make use of features of the lower layer in order to provide some
integrity protection; for instance TCP checksums or TLS records [RFC2818].

However, there are cases where relying on this alone is insufficient. An
HTTP-level integrity mechanism that operates independent of transfer can be used
to detect programming errors and/or corruption of data at rest, be used across
multiple hops in order to provide end-to-end integrity guarantees, aid fault
diagnosis across hops and system boundaries, and can be used to validate
integrity when reconstructing a resource fetched using different HTTP
connections.

This document defines a mechanism that acts on HTTP representation-data. It can
be combined with other mechanisms that protect representation-metadata, such as
digital signatures, in order to protect the desired parts of an HTTP exchange in
whole or in part.

## A Brief History of HTTP Integrity Fields {#history}

The Content-MD5 header field was originally introduced to provide integrity, but
HTTP/1.1 ([RFC7231], Appendix B) obsoleted it:

  > The Content-MD5 header field has been removed because it was
  > inconsistently implemented with respect to partial responses.

[RFC3230] provided a more flexible solution introducing the concept of
"instance", and the fields `Digest` and `Want-Digest`.

## This Proposal

The concept of `selected representation` defined in Section 7 of
{{!SEMANTICS=I-D.ietf-httpbis-semantics}} makes [RFC3230] definitions inconsistent with
current HTTP semantics. This document updates the `Digest` and `Want-Digest`
field definitions to align with {{SEMANTICS}} concepts.

Basing `Digest` on the selected representation makes it straightforward to
apply it to use-cases where the transferred data does require some sort of
manipulation to be considered a representation, or conveys a partial
representation of a resource eg. Range Requests (see Section 9.3 of
{{SEMANTICS}}).

Changes are semantically compatible with existing implementations and better
cover both the request and response cases.

The value of `Digest` is calculated on selected representation, which is tied to
the value contained in any `Content-Encoding` or `Content-Type` header fields.
Therefore, a given resource may have multiple different digest values.

To allow both parties to exchange a Digest of a representation with no content
codings (see Section 7.1.2 of {{SEMANTICS}}) two more algorithms
are added (`ID-SHA-256` and `ID-SHA-512`).

## Goals

The goals of this proposal are:

   1. Digest coverage for either the resource's `representation data` or
      `selected representation data` communicated via HTTP.

   2. Support for multiple digest algorithms.

   3. Negotiation of the use of digests.

The goals do not include:

  HTTP message integrity:
  : The digest mechanism described here does not cover the full HTTP message
    nor its semantic, as representation metadata are not included in the
    checksum.

  HTTP field integrity:
  : The digest mechanisms described here cover only representation and selected
    representation data, and do not protect the integrity of associated
    representation metadata or other message fields.

  Authentication:
  : The digest mechanisms described here are not meant to support authentication
    of the source of a digest or of a message or anything else. These mechanisms,
    therefore, are not a sufficient defense against many kinds of malicious
    attacks.

  Privacy:
  : Digest mechanisms do not provide message privacy.

  Authorization:
  : The digest mechanisms described here are not meant to support authorization
    or other kinds of access controls.


## Notational Conventions
The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 ([RFC2119] and [RFC8174])
when, and only when, they appear in all capitals, as shown here.

This document uses the Augmented BNF defined in [RFC5234] and updated by
[RFC7405] along with the "#rule" extension defined in Section 5 of
{{SEMANTICS}}.

The definitions "representation", "selected representation", "representation
data", "representation metadata", and "payload body" in this document are to be
interpreted as described in {{SEMANTICS}}.

The definition "validator fields" in this document is to be interpreted as described in
Section 11.2 of {{SEMANTICS}}.

# Representation Digest {#representation-digest}

The representation digest is an integrity mechanism for HTTP resources
which uses a checksum  that is calculated independently of the payload body
(see Section 7.3.3 of {{SEMANTICS}}).
It uses the representation data (see Section 7.1 of {{SEMANTICS}}),
that can be fully or partially contained in the payload body, or not contained at all:

~~~
   representation-data := Content-Encoding( Content-Type( bits ) )
~~~

This takes into account the effect of the HTTP semantics on the messages;
for example the payload body can be affected by Range Requests or methods such as HEAD,
while the way the payload body is transferred "on the wire" is dependent on other
transformations (eg. transfer codings for HTTP/1.1 see 6.1 of
{{?HTTP11=I-D.ietf-httpbis-messaging}}):
{{resource-representation}} contains several examples to help illustrate those effects.

A representation digest consists of
the value of a checksum computed on the entire selected `representation data` of a resource
together with an indication of the algorithm used (and any parameters)

~~~ abnf
   representation-data-digest = digest-algorithm "="
                                <encoded digest output>
~~~

The checksum is computed using one of the `digest-algorithms` listed in {{algorithms}}
and then encoded in the associated format.

The example below shows the  `sha-256` digest-algorithm which uses base64 encoding.

~~~ example
   sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
~~~

# The Digest Field {#digest}

The Digest field contains a list of one or more representation digest values as
defined in {{representation-digest}}. It can be used in both request and
response.

~~~ abnf
   Digest = "Digest" ":" OWS 1#representation-data-digest
~~~

The resource is specified by the effective request URI and any `validator field`
contained in the message.

The relationship between Content-Location (see Section 7.2.5 of
{{SEMANTICS}}) and Digest is demonstrated in
{{post-not-request-uri}}. A comprehensive set of examples showing the impacts of
representation metadata, payload transformations and HTTP methods on Digest is
provided in {{examples-unsolicited}} and {{examples-solicited}}.

A Digest field MAY contain multiple representation-data-digest values. This
could be useful for responses expected to reside in caches shared by users with
different browsers, for example.

A recipient MAY ignore any or all of the representation-data-digests in a Digest
field. This allows the recipient to choose which digest-algorithm(s) to use for
validation instead of verifying every received representation-data-digest.

A sender MAY send a representation-data-digest using a digest-algorithm without
knowing whether the recipient supports the digest-algorithm, or even knowing
that the recipient will ignore it.

Digest can be sent in a trailer section. When using incremental digest-algorithms
this allows the sender and the receiver to dynamically compute the digest value
while streaming the content.

Two examples of its use are

~~~ example
   Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                      AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==

   Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=,
           id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
~~~


# The Want-Digest Field {#want-digest}

The Want-Digest field indicates the sender's desire to receive a representation
digest on messages associated with the request URI and representation metadata.

~~~
   Want-Digest = "Want-Digest" ":" OWS 1#want-digest-value
   want-digest-value = digest-algorithm [ ";" "q" "=" qvalue]
   qvalue = ( "0"  [ "."  0*1DIGIT ] ) /
            ( "1"  [ "."  0*1( "0" ) ] )
~~~

If a digest-algorithm is not accompanied by a qvalue, it is treated as if its
associated qvalue were 1.0.

The sender is willing to accept a digest-algorithm if and only if it is listed
in a Want-Digest field of a message, and its qvalue is non-zero.

If multiple acceptable digest-algorithm values are given, the sender's preferred
digest-algorithm is the one (or ones) with the highest qvalue.

Two examples of its use are

~~~
   Want-Digest: sha-256
   Want-Digest: SHA-512;q=0.3, sha-256;q=1, unixsum;q=0
~~~

# Digest Algorithm Values {#algorithms}

Digest algorithm values are used to indicate a specific digest computation.  For
some algorithms, one or more parameters can be supplied.

~~~
   digest-algorithm = token
~~~

The BNF for "parameter" is defined in Section 5.4.1.4 of
{{SEMANTICS}}. All digest-algorithm values are case-insensitive.

The Internet Assigned Numbers Authority (IANA) acts as a registry for
digest-algorithm values.
The registry contains the tokens listed below.

Some algorithms, although registered, have since been found vulnerable:
the MD5 algorithm MUST NOT be used due to collision attacks [CMU-836068]
and the SHA algorithm MUST NOT be used due
to collision attacks [IACR-2020-014].


  {: vspace="0"}
  SHA-256
  : * Description: The SHA-256 algorithm [RFC6234].  The output of
      this algorithm is encoded using the base64 encoding [RFC4648].
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  SHA-512
  : * Description: The SHA-512 algorithm [RFC6234].  The output of
      this algorithm is encoded using the base64 encoding [RFC4648].
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  MD5
  : * Description: The MD5 algorithm, as specified in [RFC1321].
      The output of this algorithm is encoded using the
      base64 encoding  [RFC4648].
      The MD5 algorithm MUST NOT be used as it's now vulnerable
      to collision attacks [CMU-836068].
    * Reference: [RFC1321], [RFC4648], this document.
    * Status: deprecated

  SHA
  : * Description:  The SHA-1 algorithm [RFC3174].  The output of this
      algorithm is encoded using the base64 encoding  [RFC4648].
      The SHA algorithm MUST NOT be used as it's now vulnerable
      to collision attacks [IACR-2020-014].
    * Reference: [RFC3174], [RFC6234], [RFC4648], this document.
    * Status: deprecated

  UNIXsum
  : * Description: The algorithm computed by the UNIX "sum" command,
      as defined by the Single UNIX Specification,
      Version 2 [UNIX].  The output of this algorithm is an
      ASCII decimal-digit string representing the 16-bit
      checksum, which is the first word of the output of
      the UNIX "sum" command.
    * Reference: [UNIX], this document.
    * Status: standard

  UNIXcksum
  : * Description: The algorithm computed by the UNIX "cksum" command,
      as defined by the Single UNIX Specification,
      Version 2 [UNIX].  The output of this algorithm is an
      ASCII digit string representing the 32-bit CRC,
      which is the first word of the output of the UNIX
      "cksum" command.
    * Reference: [UNIX], this document.
    * Status: standard

To allow sender and recipient to provide a checksum which is independent from
`Content-Encoding`, the following additional algorithms are defined:

  {: vspace="0"}
  ID-SHA-512
  : * Description: The sha-512 digest of the representation-data of the resource when no
    content coding is applied
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  ID-SHA-256
  : * Description: The sha-256 digest of the representation-data of the resource when no
      content coding is applied
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

If other digest-algorithm values are defined, the associated encoding MUST
either be represented as a quoted string, or MUST NOT include ";" or "," in the
character sets used for the encoding.


# Use of Digest when acting on resources {#acting-on-resources}

POST and PATCH requests can appear to convey partial representations but are
semantically acting on resources. The enclosed representation, including its
metadata refers to that action.

In these requests the representation digest MUST be computed on the
representation-data of that action.
This is the only possible choice because representation digest requires complete
representation metadata (see {{representation-digest}}).

In responses,

- if the representation describes the status of the request,
  `Digest` MUST be computed on the enclosed representation
   (see {{post-referencing-action}} );

- if there is a referenced resource
  `Digest` MUST be computed on the selected representation of the referenced resource
   even if that is different from the target resource.
   That might or might not result in computing `Digest` on the enclosed representation.

The latter case might be done according to the HTTP semantics of the given
method, for example using the `Content-Location` header field.
In contrast, the `Location` header field does not affect `Digest` because
it is not representation metadata.

## Digest and PATCH

In PATCH requests the representation digest MUST be computed on the patch document
because the representation metadata refers to the patch document and not
to the target resource (see Section 2 of {{?RFC5789}}).

In PATCH responses the representation digest MUST be computed on the selected
representation of the patched resource.

`Digest` usage with PATCH is thus very similar to the POST one, but with the
resource's own semantic partly implied by the method and by the patch document.

# Deprecate Negotiation of Content-MD5 {#deprecate-contentMD5}

This RFC deprecates the negotiation of Content-MD5 as it has been obsoleted by
[RFC7231].

# Relationship to Subresource Integrity (SRI)

Subresource Integrity [SRI] is an integrity mechanism that shares some
similarities to the present document's mechanism. However, there are differences
in motivating factors, threat model and specification of integrity digest
generation, signalling and validation.

SRI allows a first-party authority to declare an integrity assertion on a
resource served by a first or third party authority. This is done via the
`integrity` attribute that can be added to `script` or `link` HTML elements.
Therefore, the integrity assertion is always made out-of-band to the resource
fetch. In contrast, the `Digest` field is supplied in-band alongside the
selected representation, meaning that an authority can only declare an integrity
assertion for itself. Methods to improve the security properties of
representation digests are presented in {{security-considerations}}. This
contrast is interesting because on one hand self-assertion is less likely to be
affected by coordination problems such as the first-party holding stale
information about the third party, but on the other hand the self-assertion is
only as trustworthy as the authority that provided it.

The SRI `integrity` attribute contains a cryptographic hash algorithm and digest
value which is similar to `representation-data-digest` (see
{{representation-digest}}). The major differences are in serialization format.

The SRI digest value is calculated over the identity encoding of the resource,
not the selected representation (as specified for `representation-data-digest`
in this document). Section 3.4.5 of [SRI] describes the benefit of the identity
approach - the SRI `integrity` attribute can contain multiple algorithm-value
pairs where each applies to a different identity encoded payload. This allows
for protection of distinct resources sharing a URL. However, this is a contrast
to the design of representation digests, where multiple `Digest` field-values
all protect the same representation.

SRI does not specify handling of partial representation data (e.g. Range
requests). In contrast, this document specifies handling in terms that are fully
compatible with core HTTP concepts (an example is provided in
{{server-returns-partial-representation-data}}).

SRI specifies strong requirements on the selection of algorithm for generation
and validation of digests. In contrast, the requirements in this document are
weaker.

SRI defines no method for a client to declare an integrity assertion on
resources it transfers to a server. In contrast, the `Digest` field can
appear on requests.

## Supporting Both SRI and Representation Digest

The SRI and Representation Digest mechanisms are different and complementary but
one is not capable of replacing the other because they have different
threat, security and implementation properties.

A user agent that supports both mechanisms is expected to apply the rules
specified for each but since the two mechanisms are independent, the ordering is
not important. However, a user agent supporting both could benefit from
performing representation digest validation first because it does not always
require a conversion into identity encoding.

There is a chance that a user agent supporting both mechanisms may find one
validates successfully while the other fails. This document specifies no
requirements or guidance for user agents that experience such cases.


# Examples of Unsolicited Digest {#examples-unsolicited}

The following examples demonstrate interactions where a server responds with a
`Digest` field even though the client did not solicit one using
`Want-Digest`.


## Server Returns Full Representation Data {#example-full-representation}

Request:

~~~
GET /items/123

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

## Server Returns No Representation Data

Requests without a payload body can still send a Digest field
applying the digest algorithm to an empty representation.

As there is no content coding applied, the `sha-256` and the `id-sha-256`
digest-values in the response are the same.

Request:

~~~
HEAD /items/123 HTTP/1.1
Digest: sha-256=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Digest: id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

~~~

## Server Returns Partial Representation Data

Request:

~~~
GET /items/123
Range: bytes=1-7

~~~

Response:

~~~
HTTP/1.1 206 Partial Content
Content-Type: application/json
Content-Range: bytes 1-7/18
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

"hello"
~~~


## Client and Server Provide Full Representation Data

The request contains a `Digest` field calculated on the enclosed
representation.

It also includes an `Accept-Encoding: br` header field that advertises the
client supports brotli encoding.

The response includes a `Content-Encoding: br` that indicates the selected
representation is brotli encoded. The `Digest` field-value is therefore
different compared to the request.

The response body is displayed as a base64-encoded string because it contains
non-printable characters.

Request:

~~~
PUT /items/123
Content-Type: application/json
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~
Content-Type: application/json
Content-Encoding: br
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~


## Client Provides Full Representation Data, Server Provides No Representation Data

Request `Digest` value is calculated on the enclosed payload. Response `Digest`
value depends on the representation metadata header fields, including
`Content-Encoding: br` even when the response does not contain a payload body.


Request:

~~~
PUT /items/123
Content-Type: application/json
Content-Length: 18
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~
HTTP/1.1 204 No Content
Content-Type: application/json
Content-Encoding: br
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

~~~

## Client and Server Provide Full Representation Data, Client Uses id-sha-256.

The response contains two digest values:

- one with no content coding applied, which in this case accidentally
  matches the unencoded digest-value sent in the request;
- one taking into account the `Content-Encoding`.

As the response body contains non-printable characters, it is displayed as a
base64-encoded string.

Request:

~~~
PUT /items/123 HTTP/1.1
Content-Type: application/json
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: br
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=,
        id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~


## POST Response does not Reference the Request URI {#post-not-request-uri}

Request `Digest` value is computed on the enclosed representation (see
{{acting-on-resources}}).

The representation enclosed in the response refers to the resource identified by
`Content-Location` (see {{SEMANTICS}}, Section 7.3.2).

`Digest` is thus computed on the enclosed representation.

Request:

~~~
POST /books HTTP/1.1
Content-Type: application/json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=

{"title": "New Title"}
~~~


Response

~~~
HTTP/1.1 201 Created
Content-Type: application/json
Digest: id-sha-256=BZlF2v0IzjuxN01RQ97EUXriaNNLhtI8Chx8Eq+XYSc=
Content-Location: /books/123

{"id": "123", "title": "New Title"}
~~~

Note that a `204 No Content` response without a payload body but with the same
`Digest` field-value would have been legitimate too.

## POST Response Describes the Request Status {#post-referencing-action}

Request `Digest` value is computed on the enclosed representation (see
{{acting-on-resources}}).

The representation enclosed in the response describes the status of the request,
so `Digest` is computed on that enclosed representation.

Response `Digest` has no explicit relation with the resource referenced by
`Location`.

Request:

~~~
POST /books HTTP/1.1
Content-Type: application/json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=
Location: /books/123

{"title": "New Title"}
~~~


Response

~~~
HTTP/1.1 201 Created
Content-Type: application/json
Digest: id-sha-256=0o/WKwSfnmIoSlop2LV/ISaBDth05IeW27zzNMUh5l8=
Location: /books/123

{
  "status": "created",
  "id": "123",
  "ts": 1569327729,
  "instance": "/books/123"
}
~~~

## Digest with PATCH

This case is analogous to a POST request where the target resource reflects the
effective request URI.

The PATCH request uses the `application/merge-patch+json` media type defined in
{{?RFC7396}}.

`Digest` is calculated on the enclosed payload, which corresponds to the patch
document.

The response `Digest` is computed on the complete representation of the patched
resource.

Request:

~~~
PATCH /books/123 HTTP/1.1
Content-Type: application/merge-patch+json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=

{"title": "New Title"}
~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Digest: id-sha-256=BZlF2v0IzjuxN01RQ97EUXriaNNLhtI8Chx8Eq+XYSc=

{"id": "123", "title": "New Title"}
~~~

Note that a `204 No Content` response without a payload body but with the same
`Digest` field-value would have been legitimate too.

## Error responses

In error responses, the representation-data does not necessarily refer to the
target resource. Instead it refers to the representation of the error.

In the following example a client attempts to patch the resource located at
/books/123. However, the resource does not exist and the server generates a 404
response with a body that describes the error in accordance with {{?RFC7807}}.

The digest of the response is computed on this enclosed representation.

Request:

~~~
PATCH /books/123 HTTP/1.1
Content-Type: application/merge-patch+json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=

{"title": "New Title"}
~~~

Response:

~~~
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
Digest: sha-256=UJSojgEzqUe4UoHzmNl5d2xkmrW3BOdmvsvWu1uFeu0=

{
  "title": "Not Found",
  "detail": "Cannot PATCH a non-existent resource",
  "status": 404
}
~~~

## Use with trailers and transfer coding

An origin server sends Digest in the HTTP trailer, so it can calculate digest-value
while streaming content and thus mitigate resource consumption.
The field value is the same as in {{example-full-representation}} because Digest is designed to
 be independent from the use of one or more transfer codings (see {{representation-digest}}).

Request:

~~~
GET /items/123

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Transfer-Encoding: chunked
Trailer: Digest

8\r\n
{"hello"\r\n
8
: "world\r\n
2\r\n
"}\r\n
0\r\n
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

~~~


# Examples of Want-Digest Solicited Digest {#examples-solicited}

The following examples demonstrate interactions where a client solicits a
`Digest` using `Want-Digest`.

## Server Selects Client's Least Preferred Algorithm

The client requests a digest, preferring sha. The server is free to reply with
sha-256 anyway.

Request:

~~~
GET /items/123 HTTP/1.1
Want-Digest: sha-256;q=0.3, sha;q=1

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

##  Server Selects Algorithm Unsupported by Client

The client requests a sha digest only. The server is currently free to reply
with a Digest containing an unsupported algorithm.

Request:

~~~
GET /items/123
Want-Digest: sha;q=1

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                   +AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==

{"hello": "world"}
~~~

## Server Does Not Support Client Algorithm and Returns an Error

The client requests a sha Digest, the server advises for sha-256 and sha-512

Request:

~~~
GET /items/123
Want-Digest: sha;q=1

~~~

Response:

~~~
HTTP/1.1 400 Bad Request
Want-Digest: sha-256, sha-512

~~~


# Security Considerations

## Digest Does Not Protect the Full HTTP Message

This document specifies a data integrity mechanism that protects HTTP
`representation data`, but not HTTP `representation metadata` fields, from
certain kinds of accidental corruption.

`Digest` is not intended as general protection against malicious tampering with
HTTP messages, this can be achieved by combining it with other approaches such
as transport-layer security or digital signatures.

## Broken Cryptographic Algorithms

Cryptographic algorithms are intended to provide a proof of integrity suited
towards cryptographic constructions such as signatures.

However, these rely on collision-resistance for their security proofs
[CMU-836068]. The MD5 and SHA-1 algorithms are vulnerable to collisions attacks,
so they MUST NOT be used with `Digest`.

## Other Deprecated Algorithms

The ADLER32 algorithm defined in [RFC1950] has been deprecated by [RFC3309]
because under certain conditions it provides weak detection of errors and is now
NOT RECOMMENDED  for use with `Digest`.

## Digest for End-to-End Integrity

`Digest` alone does not provide end-to-end integrity of HTTP messages over
multiple hops, as it just covers the `representation data` and not the
`representation metadata`.

Besides, it allows to protect `representation data` from buggy manipulation,
buggy compression, etc.

Moreover identity digest algorithms (eg. ID-SHA-256 and ID-SHA-512) allow
piecing together a resource from different sources (e.g. different servers that
perhaps apply different content codings) enabling the user-agent to detect that
the application-layer tasks completed properly, before handing off to say the
HTML parser, video player etc.

Even a simple mechanism for end-to-end validation is thus valuable.

## Digest and Content-Location in responses {#digest-and-content-location}

When a state-changing method returns the `Content-Location` header field, the
enclosed representation refers to the resource identified by its value and
`Digest` is computed accordingly.


## Usage in signatures {#usage-in-signatures}

Digital signatures are widely used together with checksums to provide the
certain identification of the origin of a message [NIST800-32]. Such signatures
can protect one or more HTTP fields and there are additional considerations when
`Digest` is included in this set.

Since the `Digest` field is a hash of a resource representation, it explicitly
depends on the `representation metadata` (eg. the values of `Content-Type`,
`Content-Encoding` etc). A signature that protects `Digest` but not other
`representation metadata` can expose the communication to tampering. For
example, an actor could manipulate the `Content-Type` field-value and cause a
digest validation failure at the recipient, preventing the application from
accessing the representation. Such an attack consumes the resources of both
endpoints. See also {{digest-and-content-location}}.

`Digest` SHOULD always be used over a connection which provides integrity at
the transport layer that protects HTTP fields.

A `Digest` field using NOT RECOMMENDED digest-algorithms SHOULD NOT be used in
signatures.

Using signatures to protect the Digest of an empty representation
allows receiving endpoints to detect if an eventual payload has been stripped or added.

## Usage in trailers

When used in trailers, the receiver gets the digest value after the payload body
and may thus be tempted to process the data before validating the digest value.
Instead, data should only be processed after validating the Digest.

If received in trailers, Digest MUST NOT be discarded;
instead it MAY be merged in the header section (See Section 5.6.2 of {{SEMANTICS}}).

Not every digest-algorithm is suitable for trailers, as they may require to pre-process
the whole payload before sending a message (eg. see {{?I-D.thomson-http-mice}}).

## Usage with encryption

Digest may expose information details of encrypted payload when the checksum
is computed on the unecrypted data.
An example of that is the use of the `id-sha-256` digest algorithm
in conjuction with the encrypted content-coding {{?RFC8188}}.

## Algorithm Agility

...

# IANA Considerations

## Establish the HTTP Digest Algorithm Values

This memo sets this spec to be the establishing document for the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)

## The "status" Field in the HTTP Digest Algorithm Values

This memo adds the field "Status" to the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry. The allowed values for the "Status" fields are described below.

   Status
   :  Specify "standard", "experimental", "historic",
      "obsoleted", or "deprecated" according to the type
      and status of the primary document in which the algorithm
      is defined.

## Deprecate "MD5" Digest Algorithm {#iana-MD5}

This memo updates the "MD5" digest algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: MD5
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Update "CRC32C" Digest Algorithm {#iana-CRC32C}

This memo updates the "CRC32c" digest algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: CRC32c
* Description: The CRC32c algorithm is a 32-bit cyclic redundancy check. It
  achieves a better hamming distance (for better error-detection performance)
  than many other 32-bit CRC functions. Other places it is used include iSCSI
  and SCTP. The 32-bit output is encoded in hexadecimal (using between 1 and 8
  ASCII characters from 0-9, A-F, and a-f; leading 0's are allowed). For
  example, CRC32c=0a72a4df and crc32c=A72A4DF are both valid checksums for the
  3-byte message "dog".
* Reference: {{!RFC4960}} appendix B, this document.
* Status: standard.

## Obsolete "SHA" Digest Algorithm {#iana-SHA}

This memo updates the "SHA" digest algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: SHA
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Obsolete "ADLER32" Digest Algorithm {#iana-adler-32}

This memo updates the "ADLER32" digest algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: ADLER32
* Description: The ADLER32 algorithm is a checksum specified in [RFC1950] "ZLIB
  Compressed Data Format". The 32-bit output is encoded in hexadecimal (using
  between 1 and 8 ASCII characters from 0-9, A-F, and a-f; leading 0's are
  allowed). For example, ADLER32=03da0195 and ADLER32=3DA0195 are both valid
  checksums for the 4-byte message "Wiki". This algorithm is obsoleted and
  SHOULD NOT be used.
* Status: obsoleted

## The "ID-SHA-256" Digest Algorithm {#iana-ID-SHA-256}

This memo registers the "ID-SHA-256" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: ID-SHA-256
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## The "ID-SHA-512" Digest Algorithm {#iana-ID-SHA-512}

This memo registers the "ID-SHA-512" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: ID-SHA-512
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Changes compared to RFC5843

The status of "MD5" has been updated to "deprecated", and its description states
that this algorithm MUST NOT be used.

The status of "SHA" has been updated to "obsoleted", and its description states
that this algorithm is NOT RECOMMENDED.

The status for "CRC32C" has been updated to "standard".

The "ID-SHA-256" and "ID-SHA-512" algorithms have been added to the registry.

## Want-Digest Field Registration

This section registers the `Want-Digest` field in the "Hypertext Transfer
Protocol (HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Want-Digest`

Status:  permanent

Specification document(s):  {{want-digest}} of this document

## Digest Header Field Registration

This section registers the `Digest` field in the "Hypertext Transfer Protocol
(HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Digest`

Status:  permanent

Specification document(s):  {{digest}} of this document

--- back

# Resource Representation and Representation-Data {#resource-representation}

The following examples show how representation metadata, payload transformations
and method impacts on the message and payload body. When the payload body
contains non-printable characters (eg. when it is compressed) it is shown as
base64-encoded string.

A request with a json object without any content coding.

Request:

~~~
PUT /entries/1234 HTTP/1.1
Content-Type: application/json

{"hello": "world"}
~~~

Here is a gzip-compressed json object
using a content coding.

Request:

~~~
PUT /entries/1234 HTTP/1.1
Content-Type: application/json
Content-Encoding: gzip

H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=
~~~

Now the same payload body conveys a malformed json object.

Request:

~~~
PUT /entries/1234 HTTP/1.1
Content-Type: application/json

H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=
~~~

A Range-Request alters the payload body, conveying a partial representation.

Request:

~~~
GET /entries/1234 HTTP/1.1
Range: bytes=1-7

~~~

Response:

~~~
HTTP/1.1 206 Partial Content
Content-Encoding: gzip
Content-Type: application/json
Content-Range: bytes 1-7/18

iwgAla3RXA==
~~~


Now the method too alters the payload body.

Request:

~~~
HEAD /entries/1234 HTTP/1.1
Accept: application/json
Accept-Encoding: gzip

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip

~~~

Finally the semantics of an HTTP response might decouple the effective request URI
from the enclosed representation. In the example response below, the
`Content-Location` header field indicates that the enclosed representation
refers to the resource available at `/authors/123`.

Request:

~~~
POST /authors/ HTTP/1.1
Accept: application/json
Content-Type: application/json

{"author": "Camilleri"}
~~~

Response:

~~~
HTTP/1.1 201 Created
Content-Type: application/json
Content-Location: /authors/123
Location: /authors/123

{"id": "123", "author": "Camilleri"}
~~~


# FAQ

1. Why remove all references to content-md5?

   Those were unnecessary to understanding and using this spec.

2. Why remove references to instance manipulation?

   Those were unnecessary for correctly using and applying the spec. An example
   with Range Request is more than enough. This doc uses the term "partial
   representation" which should group all those cases.

3. How to use `Digest` with `PATCH` method?

   See {{acting-on-resources}}.

4. Why remove references to delta-encoding?

   Unnecessary for a correct implementation of this spec. The revised spec can
   be nicely adapted to "delta encoding", but all the references here to delta
   encoding don't add anything to this RFC. Another job would be to refresh
   delta encoding.

5. Why remove references to Digest Authentication?

   This RFC seems to me completely unrelated to Digest Authentication but for
   the word "Digest".

6. What changes in `Want-Digest`?

   The contentMD5 token defined in Section 5 of [RFC3230] is deprecated by {{deprecate-contentMD5}}.

   To clarify that `Digest` and `Want-`Digest can be used in both requests and responses
   - [RFC3230] carefully uses `sender` and `receiver` in their definition -
   we added examples on using `Want-Digest` in responses to advertise the supported
   digest-algorithms and the inability to accept requests with unsupported
   digest-algorithms.

7. Does this spec changes supported algorithms?

   This RFC updates [RFC5843] which is still delegated for all algorithms
   updates, and adds two more algorithms: ID-SHA-256 and ID-SHA-512 which allows
   to send a checksum of a resource representation with no content codings
   applied.

8. What about mid-stream trailers?

   While
   [mid-stream trailers](https://github.com/httpwg/http-core/issues/313#issuecomment-584389706)
   are interesting, since this specification is a rewrite of [RFC3230] we do not
   think we should face that. As a first thought, nothing in this document
   precludes future work that would find a use for mid-stream trailers, for
   example an incremental digest-algorithm. A document defining such a
   digest-algorithm is best positioned to describe how it is used.

# Acknowledgements
{:numbered="false"}
The vast majority of this document is inherited from [RFC3230], so thanks
to J. Mogul and A. Van Hoff for their great work.
The original idea of refreshing this document arose from an interesting
discussion with M. Nottingham, J. Yasskin and M. Thomson when reviewing
the MICE content coding.


# Code Samples
{:numbered="false"}

_RFC Editor: Please remove this section before publication._

How can I generate and validate the Digest values shown in the examples
throughout this document?

The following python3 code can be used to generate digests for json objects
using SHA algorithms for a range of encodings. Note that these are formatted as
base64. This function could be adapted to other algorithms and should take into
account their specific formatting rules.

~~~
import base64, json, hashlib, brotli


def digest(item, encoding=lambda x: x, algorithm=hashlib.sha256):
    json_bytes = json.dumps(item).encode()
    content_encoded = encoding(json_bytes)
    checksum_bytes = algorithm(content_encoded).digest()
    return base64.encodebytes(checksum_bytes).strip()


item = {"hello": "world"}

print("Encoding | digest-algorithm | digest-value")
print("Identity | sha256 |", digest(item))
# Encoding | digest-algorithm | digest-value
# Identity | sha256 | 4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

print("Encoding | digest-algorithm | digest-value")
print("Brotli | sha256 |", digest(item, encoding=brotli.compress))
# Encoding | digest-algorithm | digest-value
# Brotli , sha256 4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=


print("Encoding | digest-algorithm | digest-value")
print("Identity | sha512 |", digest(item, algorithm=hashlib.sha512))
# Encoding | digest-algorithm | digest-value
# Identity | sha512 | b'WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2s
vX+TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==\n'
~~~

# Changes
{:numbered="false"}

_RFC Editor: Please remove this section before publication._


## Since draft-ietf-httpbis-digest-headers-00

* Align title with document name
* Add id-sha-* algorithm examples #880
* Reference [RFC6234] and [RFC3174] instead of FIPS-1
* Deprecate MD5
* Obsolete ADLER-32 but don't forbid it #828
* Update CRC32C value in IANA table #828
* Use when acting on resources (POST, PATCH) #853
* Added Relationship with SRI, draft Use Cases #868, #971
* Warn about the implications of `Content-Location`

## Since draft-ietf-httpbis-digest-headers-01

* Digest of error responses is computed on the error representation-data #1004
* Effect of HTTP semantics on payload and message body moved to appendix #1122
* Editorial refactoring, moving headers sections up. #1109-#1112, #1116,
  #1117, #1122-#1124

## Since draft-ietf-httpbis-digest-headers-02

* Deprecate SHA-1 #1154
* Avoid id-* with encrypted content
* Digest is independent from MESSAGING and HTTP/1.1 is not normative #1215
* Identity is not a valid field value for content-encoding #1223
* Mention trailers #1157
* Reference httpbis-semantics #1156
