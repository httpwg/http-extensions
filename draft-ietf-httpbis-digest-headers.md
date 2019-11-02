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
    country: Italy
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
  RFC7230:
  RFC7231:
  RFC7233:
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
  IACR-2019-459:
    title: From Collisions to Chosen-Prefix Collisions Application to Full SHA-1
    author:
      -
         ins: G. Leurent
         org: Inria, France
      -
         ins: T. Peyrin
         org: Nanyang Technological University, Singapore; Temasek Laboratories, Singapore
    date: 2019-05-06
    target: https://eprint.iacr.org/2019/459.pdf

informative:
  RFC2818:
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

This document defines the Digest and Want-Digest header fields for HTTP, thus allowing client
 and server to negotiate an integrity checksum of the exchanged resource representation data.

This document obsoletes RFC 3230. It replaces the term "instance" with "representation",
which makes it consistent  with the HTTP Semantic and Context defined in RFC 7231.


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

## A Brief History of Integrity Header Fields

The Content-MD5 header field was originally introduced to provide integrity,
but HTTP/1.1 ([RFC7231], Appendix B) obsoleted it:

  > The Content-MD5 header field has been removed because it was
  > inconsistently implemented with respect to partial responses.

[RFC3230] provided a more flexible solution introducing the concept of "instance",
and the header fields `Digest` and `Want-Digest`.

## This Proposal

The concept of `selected representation` defined in [RFC7231] made [RFC3230] definitions
inconsistent with the current standard. A refresh was then required.

This document updates the `Digest` and `Want-Digest` header field definitions to align with [RFC7231] concepts.

This approach can be easily adapted to use-cases where the transferred data
does require some sort of manipulation to be considered a representation
or conveys a partial representation of a resource (eg. Range Requests [RFC7233]).

Changes are semantically compatible with existing implementations
and better cover both the request and response cases.

The value of `Digest` is calculated on selected representation,
which is tied to the value contained in any `Content-Encoding` or `Content-Type` header fields.
Therefore, a given resource may have multiple different digest values.

To allow both parties to exchange a Digest of a representation
with [no content codings](https://tools.ietf.org/html/rfc7231#section-3.1.2.1)
two more algorithms are added (`ID-SHA-256` and `ID-SHA-512`).

## Goals

The goals of this proposal are:

   1. Digest coverage for either the resource's `representation data` or `selected representation data`
      communicated via HTTP.

   2. Support for multiple digest algorithms.

   3. Negotiation of the use of digests.

The goals do not include:

  HTTP Message integrity:
  : The digest mechanism described here does not cover the full HTTP message
    nor its semantic, as representation metadata are not included in the
    checksum.

  Header field integrity:
  : The digest mechanisms described here cover only representation and selected representation data,
    and do not protect the integrity of associated
    representation metadata or other message header fields.

  Authentication:
  : The digest mechanisms described here are not meant to support
    authentication of the source of a digest or of a message or
    anything else.  These mechanisms, therefore, are not a sufficient
    defense against many kinds of malicious attacks.

  Privacy:
  : Digest mechanisms do not provide message privacy.

  Authorization:
  : The digest mechanisms described here are not meant to support
    authorization or other kinds of access controls.


## Notational Conventions
The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 ([RFC2119] and [RFC8174])
when, and only when, they appear in all capitals, as shown here.

This document uses the Augmented BNF defined in [RFC5234] and updated
by [RFC7405] along with the "#rule" extension defined in Section 7 of
[RFC7230].

The definitions
"representation", "selected representation",
"representation data", "representation metadata",
and "payload body"
in this document are to be
interpreted as described in [RFC7230] and [RFC7231].

The definition "validator"
in this document is to be
interpreted as described in Section 7.2 of [RFC7231].


# Resource Representation and Representation-Data {#resource-representation}

To avoid inconsistencies, an integrity mechanism for HTTP messages
should decouple the checksum calculation from:

- the payload body - which may be altered by mechanism like Range Requests [RFC7233] or the method (eg. HEAD);

- and the message body - which depends on `Transfer-Encoding` and whatever transformations
the intermediaries may apply.

The following examples show how representation metadata, payload transformations and method
impacts on the message and payload body.

Here is a gzip-compressed json object

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


# Digest Algorithm Values {#algorithms}

   Digest algorithm values are used to indicate a specific digest
   computation.  For some algorithms, one or more parameters may be
   supplied.

~~~
   digest-algorithm = token
~~~

   The BNF for "parameter" is as is used in [RFC7230].
   All digest-algorithm values are case-insensitive.


   The Internet Assigned Numbers Authority (IANA) acts as a registry for
   digest-algorithm values.  The registry contains the
   following tokens.


  SHA-256:
  :  
    * Description: The SHA-256 algorithm [RFC6234].  The output of
      this algorithm is encoded using the base64 encoding [RFC4648].
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  SHA-512:
  :  
    * Description: The SHA-512 algorithm [RFC6234].  The output of
      this algorithm is encoded using the base64 encoding [RFC4648].
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  MD5:
  :  
    * Description: The MD5 algorithm, as specified in [RFC1321].
      The output of this algorithm is encoded using the
      base64 encoding  [RFC4648].
      The MD5 algorithm MUST NOT be used as it's now vulnerable
      to collision attacks [CMU-836068].
    * Reference: [RFC1321], [RFC4648], this document.
    * Status: deprecated

  SHA:
  :  
    * Description:  The SHA-1 algorithm [RFC3174].  The output of this
      algorithm is encoded using the base64 encoding  [RFC4648].
      The SHA algorithm is NOT RECOMMENDED as it's now vulnerable
      to collision attacks [IACR-2019-459].
    * Reference: [RFC3174], [RFC6234], [RFC4648], this document.
    * Status: obsoleted

  UNIXsum:
  :  
    * Description: The algorithm computed by the UNIX "sum" command,
      as defined by the Single UNIX Specification,
      Version 2 [UNIX].  The output of this algorithm is an
      ASCII decimal-digit string representing the 16-bit
      checksum, which is the first word of the output of
      the UNIX "sum" command.
    * Reference: [UNIX], this document.
    * Status: standard

  UNIXcksum:
  :  
    * Description: The algorithm computed by the UNIX "cksum" command,
      as defined by the Single UNIX Specification,
      Version 2 [UNIX].  The output of this algorithm is an
      ASCII digit string representing the 32-bit CRC,
      which is the first word of the output of the UNIX
      "cksum" command.
    * Reference: [UNIX], this document.
    * Status: standard

To allow sender and recipient to provide a checksum which is independent from `Content-Encoding`,
the following additional algorithms are defined:

  ID-SHA-512:
  :  
    * Description: The sha-512 digest of the representation-data of the resource when no
    content coding is applied (eg. `Content-Encoding: identity`)
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard


  ID-SHA-256:
  :  
    * Description: The sha-256 digest of the representation-data of the resource when no
      content coding is applied (eg. `Content-Encoding: identity`)
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

   If other digest-algorithm values are defined, the associated encoding
   MUST either be represented as a quoted string, or MUST NOT include
   ";" or "," in the character sets used for the encoding.

## Representation Digest {#representation-digest}

A representation  digest is the value of the output of a digest
algorithm, together with an indication of the algorithm used (and any
parameters).

~~~
   representation-data-digest = digest-algorithm "="
                                <encoded digest output>
~~~

As explained in {{resource-representation}} the digest
is computed on the entire selected `representation data` of the resource
defined in [RFC7231]:

~~~
   representation-data := Content-Encoding( Content-Type( bits ) )
~~~


The encoded digest output uses the encoding format defined for the
specific digest-algorithm.

### digest-algorithm Encoding Examples

The `sha-256` digest-algorithm uses base64 encoding.
Note that digest-algorithm values are case insensitive.


~~~
   sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
~~~

The "UNIXsum" digest-algorithm uses ASCII string of decimal digits.

~~~
   UNIXsum=30637
~~~

# Header Field Specifications

The following headers are defined

## Want-Digest {#want-digest-header}

The Want-Digest message header field indicates the sender's desire to
receive a representation digest on messages associated with
the request URI and representation metadata.

~~~
   Want-Digest = "Want-Digest" ":" OWS 1#want-digest-value
   want-digest-value = digest-algorithm [ ";" "q" "=" qvalue]
   qvalue = ( "0"  [ "."  0*1DIGIT ] ) /  ( "1"  [ "."  0*1( "0" ) ] )
~~~

If a digest-algorithm is not accompanied by a qvalue, it is treated
as if its associated qvalue were 1.0.

The sender is willing to accept a digest-algorithm if and only if it
is listed in a Want-Digest header field of a message, and its qvalue
is non-zero.

If multiple acceptable digest-algorithm values are given, the
sender's preferred digest-algorithm is the one (or ones) with the
highest qvalue.

Two examples of its use are

~~~
   Want-Digest: sha-256
   Want-Digest: SHA-512;q=0.3, sha-256;q=1, md5;q=0
~~~

## Digest {#digest-header}

The Digest header field provides a digest of the representation data.

~~~
   Digest = "Digest" ":" OWS 1#representation-data-digest
~~~

`Representation data` might be:

- fully contained in the message body,
- partially-contained in the message body,
- or not at all contained in the message body.

The resource is specified by
the effective request URI
and any `validator` contained in the message.

For example, in a response to a HEAD request, the digest is calculated using the
representation data that would have been enclosed in the payload body
if the same request had been a GET.

Digest can be used in requests too.
Returned value depends on the representation metadata header fields.

A Digest header field MAY contain multiple representation-data-digest values.
This could be useful for responses expected to reside in caches
shared by users with different browsers, for example.

A recipient MAY ignore any or all of the representation-data-digests in a Digest
header field. This allows the recipient to chose which digest-algorithm(s) to use for
validation instead of verifying every received representation-data-digest.

A sender MAY send a representation-data-digest using a digest-algorithm without
knowing whether the recipient supports the digest-algorithm, or even
knowing that the recipient will ignore it.

Two examples of its use are

~~~
   Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==
   Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=, id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
~~~


# Use of Digest when acting on resources {#acting-on-resources}

POST and PATCH requests may appear to convey partial representations
but are semantically acting on resources.
The enclosed representation, including its metadata refers to that action.

In these requests the representation digest MUST be computed on
the representation-data of that action.

This is the only possible choice because representation digest
requires complete representation metadata (see {{representation-digest}}).

In responses,

- if the representation describes the status of the request,
  `Digest` MUST be computed on the enclosed representation
   (see {{post-referencing-action}} );

- if there is a referenced resource
  `Digest` MUST be computed on the selected representation of the referenced resource
   even if that is different from the target resource.
   That may or may not result in computing `Digest` on the enclosed representation.

The latter case might be done accordingly to the HTTP semantics of the given method,
for example using the `Content-Location` header field.

Differently from `Content-Location`, which is representation metadata,
the `Location` header field does not affect `Digest`.

## Digest and PATCH

In PATCH requests
the representation digest MUST be computed on the patch document.

This is because the representation metadata refers
to the patch document and not to the target resource (see Section 2 of {{?RFC5789}}).

In PATCH responses
the representation digest MUST be computed on
the selected representation of the patched resource.

`Digest` usage with PATCH is thus very similar to the POST one,
but with the resource's own semantic partly implied by the method and by the patch document.

# Deprecate Negotiation of Content-MD5

This RFC deprecates the negotiation of Content-MD5 as
it has been obsoleted by [RFC7231]

# Broken Cryptographic Algorithms

The MD5 algorithm MUST NOT be used as it has been found vulnerable to collision
attacks [CMU-836068].

The SHA algorithm is NOT RECOMMENDED as it has been found vulnerable to
collision attacks [IACR-2019-459].

# Relationship to Subresource Integrity (SRI)

Subresource Integrity [SRI] is an integrity mechanism that shares some
similarities to the present document's mechanism. However, there are differences
in motivating factors, threat model and specification of integrity digest
generation, signalling and validation.

SRI allows a first-party authority to declare an integrity assertion on a
resource served by a first or third party authority. This is done via the
`integrity` attribute that can added to `script` or `link` HTML elements.
Therefore, the integrity assertion is always made out-of-band to the resource
fetch. In contrast, the `Digest` header field is supplied in-band alongside the
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
resources it transfers to a server. In contrast, the `Digest` header field can
appear on requests.

## Supporting Both SRI and Representation Digest

The SRI and Representation Digest mechanism are different and complementary but
one is not capable of replacing the other because they have have different
threat, security and implementation properties. 

A user agent that supports both mechanisms is expected to apply the rules
specified for each but since the two mechanisms are independent, the ordering is
not important. However, a user agent supporting both could benefit from
performing representation digest validation first because the it does not
require a conversion to into identity encoding. 

There is a chance that a user agent supporting both mechanisms may find one
validates successfully while the other fails. This document specifies no
requirements or guidance for user agents that experience such cases.


# Examples of Unsolicited Digest

The following examples demonstrate interactions where a server responds with a
`Digest` header field even though the client did not solicit one using `Want-Digest`.


## Server Returns Full Representation Data

Request:

~~~
GET /items/123

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: identity
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

## Server Returns No Representation Data

As there is no content coding applied, the `sha-256` and the `id-sha-256`
digest-values are the same.

Request:

~~~
HEAD /items/123

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: identity
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
Content-Encoding: identity
Content-Range: bytes 1-7/18
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

"hello"
~~~

## Client and Server Provide Full Representation Data

Digest can be used in requests too. Returned value depends on the representation metadata header fields.

Request:

~~~
PUT /items/123
Content-Type: application/json
Content-Encoding: identity
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

Request `Digest` value is calculated on the enclosed payload.
Response `Digest` value depends on the representation metadata header fields,
including `Content-Encoding: br`
even when the response does not contain a payload body.


Request:

~~~
PUT /items/123
Content-Type: application/json
Content-Encoding: identity
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

Request:

~~~
PUT /items/123 HTTP/1.1
Content-Type: application/json
Content-Encoding: identity
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: br
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=, id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~

## POST Response does not Reference the Request URI {#post-not-request-uri}

Request `Digest` value is computed on the enclosed representation (see {{acting-on-resources}}). 

The representation enclosed in the response
refers to the resource identified by `Content-Location`
(see [RFC7231] Section 3.1.4.2 and Section 3.1.4.1 point 4).

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

Note that a `204 No Content` response without a payload body 
but with the same `Digest` field-value would have been legitimate too.

## POST Response Describes the Request Status {#post-referencing-action}

Request `Digest` value is computed on the enclosed representation (see {{acting-on-resources}}). 

The representation enclosed in the response describes the status of the request,
so `Digest` is computed on that enclosed representation.

Response `Digest` has no explicit relation with the resource referenced by `Location`.

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

{"status": "created", "id": "123", "ts": 1569327729, "instance": "/books/123"}
~~~

## Digest with PATCH

This case is analogous to a POST request where
the target resource reflects the effective request URI.

The PATCH request uses
the `application/merge-patch+json` media type defined in {{?RFC7396}}.

`Digest` is calculated on the enclosed payload,
which corresponds to the patch document.

The response `Digest` is computed
on the complete representation of the patched resource.

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

Note that a `204 No Content` response without a payload body 
but with the same `Digest` field-value would have been legitimate too.

# Examples of Want-Digest Solicited Digest

The following examples demonstrate interactions where a client solicits a
`Digest` using `Want-Digest`.

## Server Selects Client's Least Preferred Algorithm

The client requests a digest, preferring sha. The server is free to reply with sha-256 anyway.

Request:

~~~
GET /items/123 HTTP/1.1
Want-Digest: sha-256;q=0.3, sha;q=1

~~~

Response:

~~~
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: identity
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
Content-Encoding: identity
Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==

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
`representation data`, but not HTTP `representation metadata` header fields,
from certain kinds of accidental corruption.

`Digest` is not intended as general protection against malicious tampering with
HTTP messages, this can be achieved by combining it with other approaches such
as transport-layer security or digital signatures.

## Broken Cryptographic Algorithms

Cryptographic algorithms are intended to provide a proof of integrity
suited towards cryptographic constructions such as signatures.

However, these rely on collision-resistance for their security proofs [CMU-836068].
The MD5 and SHA-1 algorithms are vulnerable to collisions attacks,
so MD5 MUST NOT be used and SHA-1 is NOT RECOMMENDED for use with `Digest`.

## Other Deprecated Algorithms

The ADLER32 algorithm defined in [RFC1950] has been deprecated
by [RFC3309] because under certain conditions it provides
weak detection of errors and is now NOT RECOMMENDED  for use with `Digest`.

## Digest for End-to-End Integrity

`Digest` alone does not provide end-to-end integrity
of HTTP messages over multiple hops, as it just covers
the `representation data` and not the `representation metadata`.

Besides, it allows to protect `representation data` from
buggy manipulation, buggy compression, etc.

Moreover identity digest algorithms (eg. ID-SHA-256 and ID-SHA-512)
allow piecing together a resource from different sources
(e.g. different servers that perhaps apply different content codings)
enabling the user-agent to detect that the application-layer tasks completed properly,
before handing off to say the HTML parser, video player etc.

Even a simple mechanism for end-to-end validation is thus valuable.

## Usage in Signatures

Digital signatures are widely used together with checksums to provide the
certain identification of the origin of a message [NIST800-32]. Such signatures
can protect one or more header fields and there are additional considerations
when `Digest` is included in this set.

Since the `Digest` header field is a hash of a resource representation, it
explicitly depends on the `representation metadata` (eg. the values of
`Content-Type`, `Content-Encoding` etc). A signature that protects `Digest` but
not other `representation metadata` may expose the communication to tampering.
For example, an actor could manipulate the `Content-Type` field-value and cause
a digest validation failure at the recipient, preventing the application from
accessing the representation. Such an attack consumes the resources of both
endpoints.

`Digest` SHOULD always be used over a connection which provides
integrity at transport layer that protects HTTP header fields.

A `Digest` header field using NOT RECOMMENDED digest-algorithms SHOULD NOT be used in signatures.

## Message Truncation

...

## Algorithm Agility

...

# IANA Considerations

## Establish the HTTP Digest Algorithm Values

This memo sets this spec to be the establishing
document for the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)

## The "status" Field in the HTTP Digest Algorithm Values

This memo adds the field "Status" to the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry. The allowed values for the "Status" fields are described below.

   Status
   :  Specify "standard", "experimental", "historic",
      "obsoleted", or "deprecated" according to the type
      and status of the primary document in which the algorithm
      is defined.

## Deprecate "MD5" Digest Algorithm {#iana-MD5}

This memo updates the "MD5" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: MD5
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Update "CRC32C" Digest Algorithm {#iana-CRC32C}

This memo updates the "CRC32c" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: CRC32c
* Description: The CRC32c algorithm is a 32-bit cyclic redundancy check.
  It achieves a better hamming distance (for better error-detection performance) than many other 32-bit CRC functions.
  Other places it is used include iSCSI and SCTP.
  The 32-bit output is encoded in hexadecimal (using between 1 and 8 ASCII characters from 0-9, A-F, and a-f; leading 0's are allowed).
  For example, CRC32c=0a72a4df and crc32c=A72A4DF are both valid checksums for the 3-byte message "dog".
* Reference: {{!RFC4960}} appendix B, this document.
* Status: standard.

## Obsolete "SHA" Digest Algorithm {#iana-SHA}

This memo updates the "SHA" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: SHA
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Obsolete "ADLER32" Digest Algorithm {#iana-adler-32}

This memo updates the "ADLER32" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: ADLER32
* Description: The ADLER32 algorithm is a checksum specified in [RFC1950] "ZLIB Compressed Data Format".
  The 32-bit output is encoded in hexadecimal (using between 1 and 8 ASCII characters from 0-9, A-F, and a-f; leading 0's are allowed).
  For example, ADLER32=03da0195 and ADLER32=3DA0195 are both valid checksums for the 4-byte message "Wiki".
  This algorithm is obsoleted and SHOULD NOT be used.
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

The status of "MD5" has been updated to "deprecated",
and its description states that this algorithm MUST NOT be used.

The status of "SHA" has been updated to "obsoleted",
and its description states that this algorithm is NOT RECOMMENDED.

The status for "CRC32C" has been updated to "standard".

The "ID-SHA-256" and "ID-SHA-512" algorithms have been added to
the registry.

## Want-Digest Header Field Registration

This section registers the `Want-Digest` header field in the "Permanent Message
Header Field Names" registry ({{!RFC3864}}).

Header field name:  `Want-Digest`

Applicable protocol:  http

Status:  standard

Author/Change controller:  IETF

Specification document(s):  {{want-digest-header}} of this document

## Digest Header Field Registration

This section registers the `Digest` header field in the "Permanent Message
Header Field Names" registry ({{!RFC3864}}).

Header field name:  `Digest`

Applicable protocol:  http

Status:  standard

Author/Change controller:  IETF

Specification document(s):  {{digest-header}} of this document

--- back


# FAQ

1. Why remove all references to content-md5?

   Those were unnecessary to understanding and using this spec.

2. Why remove references to instance manipulation?

   Those were unnecessary for correctly using and applying the spec. An
   example with Range Request is more than enough. This doc uses the term
   "partial representation" which should group all those cases.

3. How to use `Digest` with `PATCH` method?

   See {{acting-on-resources}}.

4. Why remove references to delta-encoding?

   Unnecessary for a correct implementation of this spec. The revised spec can be nicely adapted
   to "delta encoding", but all the references here to delta encoding don't add anything to this RFC.
   Another job would be to refresh delta encoding.

5. Why remove references to Digest Authentication?

   This RFC seems to me completely unrelated to Digest Authentication but for the word "Digest".

6. What changes in `Want-Digest`?

   We allow to use the `Want-Digest` in responses to advertise the supported digest-algorithms
   and the inability to accept requests with unsupported digest-algorithms.

7. Does this spec changes supported algorithms?

   This RFC updates [RFC5843] which is still delegated for all algorithms updates,
   and adds two more algorithms: ID-SHA-256 and ID-SHA-512 which allows to
   send a checksum of a resource representation with no content codings applied.

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
using SHA algorithms for a range of encodings.
Note that these are formatted as base64.
This function could be adapted to other algorithms
and should take into account their specific formatting rules.

~~~
import base64, json, hashlib, brotli


def digest(item, encoding=lambda x: x, algorithm=hashlib.sha256):
    json_bytes = json.dumps(item).encode()
    content_encoded = encoding(json_bytes)
    checksum_bytes = algorithm(content_encoded).digest()
    return base64.encodebytes(checksum_bytes).strip()


item = {"hello": "world"}

print("Identity encoding, sha256", digest(item))
# Out: Identity encoding, sha256 4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

print("Brotli encoding, sha256", digest(item, encoding=brotli.compress))
# Out: Brotli encoding, sha256 4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

print("Identity encoding, sha512", digest(item, algorithm=hashlib.sha512))
# Out: Identity encoding, sha512 b'WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==\n'
~~~

# Changes
{:numbered="false"}

_RFC Editor: Please remove this section before publication._


## Since draft-ietf-httpbis-digest-headers-00

* Align title with document name
* Add id-sha-* algorithm examples
* Reference [RFC6234] and [RFC3174] instead of FIPS-1
* Deprecate MD5
* Obsolete ADLER-32 but don't forbid it
* Update CRC32C value in IANA table
