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
  RFC3230:
  RFC2119:
  RFC5789:
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

Integrity protection for HTTP content is multi layered and
is usually achieved across the protocol stack:
TCP checksums and TLS [RFC2818] record to name but some.

The HTTP protocol does not provide means to protect the various
message parts. Besides, it might be desirable to add additional guarantees
to the ones provided by the transport layer (eg. HTTPS). This may be in order to:

- detect programming errors and corruption of stored data;
- address the need for the representation-data to remain unmodified throughout multiple hops;
- implement signature mechanisms that cover the desired parts of an HTTP exchange;
- provide additional protection against failures or attack (see [SRI]).

## Brief history of integrity header fields

The Content-MD5 header field was originally introduced to provide integrity,
but HTTP/1.1 ([RFC7231], Appendix B) obsoleted it:

  > The Content-MD5 header field has been removed because it was
  >  inconsistently implemented with respect to partial responses.

[RFC3230] provided a more flexible solution introducing the concept of "instance",
and the header fields `Digest` and `Want-Digest`.

## This proposal

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

The definitions "representation", "selected representation", "representation data",
"representation metadata" and "payload body" in this document are to be
interpreted as described in [RFC7230] and [RFC7231].


# Resource representation and representation-data {#resource-representation}

To avoid inconsistencies, an integrity mechanism for HTTP messages
should decouple the checksum calculation:

- from the payload body - which may be altered by mechanism like Range Requests [RFC7233] or the method (eg. HEAD);

- and from the message body - which depends on `Transfer-Encoding` and whatever tranformations
the intermediaries may apply.

The following examples show how representation metadata, payload tranformations and method
impacts on the message and payload body.

Here is a gzip-compressed json object

~~~
Request:

    PUT /entries/1234 HTTP/1.1
    Content-Type: application/json
    Content-Encoding: gzip

    H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=

~~~

Now the same payload body conveys a malformed json object.

~~~
Request:

    PUT /entries/1234 HTTP/1.1
    Content-Type: application/json

    H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=

~~~

A Range-Request alters the payload body, conveying a partial representation.

~~~
Request:

    GET /entries/1234 HTTP/1.1
    Range: bytes=1-7

Response:

    HTTP/1.1 206 Partial Content
    Content-Encoding: gzip
    Content-Type: application/json
    Content-Range: bytes=1-7

    iwgAla3RXA==
~~~


Now the method too alters the payload body.

~~~
Request:

    HEAD /entries/1234 HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip

Response:

    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Encoding: gzip

~~~


# Digest Algorithm values {#algorithms}

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

## Representation digest {#representation-digest}

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

### digest-algorithm encoding examples

The `sha-256` digest-algorithm uses base64 encoding.
Note that digest-algoritm values are case insensitive.


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
receive a representation digest on messages associated with the Request-
URI and representation metadata.

    Want-Digest = "Want-Digest" ":" OWS 1#want-digest-value
    want-digest-value = digest-algorithm [ ";" "q" "=" qvalue]
    qvalue = ( "0"  [ "."  0*1DIGIT ] ) /  ( "1"  [ "."  0*1( "0" ) ] )

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

The resource is specified by the effective
Request-URI and any cache-validator contained in the message.

For example, in a response to a HEAD request, the digest is calculated using  the
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
...

# Deprecate Negotiation of Content-MD5

This RFC deprecates the negotiation of Content-MD5 as
it has been obsoleted by [RFC7231]

# Broken cryptographic algorithms

The MD5 algorithm MUST NOT be used as it's now vulnerable
to collision attacks [CMU-836068].

The SHA algorithm is NOT RECOMMENDED as it's now vulnerable
to collision attacks [IACR-2019-459].

# Examples


## Unsolicited Digest response

### Representation data is fully contained in the payload

~~~
Request:

  GET /items/123

Response:

  HTTP/1.1 200 Ok
  Content-Type: application/json
  Content-Encoding: identity
  Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

  {"hello": "world"}
~~~

###  Representation data is not contained in the payload

As there is no content coding applied, the `sha-256` and the `id-sha-256`
digest-values are the same.

~~~
Request:

  HEAD /items/123

Response:

  HTTP/1.1 200 Ok
  Content-Type: application/json
  Content-Encoding: identity
  Digest: id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

~~~

###  Representation data is partially contained in the payload i.e. range request

~~~

Request:

  GET /items/123
  Range: bytes=1-7

Response:

  HTTP/1.1 206 Partial Content
  Content-Type: application/json
  Content-Encoding: identity
  Content-Range: bytes 1-7/18
  Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

  "hello"

~~~

### Digest in both Request and Response. Returned value depends on representation metadata

Digest can be used in requests too. Returned value depends on the representation metadata header fields.

~~~
Request:

  PUT /items/123
  Content-Type: application/json
  Content-Encoding: identity
  Accept-Encoding: br
  Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

  {"hello": "world"}

Response:

  Content-Type: application/json
  Content-Encoding: br
  Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

  iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==

~~~


### Digest in both Request and Response. Representation data is not contained in the response payload

Returned `Digest` value depends on the representation metadata header fields,
even when the response does not contain a payload body.


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

  HTTP/1.1 204 No Content
  Content-Type: application/json
  Content-Encoding: br
  Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

~~~

### Digest in both Request and Response. Response uses id-sha-256.

The response contains two digest values:

- one with no content coding applied, which in this case accidentally
  matches the unencoded digest-value sent in the request;
- one taking into account the `Content-Encoding`.

~~~
Request:

  PUT /items/123
  Content-Type: application/json
  Content-Encoding: identity
  Accept-Encoding: br
  Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

  {"hello": "world"}

Response:

  Content-Type: application/json
  Content-Encoding: br
  Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=, id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

  iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==

~~~

## Want-Digest solicited digest responses

### Client request data is fully contained in the payload

The client requests a digest, preferring sha. The server is free to reply with sha-256 anyway.

~~~
Request:

  GET /items/123
  Want-Digest: sha-256;q=0.3, sha;q=1

Response:

  HTTP/1.1 200 Ok
  Content-Type: application/json
  Content-Encoding: identity
  Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

  {"hello": "world"}
~~~

###  A client requests an unsupported Digest, the server MAY reply with an unsupported digest

The client requests a sha digest only. The server is currently free to reply with a Digest containing an unsupported algorithm

~~~
Request:

  GET /items/123
  Want-Digest: sha;q=1

Response:

  HTTP/1.1 200 Ok
  Content-Type: application/json
  Content-Encoding: identity
  Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==

  {"hello": "world"}
~~~

### A client requests an unsupported Digest, the server MAY reply with a 400

The client requests a sha Digest, the server advises for sha-256 and sha-512

~~~
Request:

  GET /items/123
  Want-Digest: sha;q=1

Response:

  HTTP/1.1 400 Bad Request
  Want-Digest: sha-256, sha-512
~~~

...


# Security Considerations

## Digest does not protect the full HTTP message

This document specifies a data integrity mechanism that protects HTTP
`representation data`, but not HTTP `representation metadata` header fields,
from certain kinds of accidental corruption.

While it is not intended as general protection
against malicious tampering with HTTP messages,
this goal can be achieved using `Digest` together
with a transport-layer security mechanism and digital signatures.

## Broken cryptographic algorithms

Cryptogrphic alorithms are intended to provide a proof of integrity
suited towards cryptographic constructions such as signatures.

However, these rely on collision-resistance for their security proofs [CMU-836068].
The MD5 and SHA-1 algorithms are vulnerable to collisions attacks,
so MD5 MUST NOT be used and SHA-1 is NOT RECOMMENDED.

## Digest for end-to-end integrity

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

## Usage in signatures

Digital signatures are widely used together with checksums to provide
the certain identification of the origin of a message [NIST800-32].

It's important to note that, being the `Digest` header field an hash of a resource representation,
signing only the `Digest` header field, without all the `representation metatada` (eg.
the values of `Content-Type` and `Content-Encoding`) may expose the communication
to tampering.

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

## The "status" field in the HTTP Digest Algorithm Values

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


## Obsolete "SHA" Digest Algorithm {#iana-SHA}

This memo updates the "SHA" digest algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: SHA
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

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
and its description states that this algoritm MUST NOT be used.

The status of "SHA" has been updated to "obsoleted",
and its description states that this algorithm is NOT RECOMMENDED.

The status for all other algorithms have been updated to "standard".

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

# Change Log

RFC EDITOR PLEASE DELETE THIS SECTION.


# FAQ

1. Why remove all references to content-md5?

   Those were unnecessary to understanding and using this spec.

2. Why remove references to instance manipulation?

   Those were unnecessary for correctly using and applying the spec. An
   example with Range Request is more than enough. This doc uses the term
   "partial representation" which should group all those cases.

3. How to use `Digest` with `PATCH` method?

   The PATCH verb brings some complexities (eg. about representation metadata header fields, patch document format, ...),

   - PATCH entity-headers apply to the patch document and MUST NOT be applied to the target resource,
     see [RFC5789], Section 2.
   - servers shouldn't assume PATCH semantics for generic media types like "application/json" but should
     instead use a proper content-type, eg [RFC7396]
   - a `200 OK` response to a PATCH request would contain the digest of the patched item, and the etag of the new object.
     This behavior - tighly coupled to the application logic - gives the client low probability of guessing the actual
     outcome of this operation (eg. concurrent changes, ...)

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

# Changes

_RFC Editor: Please remove this section before publication._


## Since draft-ietf-httpbis-digest-headers-00

* Align title with document name
* Add id-sha-* algorithm examples
* Reference [RFC6234] and [RFC3174] instead of FIPS-1
* Deprecate MD5

