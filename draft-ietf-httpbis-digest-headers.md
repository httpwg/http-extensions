---
title: Digest Headers
abbrev:
docname: draft-ietf-httpbis-digest-headers-latest
category: std
obsoletes: 3230

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Digest

stand_alone: yes
smart_quotes: no
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

This document defines the HTTP Digest and Want-Digest fields, which allows
client and server to negotiate an integrity checksum of the exchanged resource
representation data.

This document obsoletes RFC 3230.


--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at
<https://lists.w3.org/Archives/Public/ietf-http-wg/>.

The source code and issues list for this draft can be found at
<https://github.com/httpwg/http-extensions>.


--- middle

# Introduction

HTTP does not define a means to protect the integrity of representations. When
HTTP messages are transferred between endpoints, the protocol might choose to
make use of features of the lower layer in order to provide some integrity
protection; for instance TCP checksums or TLS records [RFC2818].

This document defines the Digest HTTP integrity mechanism that acts on
representation data. It operates independent of transport integrity, offering
the potential to detect programming errors and corruption of data in flight or
at rest. It can be used across multiple hops in order to provide end-to-end
integrity guarantees, which can aid fault diagnosis when resources are
transferred across hops and system boundaries. Finally, it can be used to
validate integrity when reconstructing a resource fetched using different HTTP
connections.

This document obsoletes [RFC3230].

## Document Structure

This document describes Digest integrity for HTTP and is structured as follows:

- {{representation-digest}} describes concepts related to representation
  digests,
- {{digest}} defines the Digest request and response header and trailer field,
- {{want-digest}} defines the Want-Digest request and response header and
  trailer field,
- {{algorithms}}, {{broken-algorithms}}, {{deprecated-algorithms}} and
  {{deprecate-contentMD5}}  and  describe algorithms and their relation to
  Digest,
- {{acting-on-resources}} details computing representation digests,
- {{obsolete-parameters}} obsoletes Digest field parameters,
- {{sri}} describes the relationship between Digest and Subresource Integrity,
  and
- {{examples-unsolicited}} and {{examples-solicited}} provide examples of using
  Digest and Want-Digest.

## Concept Overview

This document defines the `Digest` request and response header and trailer
field. At a high level the value contains a checksum, computed over
`selected representation data`
(Section 3.2; {{!SEMANTICS=I-D.ietf-httpbis-semantics}}),
that the recipient can use to validate integrity. `Digest` supports
algorithm agility. The `Want-Digest` field allows endpoints to express interest
in `Digest` and preference of algorithms.

Basing `Digest` on the selected representation makes it straightforward to apply
it to use-cases where the transferred data requires some sort of
manipulation to be considered a representation, or conveys a partial
representation of a resource, for example Range Requests (see Section 14.2 of
{{SEMANTICS}}).

Historically, the Content-MD5 header field provided an HTTP integrity mechanism
but HTTP/1.1 ([RFC7231], Appendix B) obsoleted it due to inconsistent handling
of partial responses. [RFC3230] defined the concept of "instance" digests and a
more flexible integrity scheme to help address issues with Content-MD5. It first
introduced the `Digest` and `Want-Digest` fields. HTTP terminology has evolved
since [RFC3230] was published. The concept of "instance" has been superseded by
`selected representation`.

This document replaces [RFC3230]. The `Digest` and `Want-Digest` field
definitions are updated to align with the terms and notational conventions in
{{!SEMANTICS}}. Changes are intended to be semantically compatible with existing
implementations but note that negotiation of `Content-MD5` is deprecated
{{deprecate-contentMD5}}, `Digest` field parameters are obsoleted
{{obsolete-parameters}}, "md5" and "sha" digest-algorithms are obsoleted
{{broken-algorithms}}, and the "adler32" algorithm is deprecated
{{deprecated-algorithms}}.

Calculating the value of `Digest` using selected representation means it is tied
to the `Content-Encoding` and `Content-Type` header fields. Therefore, a given
resource may have multiple different digest values. To allow both parties to
exchange a Digest of a representation with no content codings (see Section 8.4.1
of {{SEMANTICS}}) two more digest-algorithms are added ("id-sha-256" and
"id-sha-512").

`Digest` is used for representation integrity. It does not provide integrity for
HTTP messages or fields. However, it can be combined with other mechanisms that
protect representation metadata, such as digital signatures, in order to protect
the phases of an HTTP exchange in whole or in part.

`Digest` does not define means for authentication, authorization or privacy.


## Notational Conventions
{::boilerplate bcp14}

This document uses the Augmented BNF defined in [RFC5234] and updated by
[RFC7405] along with the "#rule" extension defined in Section 5.6.1 of
{{SEMANTICS}}.

The definitions "representation", "selected representation", "representation
data", "representation metadata", and "content" in this document are to be
interpreted as described in {{SEMANTICS}}.

Algorithm names respect the casing used in their definition document (eg. SHA-1, CRC32c)
whereas digest-algorithm tokens are quoted (eg. "sha", "crc32c").

# Representation Digest {#representation-digest}

The representation digest is an integrity mechanism for HTTP resources
which uses a checksum  that is calculated independently of the content
(see Section 6.4 of {{SEMANTICS}}).
It uses the representation data (see Section 8.1 of {{SEMANTICS}}),
that can be fully or partially contained in the content, or not contained at all.

This takes into account the effect of the HTTP semantics on the messages;
for example, the content can be affected by Range Requests or methods such as HEAD,
while the way the content is transferred "on the wire" is dependent on other
transformations (e.g. transfer codings for HTTP/1.1 - see Section 6.1 of
{{?HTTP11=I-D.ietf-httpbis-messaging}}). To help illustrate how such things affect `Digest`,
several examples are provided in {{resource-representation}}.

A representation digest consists of
the value of a checksum computed on the entire selected `representation data`
(see Section 8.1 of {{SEMANTICS}}) of a resource identified according to Section 6.4.2 of {{SEMANTICS}}
together with an indication of the algorithm used:

~~~ abnf
   representation-data-digest = digest-algorithm "="
                                <encoded digest output>
~~~

When a message has no representation data
it is still possible to assert that no representation data was sent
computing the representation digest on an empty string
(see {{usage-in-signatures}}).

The checksum is computed using one of the digest-algorithms listed in {{algorithms}}
and then encoded in the associated format.

# The Digest Field {#digest}

The `Digest` field contains a comma-separated list of one or more representation digest values as
defined in {{representation-digest}}. It can be used in both requests and
responses.

~~~ abnf
   Digest = 1#representation-data-digest
~~~

For example:

~~~ http-message
Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                   AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==
~~~

The relationship between `Content-Location` (see Section 8.7 of
{{SEMANTICS}}) and `Digest` is demonstrated in
{{post-not-request-uri}}. A comprehensive set of examples showing the impacts of
representation metadata, payload transformations and HTTP methods on Digest is
provided in {{examples-unsolicited}} and {{examples-solicited}}.

A `Digest` field MAY contain multiple representation-data-digest values.
For example, a server may provide representation-data-digest values using different algorithms,
allowing it to support a population of clients with different evolving capabilities;
this is particularly useful in support of transitioning away
from weaker algorithms should the need arise (see {{algorithm-agility}}).

~~~ http-message
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=,
        id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
~~~

A recipient MAY ignore any or all of the representation-data-digests in a Digest
field. This allows the recipient to choose which digest-algorithm(s) to use for
validation instead of verifying every received representation-data-digest.

A sender MAY send a representation-data-digest using a digest-algorithm without
knowing whether the recipient supports the digest-algorithm, or even knowing
that the recipient will ignore it.

`Digest` can be sent in a trailer section.
In this case,
`Digest` MAY be merged in to the header section (See Section 6.5.1 of {{SEMANTICS}}).

When an incremental digest-algorithm
is used, the sender and the receiver can dynamically compute the digest value
while streaming the content.

# The Want-Digest Field {#want-digest}

The `Want-Digest` field indicates the sender's desire to receive a representation
digest on messages associated with the request URI and representation metadata.
It can be used in both requests and responses.

~~~
   Want-Digest = 1#want-digest-value
   want-digest-value = digest-algorithm [ ";" "q" "=" qvalue]
   qvalue = ( "0"  [ "."  0*1DIGIT ] ) /
            ( "1"  [ "."  0*1( "0" ) ] )
~~~

If a digest-algorithm is not accompanied by a "qvalue" (see Section 12.4.2 of{{SEMANTICS}}),
it is treated as if its associated "qvalue" were 1.0.

The sender is willing to accept a digest-algorithm if and only if it is listed
in a `Want-Digest` field of a message, and its "qvalue" is non-zero.

If multiple acceptable digest-algorithm values are given, the sender's preferred
digest-algorithm is the one (or ones) with the highest "qvalue".

Two examples of its use are:

~~~ http-message
Want-Digest: sha-256
Want-Digest: sha-512;q=0.3, sha-256;q=1, unixsum;q=0
~~~

# Digest Algorithm Values {#algorithms}

Digest-algorithm values are used to indicate a specific digest computation.

~~~
   digest-algorithm = token
~~~

All digest-algorithm token values are case-insensitive
but lower case is preferred;
digest-algorithm token values MUST be compared in a case-insensitive fashion.

The Internet Assigned Numbers Authority (IANA) maintains a registry for
digest-algorithm values.
The registry is initialized with the tokens listed below.

Deprecated digest algorithms MUST NOT be used:

- "md5", see [CMU-836068] and {{?NO-MD5=RFC6151}};
- "sha", see [IACR-2020-014] and {{?NO-SHA1=RFC6194}}.

See the references above for further information.


  {: vspace="0"}
  sha-256
  : * Description: The SHA-256 algorithm [RFC6234].  The output of
      this algorithm is encoded using the base64 encoding [RFC4648].
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  sha-512
  : * Description: The SHA-512 algorithm [RFC6234].  The output of
      this algorithm is encoded using the base64 encoding [RFC4648].
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  md5
  : * Description: The MD5 algorithm, as specified in [RFC1321].
      The output of this algorithm is encoded using the
      base64 encoding  [RFC4648].
      This digest-algorithm is now vulnerable
      to collision attacks. See {{NO-MD5}} and [CMU-836068].
    * Reference: [RFC1321], [RFC4648], this document.
    * Status: deprecated

  sha
  : * Description:  The SHA-1 algorithm [RFC3174].  The output of this
      algorithm is encoded using the base64 encoding  [RFC4648].
      This digest-algorithm is now vulnerable
      to collision attacks. See {{NO-SHA1}} and [IACR-2020-014].
    * Reference: [RFC3174], [RFC6234], [RFC4648], this document.
    * Status: deprecated

  unixsum
  : * Description: The algorithm computed by the UNIX "sum" command,
      as defined by the Single UNIX Specification,
      Version 2 [UNIX].  The output of this algorithm is an
      ASCII decimal-digit string representing the 16-bit
      checksum, which is the first word of the output of
      the UNIX "sum" command.
    * Reference: [UNIX], this document.
    * Status: standard

  unixcksum
  : * Description: The algorithm computed by the UNIX "cksum" command,
      as defined by the Single UNIX Specification,
      Version 2 [UNIX].  The output of this algorithm is an
      ASCII digit string representing the 32-bit CRC,
      which is the first word of the output of the UNIX
      "cksum" command.
    * Reference: [UNIX], this document.
    * Status: standard

To allow sender and recipient to provide a checksum which is independent from
`Content-Encoding`, the following additional digest-algorithms are defined:

  {: vspace="0"}
  id-sha-512
  : * Description: The sha-512 digest of the representation-data of the resource when no
    content coding is applied
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  id-sha-256
  : * Description: The sha-256 digest of the representation-data of the resource when no
      content coding is applied
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

If other digest-algorithm values are defined, the associated encoding MUST
either be represented as a quoted string or MUST NOT include ";" or "," in the
character sets used for the encoding.


# Use of Digest when acting on resources {#acting-on-resources}

POST and PATCH requests can appear to convey partial representations but are
semantically acting on resources. The enclosed representation, including its
metadata, refers to that action.

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

In PATCH requests, the representation digest MUST be computed on the patch document
because the representation metadata refers to the patch document and not
to the target resource (see Section 2 of {{?PATCH=RFC5789}}).

In PATCH responses, the representation digest MUST be computed on the selected
representation of the patched resource.

`Digest` usage with PATCH is thus very similar to POST, but with the
resource's own semantic partly implied by the method and by the patch document.

# Relationship to Subresource Integrity (SRI) {#sri}

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

A user agent supporting both mechanisms:
 - can legitimately ignore `Digest` when using SRI, because
   {{digest}} specifies that
   "a recipient MAY ignore any or all of the representation-data-digests";
 - enforce both `Digest` and SRI: in this case it can be useful to provide
   enough information to identify whether the mismatch happened at the `Digest`
   or the SRI level.

# Examples of Unsolicited Digest {#examples-unsolicited}

The following examples demonstrate interactions where a server responds with a
`Digest` field even though the client did not solicit one using
`Want-Digest`.

Some examples include JSON objects in the content.
For presentation purposes, objects that fit completely within the line-length limits
are presented on a single line using compact notation with no leading space.
Objects that would exceed line-length limits are presented across multiple lines
(one line per key-value pair) with 2 spaced of leading indentation.

`Digest` is media-type agnostic
and does not provide canonicalization algorithms for specific formats.
Examples of `Digest` are calculated inclusive of any space.

## Server Returns Full Representation Data {#example-full-representation}

Request:

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example

~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

## Server Returns No Representation Data

In this example, a HEAD request is used to retrieve the checksum
of a resource.

The response `Digest` field-value is calculated over the JSON object
`{"hello": "world"}`, which is not shown because there is no payload
data.

Request:

~~~ http-message
HEAD /items/123 HTTP/1.1
Host: foo.example

~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

~~~

## Server Returns Partial Representation Data

In this example, the client makes a range request and the server
responds with partial content. The `Digest` field-value represents
the entire JSON object `{"hello": "world"}`.

Request:

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Range: bytes=1-7

~~~

Response:

~~~ http-message
HTTP/1.1 206 Partial Content
Content-Type: application/json
Content-Range: bytes 1-7/18
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

"hello"
~~~


## Client and Server Provide Full Representation Data

The request contains a `Digest` field-value calculated on the enclosed
representation. It also includes an `Accept-Encoding: br` header field that advertises the
client supports brotli encoding.

The response includes a `Content-Encoding: br` that indicates the selected
representation is brotli encoded. The `Digest` field-value is therefore
different compared to the request.

For presentation purposes, the response body is displayed as a base64-encoded string because it contains
non-printable characters.

Request:

~~~ http-message
PUT /items/123 HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~ http-message
HTTP/1.1 200 Ok
Content-Type: application/json
Content-Location: /items/123
Content-Encoding: br
Content-Length: 22
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~


## Client Provides Full Representation Data, Server Provides No Representation Data

The request `Digest` field-value is calculated on the enclosed payload.

The response `Digest` field-value
depends on the representation metadata header fields, including
`Content-Encoding: br` even when the response does not contain content.


Request:

~~~ http-message
PUT /items/123 HTTP/1.1
Host: foo.example
Content-Type: application/json
Content-Length: 18
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~ http-message
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

~~~ http-message
PUT /items/123 HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept-Encoding: br
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: br
Content-Location: /items/123
Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=,
        id-sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~


## POST Response does not Reference the Request URI {#post-not-request-uri}

The request `Digest` field-value is computed on the enclosed representation (see
{{acting-on-resources}}).

The representation enclosed in the response refers to the resource identified by
`Content-Location` (see {{SEMANTICS}}, Section 6.4.2). `Digest` is thus computed on the enclosed representation.

Request:

~~~ http-message
POST /books HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=

{"title": "New Title"}
~~~


Response:

~~~ http-message
HTTP/1.1 201 Created
Content-Type: application/json
Content-Location: /books/123
Location: /books/123
Digest: id-sha-256=yxOAqEeoj+reqygSIsLpT0LhumrNkIds5uLKtmdLyYE=

{
  "id": "123",
  "title": "New Title"
}
~~~

Note that a `204 No Content` response without content but with the same
`Digest` field-value would have been legitimate too.

## POST Response Describes the Request Status {#post-referencing-action}

The request `Digest` field-value is computed on the enclosed representation (see
{{acting-on-resources}}).

The representation enclosed in the response describes the status of the request,
so `Digest` is computed on that enclosed representation.

Response `Digest` has no explicit relation with the resource referenced by
`Location`.

Request:

~~~ http-message
POST /books HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=
Location: /books/123

{"title": "New Title"}
~~~


Response:

~~~ http-message
HTTP/1.1 201 Created
Content-Type: application/json
Digest: id-sha-256=2LBp5RKZGpsSNf8BPXlXrX4Td4Tf5R5bZ9z7kdi5VvY=
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

The response `Digest` field-value is computed on the complete representation of the patched
resource.

Request:

~~~ http-message
PATCH /books/123 HTTP/1.1
Host: foo.example
Content-Type: application/merge-patch+json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=

{"title": "New Title"}
~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Digest: id-sha-256=yxOAqEeoj+reqygSIsLpT0LhumrNkIds5uLKtmdLyYE=

{
  "id": "123",
  "title": "New Title"
}
~~~

Note that a `204 No Content` response without content but with the same
`Digest` field-value would have been legitimate too.

## Error responses

In error responses, the representation-data does not necessarily refer to the
target resource. Instead, it refers to the representation of the error.

In the following example a client attempts to patch the resource located at
/books/123. However, the resource does not exist and the server generates a 404
response with a body that describes the error in accordance with {{?RFC7807}}.

The response `Digest` field-value is computed on this enclosed representation.

Request:

~~~ http-message
PATCH /books/123 HTTP/1.1
Host: foo.example
Content-Type: application/merge-patch+json
Accept: application/json
Accept-Encoding: identity
Digest: sha-256=bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=

{"title": "New Title"}
~~~

Response:

~~~ http-message
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
Digest: sha-256=KPqhVXAT25LLitV1w0O167unHmVQusu+fpxm65zAsvk=

{
  "title": "Not Found",
  "detail": "Cannot PATCH a non-existent resource",
  "status": 404
}
~~~

## Use with Trailer Fields and Transfer Coding

An origin server sends `Digest` as trailer field, so it can calculate digest-value
while streaming content and thus mitigate resource consumption.
The `Digest` field-value is the same as in {{example-full-representation}} because `Digest` is designed to
be independent from the use of one or more transfer codings (see {{representation-digest}}).

Request:

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example

~~~

Response:

~~~ http-message
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

Some examples include JSON objects in the content.
For presentation purposes, objects that fit completely within the line-length limits
are presented on a single line using compact notation with no leading space.
Objects that would exceed line-length limits are presented across multiple lines
(one line per key-value pair) with 2 spaced of leading indentation.

`Digest` is media-type agnostic
and does not provide canonicalization algorithms for specific formats.
Examples of `Digest` are calculated inclusive of any space.

## Server Selects Client's Least Preferred Algorithm

The client requests a digest, preferring "sha". The server is free to reply with
"sha-256" anyway.

Request:

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Want-Digest: sha-256;q=0.3, sha;q=1

~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~

##  Server Selects Algorithm Unsupported by Client

The client requests a "sha" digest only. The server is currently free to reply
with a Digest containing an unsupported algorithm.

Request:

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Want-Digest: sha;q=1

~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Digest: id-sha-512=WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                   +AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==

{"hello": "world"}
~~~

## Server Does Not Support Client Algorithm and Returns an Error

The client requests a "sha" Digest, the server advises "sha-256" and "sha-512".

Request:

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Want-Digest: sha;q=1

~~~

Response:

~~~ http-message
HTTP/1.1 400 Bad Request
Want-Digest: sha-256, sha-512

~~~


# Security Considerations

## Digest Does Not Protect the Full HTTP Message

This document specifies a data integrity mechanism that protects HTTP
`representation data`, but not HTTP `representation metadata` fields, from
certain kinds of accidental corruption.

`Digest` is not intended to be a general protection against malicious tampering with
HTTP messages. This can be achieved by combining it with other approaches such
as transport-layer security or digital signatures.

## Broken Cryptographic Algorithms {#broken-algorithms}

Cryptographic algorithms are intended to provide a proof of integrity suited
towards cryptographic constructions such as signatures.

However, these rely on collision-resistance for their security proofs
[CMU-836068]. The "md5" and "sha" digest-algorithms are vulnerable to collisions attacks,
so they MUST NOT be used with `Digest`.

## Other Deprecated Algorithms {#deprecated-algorithms}

The ADLER32 algorithm defined in [RFC1950] has been deprecated by [RFC3309]
because, under certain conditions, it provides weak detection of errors. It is now
NOT RECOMMENDED for use with `Digest`.

## Digest for End-to-End Integrity

`Digest` only covers the `representation data` and not the
`representation metadata`. `Digest` could help protect the `representation data`
from buggy manipulation, undesired "transforming proxies" (see Section 7.7 of {{SEMANTICS}})
or other actions as the data passes across multiple hops or system boundaries.
Even a simple mechanism for end-to-end `representation data` integrity is valuable
because user-agent can validate that resource retrieval succeeded before handing off to a
HTML parser, video player etc. for parsing.

Identity digest-algorithms (e.g. "id-sha-256" and "id-sha-512") are particularly useful
for end-to-end integrity because they allow piecing together a resource from different sources
with different HTTP messaging characteristics. For example, different servers that
apply different content codings.

Note that using `Digest` alone does not provide end-to-end integrity of HTTP messages over
multiple hops, since metadata could be manipulated at any stage. Methods to protect
metadata are discussed in {{usage-in-signatures}}.

## Digest and Content-Location in Responses {#digest-and-content-location}

When a state-changing method returns the `Content-Location` header field, the
enclosed representation refers to the resource identified by its value and
`Digest` is computed accordingly.


## Usage in Signatures {#usage-in-signatures}

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

`Digest` SHOULD always be used over a connection that provides integrity at
the transport layer that protects HTTP fields.

A `Digest` field using NOT RECOMMENDED digest-algorithms SHOULD NOT be used in
signatures.

Using signatures to protect the `Digest` of an empty representation
allows receiving endpoints to detect if an eventual payload has been stripped or added.

Any mangling of `Digest`, including de-duplication of representation-data-digest values
or combining different field values (see Section 5.2 of {{SEMANTICS}})
might affect signature validation.

## Usage in Trailer Fields

Before sending `Digest` in a trailer section, the sender
should consider that intermediaries are explicitly allowed to drop any trailer
(see Section 6.5.2 of {{SEMANTICS}}).

When `Digest` is used in trailer fields, the receiver gets the digest value after the content
and may thus be tempted to process the data before validating the digest value.
It is preferable that data is only be processed after validating the Digest.

Not every digest-algorithm is suitable for use in the trailer section, some may require to pre-process
the whole payload before sending a message (eg. see {{?I-D.thomson-http-mice}}).

## Usage with Encryption

`Digest` may expose details of encrypted payload when the checksum
is computed on the unencrypted data.
For example, the use of the "id-sha-256" digest-algorithm
in conjunction with the encrypted content-coding {{?RFC8188}}.

The representation-data-digest of an encrypted payload can change between different messages
depending on the encryption algorithm used; in those cases its value could not be used to provide
a proof of integrity "at rest" unless the whole (e.g. encoded) content is persisted.

## Algorithm Agility

The security properties of digest-algorithms are not fixed.
Algorithm Agility (see {{?RFC7696}}) is achieved by providing implementations with flexibility
choose digest-algorithms from the IANA Digest Algorithm Values registry in
{{iana-digest-algorithm-registry}}.

To help endpoints understand weaker algorithms from stronger ones,
this document adds to the IANA Digest Algorithm Values registry
a new "Status" field containing the most-recent appraisal of the digest-algorithm;
the allowed values are specified in {{iana-digest-algorithm-status}}.

An endpoint might have a preference for algorithms,
such as preferring "standard" algorithms over "deprecated" ones.
Transition from weak algorithms is supported
by negotiation of digest-algorithm using `Want-Digest` (see {{want-digest}})
or by sending multiple representation-data-digest values from which the receiver chooses.
Endpoints are advised that sending multiple values consumes resources,
which may be wasted if the receiver ignores them (see {{digest}}).

### Duplicate digest-algorithm in field value

An endpoint might receive multiple representation-data-digest values (see {{digest}}) that use the same digest-algorithm with different or identical digest-values. For example:

~~~ example
Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=,
        sha-256=47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=
~~~

A receiver is permitted to ignore any representation-data-digest value,
so validation of duplicates is left as an implementation decision.
Endpoints might select all, some or none of the values for checksum comparison and,
based on the intersection of those results, conditionally pass or fail digest validation.

## Resource exhaustion

`Digest` validation consumes computational resources.
In order to avoid resource exhaustion, implementations can restrict
validation of the algorithm types, number of validations, or the size of content.

# IANA Considerations

## Establish the HTTP Digest Algorithm Values Registry {#iana-digest-algorithm-registry}

This memo sets this specification to be the establishing document for the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml) registry.

## The "status" Field in the HTTP Digest Algorithm Values Registry {#iana-digest-algorithm-status}

This memo adds the field "Status" to the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry. The allowed values for the "Status" fields are described below.

  {: vspace="0"}
   Status
   :  * "standard" for standardized algorithms without known problems;
      * "experimental", "obsoleted" or some other appropriate value - e.g. according to the type
      and status of the primary document in which the algorithm is defined;
      * "deprecated" when the algorithm is insecure or otherwise undesirable.

## Deprecate "MD5" Digest Algorithm {#iana-md5}

This memo updates the "MD5" digest-algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: md5
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Update "UNIXsum" Digest Algorithm {#iana-unixsum}

This memo updates the "UNIXsum" digest-algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: As specified in {{algorithms}}.
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Update "UNIXcksum" Digest Algorithm {#iana-unixcksum}

This memo updates the "UNIXcksum" digest-algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: As specified in {{algorithms}}.
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Update "CRC32c" Digest Algorithm {#iana-crc32c}

This memo updates the "CRC32c" digest-algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: crc32c
* Description: The CRC32c algorithm is a 32-bit cyclic redundancy check. It
  achieves a better hamming distance (for better error-detection performance)
  than many other 32-bit CRC functions. Other places it is used include iSCSI
  and SCTP. The 32-bit output is encoded in hexadecimal (using between 1 and 8
  ASCII characters from 0-9, A-F, and a-f; leading 0's are allowed). For
  example, crc32c=0a72a4df and crc32c=A72A4DF are both valid checksums for the
  3-byte message "dog".
* Reference: {{!RFC4960}} appendix B, this document.
* Status: standard.

## Deprecate "SHA" Digest Algorithm {#iana-sha}

This memo updates the "SHA" digest-algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: sha
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Obsolete "ADLER32" Digest Algorithm {#iana-adler-32}

This memo updates the "ADLER32" digest-algorithm in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: adler32
* Description: The ADLER32 algorithm is a checksum specified in [RFC1950] "ZLIB
  Compressed Data Format". The 32-bit output is encoded in hexadecimal (using
  between 1 and 8 ASCII characters from 0-9, A-F, and a-f; leading 0's are
  allowed). For example, adler32=03da0195 and adler32=3DA0195 are both valid
  checksums for the 4-byte message "Wiki". This algorithm is obsoleted and
  SHOULD NOT be used.
* Status: obsoleted

## Obsolete "contentMD5" token in Digest Algorithm {#iana-contentMD5}

This memo adds the "contentMD5" token in the [HTTP Digest Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: contentMD5
* Description: Section 5 of [RFC3230] defined the "contentMD5" token to be used only in Want-Digest.
  This token is obsoleted and MUST NOT be used.
* Reference: {{iana-contentMD5}} of this document, Section 5 of [RFC3230].
* Status: obsoleted


## The "id-sha-256" Digest Algorithm {#iana-id-sha-256}

This memo registers the "id-sha-256" digest-algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: id-sha-256
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## The "id-sha-512" Digest Algorithm {#iana-id-sha-512}

This memo registers the "id-sha-512" digest-algorithm in the [HTTP Digest
Algorithm
Values](https://www.iana.org/assignments/http-dig-alg/http-dig-alg.xhtml)
registry:

* Digest Algorithm: id-sha-512
* Description: As specified in {{algorithms}}.
* Status: As specified in {{algorithms}}.

## Changes Compared to RFC3230
￼
The `contentMD5` digest-algorithm token defined in Section 5 of [RFC3230] is removed from
the HTTP Digest Algorithm Values Registry.

## Changes Compared to RFC5843

The digest-algorithm values for "MD5", "SHA", "SHA-256", "SHA-512", "UNIXcksum", "UNIXsum",
"ADLER32" and "CRC32c" have been updated to lowercase.

The status of "MD5" has been updated to "deprecated", and its description states
that this algorithm MUST NOT be used.

The status of "SHA" has been updated to "deprecated", and its description states
that this algorithm MUST NOT be used.

The status for "CRC2c", "UNIXsum" and "UNIXcksum" has been updated to "standard".

The "id-sha-256" and "id-sha-512" algorithms have been added to the registry.

## Want-Digest Field Registration

This section registers the `Want-Digest` field in the "Hypertext Transfer
Protocol (HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Want-Digest`

Status:  permanent

Specification document(s):  {{want-digest}} of this document

## Digest Field Registration

This section registers the `Digest` field in the "Hypertext Transfer Protocol
(HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Digest`

Status:  permanent

Specification document(s):  {{digest}} of this document

--- back

# Resource Representation and Representation-Data {#resource-representation}

The following examples show how representation metadata, payload transformations
and method impacts on the message and content. When the content
contains non-printable characters (eg. when it is compressed) it is shown as
base64-encoded string.

A request with a JSON object without any content coding.

Request:

~~~ http-message
PUT /entries/1234 HTTP/1.1
Host: foo.example
Content-Type: application/json

{"hello": "world"}
~~~

Here is a gzip-compressed JSON object
using a content coding.

Request:

~~~ http-message
PUT /entries/1234 HTTP/1.1
Host: foo.example
Content-Type: application/json
Content-Encoding: gzip

H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=
~~~

Now the same content conveys a malformed JSON object.

Request:

~~~ http-message
PUT /entries/1234 HTTP/1.1
Host: foo.example
Content-Type: application/json

H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=
~~~

A Range-Request alters the content, conveying a partial representation.

Request:

~~~ http-message
GET /entries/1234 HTTP/1.1
Host: foo.example
Range: bytes=1-7

~~~

Response:

~~~ http-message
HTTP/1.1 206 Partial Content
Content-Encoding: gzip
Content-Type: application/json
Content-Range: bytes 1-7/18

iwgAla3RXA==
~~~


Now the method too alters the content.

Request:

~~~ http-message
HEAD /entries/1234 HTTP/1.1
Host: foo.example
Accept: application/json
Accept-Encoding: gzip

~~~

Response:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip

~~~

Finally the semantics of an HTTP response might decouple the effective request URI
from the enclosed representation. In the example response below, the
`Content-Location` header field indicates that the enclosed representation
refers to the resource available at `/authors/123`.

Request:

~~~ http-message
POST /authors/ HTTP/1.1
Host: foo.example
Accept: application/json
Content-Type: application/json

{"author": "Camilleri"}
~~~

Response:

~~~ http-message
HTTP/1.1 201 Created
Content-Type: application/json
Content-Location: /authors/123
Location: /authors/123

{"id": "123", "author": "Camilleri"}
~~~

# Changes from RFC3230

## Deprecate Negotiation of Content-MD5 {#deprecate-contentMD5}

This RFC deprecates the negotiation of `Content-MD5` as it has been obsoleted by
[RFC7231].

## Obsolete Digest Field Parameters {#obsolete-parameters}

Section 4.1.1 and 4.2 of [RFC3230] defined field parameters. This document
obsoletes the usage of parameters with `Digest` because this feature has not
been widely deployed and complicates field-value processing.

[RFC3230] intended field parameters to provide a common way to attach additional
information to a representation-data-digest. However, if parameters are used as
an input to validate the checksum, an attacker could alter them to steer the
validation behavior.

A digest-algorithm can still be parameterized by defining its own way to encode parameters into the
representation-data-digest, in such a way as to mitigate security risks related to its computation.

# Acknowledgements
{:numbered="false"}
The vast majority of this document is inherited from [RFC3230], so thanks
to J. Mogul and A. Van Hoff for their great work.
The original idea of refreshing this document arose from an interesting
discussion with M. Nottingham, J. Yasskin and M. Thomson when reviewing
the MICE content coding.

# FAQ
{:numbered="false"}

_RFC Editor: Please remove this section before publication._

1. Why remove all references to content-md5?

   Those were unnecessary to understanding and using this specification.

2. Why remove references to instance manipulation?

   Those were unnecessary for correctly using and applying the specification. An example
   with Range Request is more than enough. This document uses the term "partial
   representation" which should group all those cases.

3. How to use `Digest` with `PATCH` method?

   See {{acting-on-resources}}.

4. Why remove references to delta-encoding?

   Unnecessary for a correct implementation of this specification. The revised specification can
   be nicely adapted to "delta encoding", but all the references here to delta
   encoding don't add anything to this RFC. Another job would be to refresh
   delta encoding.

5. Why remove references to Digest Authentication?

   This specification seems to me completely unrelated to Digest Authentication but for
   the word "Digest".

6. What changes in `Want-Digest`?

   The contentMD5 token defined in Section 5 of [RFC3230] is deprecated by {{deprecate-contentMD5}}.

   To clarify that `Digest` and `Want-Digest` can be used in both requests and responses
   - [RFC3230] carefully uses `sender` and `receiver` in their definition -
   we added examples on using `Want-Digest` in responses to advertise the supported
   digest-algorithms and the inability to accept requests with unsupported
   digest-algorithms.

7. Does this specification change supported algorithms?

   Yes. This RFC updates [RFC5843] which is still delegated for all algorithms
   updates, and adds two more algorithms: "id-sha-256" and "id-sha-512" which allows
   to send a checksum of a resource representation with no content codings
   applied.
   To simplify a future transition to Structured Fields {{?I-D.ietf-httpbis-header-structure}}
   we suggest to use lowercase for digest-algorithms.

8. What about mid-stream trailer fields?

   While
   [mid-stream trailer fields](https://github.com/httpwg/http-core/issues/313#issuecomment-584389706)
   are interesting, since this specification is a rewrite of [RFC3230] we do not
   think we should face that. As a first thought, nothing in this document
   precludes future work that would find a use for mid-stream trailers, for
   example an incremental digest-algorithm. A document defining such a
   digest-algorithm is best positioned to describe how it is used.


# Code Samples
{:numbered="false"}

_RFC Editor: Please remove this section before publication._

How can I generate and validate the `Digest` values shown in the examples
throughout this document?

The following python3 code can be used to generate digests for JSON objects
using SHA algorithms for a range of encodings. Note that these are formatted as
base64. This function could be adapted to other algorithms and should take into
account their specific formatting rules.

~~~
import base64, json, hashlib, brotli, logging
log = logging.getLogger()

def encode_item(item, encoding=lambda x: x):
    indent = 2 if isinstance(item, dict) and len(item) > 1 else None
    json_bytes = json.dumps(item, indent=indent).encode()
    return encoding(json_bytes)


def digest_bytes(bytes_, algorithm=hashlib.sha256):
    checksum_bytes = algorithm(bytes_).digest()
    log.warning("Log bytes: \n[%r]", bytes_)
    return base64.encodebytes(checksum_bytes).strip()


def digest(item, encoding=lambda x: x, algorithm=hashlib.sha256):
    content_encoded = encode_item(item, encoding)
    return digest_bytes(content_encoded, algorithm)


item = {"hello": "world"}

print("Encoding | digest-algorithm | digest-value")
print("Identity | sha256 |", digest(item))
# Encoding | digest-algorithm | digest-value
# Identity | sha256 | X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

print("Encoding | digest-algorithm | digest-value")
print("Brotli | sha256 |", digest(item, encoding=brotli.compress))
# Encoding | digest-algorithm | digest-value
# Brotli | sha256 | 4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

print("Encoding | digest-algorithm | digest-value")
print("Identity | sha512 |", digest(item, algorithm=hashlib.sha512))
# Encoding | digest-algorithm | digest-value
# Identity | sha512 | b'WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm'
#                      '+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew=='
~~~

# Changes
{:numbered="false"}

_RFC Editor: Please remove this section before publication._

## Since draft-ietf-httpbis-digest-headers-04
{:numbered="false"}

* Improve SRI section #1354
* About duplicate digest-algorithms #1221
* Improve security considerations #852
* md5 and sha deprecation references #1392
* Obsolete 3230 #1395
* Editorial #1362

## Since draft-ietf-httpbis-digest-headers-03
{:numbered="false"}

* Reference semantics-12
* Detail encryption quirks
* Details on Algorithm agility #1250
* Obsolete parameters #850

## Since draft-ietf-httpbis-digest-headers-02
{:numbered="false"}

* Deprecate SHA-1 #1154
* Avoid id-* with encrypted content
* Digest is independent from MESSAGING and HTTP/1.1 is not normative #1215
* Identity is not a valid field value for content-encoding #1223
* Mention trailers #1157
* Reference httpbis-semantics #1156
* Add contentMD5 as an obsoleted digest-algorithm #1249
* Use lowercase digest-algorithms names in the doc and in the digest-algorithm IANA table.

## Since draft-ietf-httpbis-digest-headers-01
{:numbered="false"}

* Digest of error responses is computed on the error representation-data #1004
* Effect of HTTP semantics on payload and message body moved to appendix #1122
* Editorial refactoring, moving headers sections up. #1109-#1112, #1116,
  #1117, #1122-#1124

## Since draft-ietf-httpbis-digest-headers-00
{:numbered="false"}

* Align title with document name
* Add id-sha-* algorithm examples #880
* Reference [RFC6234] and [RFC3174] instead of FIPS-1
* Deprecate MD5
* Obsolete ADLER-32 but don't forbid it #828
* Update CRC32C value in IANA table #828
* Use when acting on resources (POST, PATCH) #853
* Added Relationship with SRI, draft Use Cases #868, #971
* Warn about the implications of `Content-Location`
