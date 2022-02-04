---
title: Structured Digest Fields
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

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/digest-headers
github-issue-label: digest-headers

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
  RFC4648:
  RFC5234:
  RFC6234:
  RFC7405:
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
  SEMANTICS: I-D.ietf-httpbis-semantics

informative:
  RFC2818:
  HTTP11: I-D.ietf-httpbis-messaging
  PATCH: RFC5789

--- abstract

This document defines HTTP fields that support integrity checksums. The
Representation-Digest field can be used for the integrity of HTTP
representations. The Content-Digest field can be used for the integrity of
HTTP message content. Want-Representation-Digest and Want-Content-Digest can be
used to indicate a sender's interest and preferences for receiving the respective
integrity fields.

This document obsoletes RFC 3230 and the Digest and Want-Digest HTTP
fields.


--- middle

# Introduction

HTTP does not define the means to protect the data integrity of representations
or content. When HTTP messages are transferred between endpoints, lower layer
features or properties such as TCP checksums or TLS records [RFC2818] can provide
some integrity protection. However, transport-oriented integrity provides a
limited utility because it is opaque to the application layer and only covers
the extent of a single connection. HTTP messages often travel over a chain of
separate connections, in between connections there is a possibility for
unintended or malicious data corruption. An HTTP integrity mechanism can provide
the means for endpoints, or applications using HTTP, to detect data corruption
and make a choice about how to act on it. An example use case is to aid
fault detection and diagnosis across system boundaries.

This document defines two digest integrity mechanisms for HTTP.
First, content integrity, which acts on conveyed content ({{Section 6.4 of
SEMANTICS}}).
Second, representation data integrity, which acts on representation data ({{Section 3.2
of SEMANTICS}}). This supports more advanced use cases such as validating the
integrity of a resource that was reconstructed from parts retrieved using
multiple requests or connections.

This document obsoletes RFC 3230 and therefore the Digest and Want-Digest HTTP
fields; see {{obsolete-3230}}.


## Document Structure

This document is structured as follows:

- {{representation-digest}} defines the Representation-Digest request and response header and trailer field,
- {{content-digest}} defines the Content-Digest request and response header and trailer field,
- {{want-fields}} defines the Want-Representation-Digest and Want-Content-Digest request and response header and
  trailer field,
- {{algorithms}} describes algorithms and their relation to the fields defined in this document,
- {{state-changing-requests}} details computing representation digests,
- {{examples-unsolicited}} and {{examples-solicited}} provide examples of using
  Representation-Digest and Want-Representation-Digest.

## Concept Overview

The HTTP fields defined in this document can be used for HTTP integrity. Senders
choose a hashing algorithm and calculate a checksum from an input related to the
HTTP message, the algorithm identifier and checksum are transmitted in an HTTP
field. Receivers can validate the checksum for integrity purposes. Hashing
algorithms are registered in the HTTP Digest Algorithm Values Registry (see
{{algorithms}}).

Selecting the data on which checksums are calculated depends on the use case of
HTTP messages. This document provides different headers for HTTP representation
data and HTTP content.

This document defines the `Representation-Digest` request and response header
and trailer field ({{representation-digest}}) that contains a checksum value
computed by applying a hashing algorithm to `selected representation data`
({{Section 3.2 of SEMANTICS}}). Basing `Representation-Digest` on the selected
representation makes it straightforward to apply it to use-cases where the
transferred data requires some sort of manipulation to be considered a
representation or conveys a partial representation of a resource, such as Range
Requests (see {{Section 14.2 of SEMANTICS}}).

There are use-cases where a simple checksum of the HTTP content bytes is
required. The `Content-Digest` request and response header and trailer field is
defined to support checksums of content ({{Section 3.2 of SEMANTICS}}); see
{{content-digest}}.

`Representation-Digest` and `Content-Digest` support hashing algorithm agility.
The `Want-Representation-Digest` and `Want-Content-Digest` fields allows
endpoints to express interest in `Representation-Digest` and `Content-Digest`
respectively, and preference of algorithms in either.

`Representation-Digest` and `Content-Digest` are collectively termed
integrity fields. `Want-Representation-Digest` and `Want-Content-Digest`are
collectively termed integrity preference fields.

Integrity fields are tied to the `Content-Encoding`
and `Content-Type` header fields. Therefore, a given resource may have multiple
different checksum values when transferred with HTTP.

Integrity fields do not provide integrity for
HTTP messages or fields. However, they can be combined with other mechanisms that
protect metadata, such as digital signatures, in order to protect
the phases of an HTTP exchange in whole or in part.

This specification does not define means for authentication, authorization or privacy.

## Obsoleting RFC 3230 {#obsolete-3230}

[RFC3230] defined the `Digest` and `Want-Digest` HTTP fields for HTTP integrity.
It also coined the term "instance" and "instance manipulation" in order to
explain concepts that are now more universally defined, and implemented, as HTTP
semantics such as `selected representation data` ({{Section 3.2 of SEMANTICS}}).

Experience has shown that implementations of [RFC3230] have interpreted the
meaning of "instance" inconsistently, leading to interoperability issues. The
most common mistake being the calculation of the checksum using (what we now call)
message content, rather than using (what we now call) representation data as was
originally intended. Interestingly, time has also shown that a checksum of
message content can be beneficial for some use cases. So it is difficult to
detect if non-conformance to [RFC3230] is intentional or unintentional.

In order to address potential inconsistencies and ambiguity across
implementations of `Digest` and `Want-Digest`, this document obsoletes
[RFC3230]. The Integrity fields ({{representation-digest}} and
{{content-digest}}) and integrity preference fields ({{want-fields}})
defined in this document are better aligned with current HTTP semantics and
have names that more clearly articulate the intended usages.


## Notational Conventions
{::boilerplate bcp14-tagged}

This document uses the Augmented BNF defined in [RFC5234] and updated by
[RFC7405].

The terms Dictionary, List, sf-dictionary, sf-integer and sf-binary are imported from
{{!STRUCTURED-FIELDS=RFC8941}}.

The definitions "representation", "selected representation", "representation
data", "representation metadata", and "content" in this document are to be
interpreted as described in {{SEMANTICS}}.

Hashing algorithm names respect the casing used in their definition document (e.g. SHA-1, CRC32c)
whereas hashing algorithm keys are quoted (e.g. "sha", "crc32c").

The term "checksum" describes the output of the application of an algorithm
to a sequence of bytes,
whereas digest is only used in relation to the value of the fields.

Integrity fields: collective term for `Representation-Digest` and `Content-Digest`

Integrity preference fields: collective term for `Want-Representation-Digest` and `Want-Content-Digest`

# The Representation-Digest Field {#representation-digest}

The `Representation-Digest` HTTP field can be used in requests and responses to
communicate checksums that are calculated using a hashing algorithm applied to
the entire selected `representation data` (see {{Section 8.1 of SEMANTICS}}).

Representations take into account the effect of the HTTP semantics on
messages. For example, the content can be affected by Range Requests or methods
such as HEAD, while the way the content is transferred "on the wire" is
dependent on other transformations (e.g. transfer codings for HTTP/1.1 - see
{{Section 6.1 of HTTP11}}). To help illustrate HTTP representation concepts,
several examples are provided in {{resource-representation}}.

When a message has no representation data it is still possible to assert that no
representation data was sent computing the representation digest on an empty
string (see {{usage-in-signatures}}).

`Representation-Digest` is a Structured Fields Dictionary (see {{Section 3.2 of
STRUCTURED-FIELDS}}):

~~~ abnf
Representation-Digest   = sf-dictionary
~~~

`Representation-Digest` member-keys convey the hashing algorithm (see
{{algorithms}}) used to compute the checksum. Member-values are the the output
of the checksum calculation. Member-values MUST be of type sf-binary.

For example:

~~~ http-message
Representation-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==:
~~~

Since `Representation-Digest` is a Dictionary, it can contain multiple
members. This could be used, for example, to attach multiple checksums
calculated using different hashing algorithms in order to support a population
of endpoints with different or evolving capabilities. Such an approach could
support transitions away from weaker algorithms (see {{algorithm-agility}}).

~~~ http-message
Representation-Digest: sha-256=:4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=:,
        sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==:
~~~

A recipient MAY ignore any or all of members of `Representation-Digest`.
This allows the recipient to choose which hashing algorithm(s) to use for
validation instead of verifying every received representation-data-digest.

A sender MAY send a `Representation-Digest` member without knowing whether the
recipient supports a given hashing algorithm, or even knowing that the recipient
will ignore it.

`Representation-Digest` can be sent in a trailer section.
In this case,
`Representation-Digest` MAY be merged into the header section; see {{Section 6.5.1 of SEMANTICS}}.

# The Content-Digest Field {#content-digest}

The `Content-Digest` HTTP field can be used in requests and responses to
communicate checksums that are calculated using a hashing algorithm applied to
the actual message content (see {{Section 6.4 of SEMANTICS}}). It is a
Structured Fields Dictionary (see {{Section 3.2 of STRUCTURED-FIELDS}}):

~~~ abnf
Content-Digest   = sf-dictionary
~~~

`Content-Digest` member-keys convey the hashing algorithm (see {{algorithms}})
used to compute the checksum. Member-values are the the output of the checksum
calculation. Member-values MUST be of type sf-binary.

For example:

~~~ http-message
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                        AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==:
~~~

Since `Content-Digest` is a Dictionary, it can contain multiple
members. This could be used, for example, to attach multiple checksums
calculated using different hashing algorithms in order to support a population
of endpoints with different or evolving capabilities. Such an approach could
support transitions away from weaker algorithms (see {{algorithm-agility}}).

~~~ http-message
Content-Digest: sha-256=:4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=:,
                sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                        AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==:
~~~

A recipient MAY ignore any or all of members of `Content-Digest`. This allows
the recipient to choose which hashing algorithm(s) to use for validation instead
of verifying every received representation-data-digest.

A sender MAY send a representation-data-digest using a hashing algorithm without
knowing whether the recipient supports the hashing algorithm, or even knowing
that the recipient will ignore it.

`Content-Digest` can be sent in a trailer section.
In this case,
`Content-Digest` MAY be merged into the header section; see {{Section 6.5.1 of SEMANTICS}}.

# Integrity preference fields  {#want-fields}

Senders can indicate their interest in integrity fields and hashing algorithm
preferences using the
`Want-Representation-Digest` or `Want-Content-Digest` fields. These can be used in both
requests and responses.

`Want-Representation-Digest` indicates the sender's desire to receive a representation digest
on messages associated with the request URI and representation metadata, using
the `Representation-Digest` field.

`Want-Content-Digest` indicates the sender's desire to receive a content digest
on messages associated with the request URI and representation metadata, using
the `Content-Digest` field.

`Want-Representation-Digest` and `Want-Content-Digest` are Structured Fields
List (see {{Section 3.2 of STRUCTURED-FIELDS}}):

~~~ abnf
   Want-Representation-Digest = sf-dictionary
   Want-Content-Digest = sf-dictionary
~~~

Dictionary members convey hashing algorithm preferences (see {{algorithms}}).
Member-keys convey the hashing algorithm (see {{algorithms}}), member-values convey
an ascending relative weighted preference between 0 and 10. Member-values MUST
be of type sf-integer, in the range 0 to 10.

Examples:

~~~ http-message
Want-Representation-Digest: sha-256=1
Want-Representation-Digest: sha-512=3, sha-256=10, unixsum=0
Want-Content-Digest: sha-256=1
Want-Content-Digest: sha-512=3, sha-256=10, unixsum=0
~~~


# Structured Digest Algorithm Registry {#algorithms}

The "HTTP Structured Digest Algorithm Registry", maintained by IANA at
<https://www.iana.org/assignments/http-dig-alg/> registers algorithms for use
with a range of HTTP fields.

Registrations MUST include the following fields:

 - Algorithm: a friendly name of the algorithm
 - Description: a short description of the algorithm
 - Algorithm Key: the Structured Fields key value used in
   `Representation-Digest`, `Content-Digest`, `Want-Representation-Digest` or
    `Want-Content-Digest` field Dictionary member keys
 - Status: the status of the algorithm.
     Use "standard" for standardized algorithms without known problems;
     "experimental" or some other appropriate value
     - e.g. according to the type and status of the primary document
     in which the algorithm is defined;
     "insecure" when the algorithm is insecure;
     "reserved" when the algorithm references a reserved token value
 - Reference: a set of pointers to the primary documents defining the algorithm
   and key

Insecure digest algorithms MAY be used to preserve integrity against corruption, but MUST
NOT be used in a potentially adversarial setting; for example, when signing digest fields' values for
authenticity.

The registry is initialized with the algorithms listed below.

  {: vspace="0"}
  SHA-512
  : * Algorithm: SHA-512
    * Description: The SHA-512 algorithm [RFC6234].
    * Algorithm Key: sha-512
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  SHA-256
  : * Algorithm: SHA-256
    * Description: The SHA-256 algorithm [RFC6234].
    * Algorithm Key: sha-256
    * Reference: [RFC6234], [RFC4648], this document.
    * Status: standard

  MD5
  : * Algorithm: md5
    * Description: The MD5 algorithm [RFC1321].
      This algorithm is now vulnerable
      to collision attacks. See {{?NO-MD5=RFC6151}} and [CMU-836068].
    * Algorithm Key: md5
    * Reference: [RFC1321], [RFC4648], this document.
    * Status: insecure

  SHA
  : * Algorithm: SHA
    * Description:  The SHA-1 algorithm [RFC3174].
      This algorithm is now vulnerable
      to collision attacks. See {{?NO-SHA1=RFC6194}} and [IACR-2020-014].
    * Algorithm Key: sha
    * Reference: [RFC3174], [RFC6234], [RFC4648], this document.
    * Status: insecure

  UNIXSUM
  : * Algorithm: UNIXSUM
    * Description: The algorithm used by the UNIX "sum" command [UNIX].
    * Algorithm Key: unixsum
    * Reference: [UNIX], this document.
    * Status: insecure

  UNIXCKSUM
  : * Algorithm: UNIXCKSUM
    * Description: The algorithm used by the UNIX "cksum" command [UNIX].
    * Algorithm Key: unixcksum
    * Reference: [UNIX], this document.
    * Status: insecure

  ADLER
  : * Algorithm: ADLER32
    * Description: The ADLER32 algorithm [RFC1950].
    * Algorithm Key: adler32
    * Reference: [RFC1950], this document.
    * Status: insecure

  CRC32C
  : * Algorithm: CRC32C
    * Description: The CRC32c algorithm {{!RFC4960}}.
    * Algorithm Key: crc32c
    * Reference: {{!RFC4960}} appendix B, this document.
    * Status: insecure

# Using Representation-Digest in State-Changing Requests {#state-changing-requests}

When the representation enclosed in a state-changing request
does not describe the target resource,
the representation digest MUST be computed on the
representation-data.
This is the only possible choice because representation digest requires complete
representation metadata (see {{representation-digest}}).

In responses,

- if the representation describes the status of the request,
  `Representation-Digest` MUST be computed on the enclosed representation
   (see {{post-referencing-status}} );

- if there is a referenced resource
  `Representation-Digest` MUST be computed on the selected representation of the referenced resource
   even if that is different from the target resource.
   That might or might not result in computing `Representation-Digest` on the enclosed representation.

The latter case is done according to the HTTP semantics of the given
method, for example using the `Content-Location` header field (see {{Section 8.7 of
SEMANTICS}}).
In contrast, the `Location` header field does not affect `Representation-Digest` because
it is not representation metadata.

For example, in PATCH requests, the representation digest
will be computed on the patch document
because the representation metadata refers to the patch document and not
to the target resource (see {{Section 2 of PATCH}}).
In responses, instead, the representation digest will be computed on the selected
representation of the patched resource.

## Representation-Digest and Content-Location in Responses {#digest-and-content-location}

When a state-changing method returns the `Content-Location` header field, the
enclosed representation refers to the resource identified by its value and
`Representation-Digest` is computed accordingly. An example is given in {{post-not-request-uri}}.


# Security Considerations

## HTTP Messages are not protected in full

This document specifies a data integrity mechanism that protects HTTP
`representation data` or content, but not HTTP header and trailer fields, from
certain kinds of corruption.

Digest fields are not intended to be a general protection against malicious tampering with
HTTP messages. This can be achieved by combining it with other approaches such
as transport-layer security or digital signatures.

## End-to-End Integrity

Representation-Digest and Content-Digest can help detect `representation data` or content modification due to implementation errors,
undesired "transforming proxies" (see {{Section 7.7 of SEMANTICS}})
or other actions as the data passes across multiple hops or system boundaries.
Even a simple mechanism for end-to-end `representation data` integrity is valuable
because user-agent can validate that resource retrieval succeeded before handing off to a
HTML parser, video player etc. for parsing.

Note that using these mechanisms alone does not provide end-to-end integrity of HTTP messages over
multiple hops, since metadata could be manipulated at any stage. Methods to protect
metadata are discussed in {{usage-in-signatures}}.

## Usage in Signatures {#usage-in-signatures}

Digital signatures are widely used together with checksums to provide the
certain identification of the origin of a message [NIST800-32]. Such signatures
can protect one or more HTTP fields and there are additional considerations when
`Representation-Digest` or `Content-Digest` is included in this set.

Checksums explicitly
depend on the "representation metadata" (e.g. the values of `Content-Type`,
`Content-Encoding` etc). A signature that protects `Representation-Digest` but not other
"representation metadata" can expose the communication to tampering. For
example, an actor could manipulate the `Content-Type` field-value and cause a
digest validation failure at the recipient, preventing the application from
accessing the representation. Such an attack consumes the resources of both
endpoints. See also {{digest-and-content-location}}.

Digest fields SHOULD always be used over a connection that provides integrity at
the transport layer that protects HTTP fields.

A `Representation-Digest` field using NOT RECOMMENDED hashing algorithms SHOULD NOT be used in
signatures.

Using signatures to protect the checksum of an empty representation
allows receiving endpoints to detect if an eventual payload has been stripped or added.

Any mangling of digest fields, including de-duplication of representation-data-digest values
or combining different field values (see {{Section 5.2 of SEMANTICS}})
might affect signature validation.

## Usage in Trailer Fields

Before sending digest fields in a trailer section, the sender
should consider that intermediaries are explicitly allowed to drop any trailer
(see {{Section 6.5.2 of SEMANTICS}}).

When digest fields are used in a trailer section, the field-values are received after the content.
Eager processing of content before the trailer section prevents digest validation, possibly leading to
processing of invalid data.

Not every hashing algorithm is suitable for use in the trailer section, some may require to pre-process
the whole payload before sending a message (e.g. see {{?I-D.thomson-http-mice}}).

## Usage with Encryption

The checksum of an encrypted payload can change between different messages
depending on the encryption algorithm used; in those cases its value could not be used to provide
a proof of integrity "at rest" unless the whole (e.g. encoded) content is persisted.

## Algorithm Agility

The security properties of hashing algorithms are not fixed.
Algorithm Agility (see {{?RFC7696}}) is achieved by providing implementations with flexibility
to choose hashing algorithms from the IANA HTTP Structured Digest Algorithm Values registry in
{{iana-digest-algorithm-registry}}.

To help endpoints distinguish weaker algorithms from stronger ones,
this document adds to the IANA Digest Algorithm Values registry
a new "Status" field containing the most recent appraisal of the hashing algorithm.

An endpoint might have a preference for algorithms,
such as preferring "standard" algorithms over "insecure" ones.
Transition from weak algorithms is supported
by negotiation of hashing algorithm using `Want-Representation-Digest` or `Want-Content-Digest` (see {{want-fields}})
or by sending multiple representation-data-digest values from which the receiver chooses.
Endpoints are advised that sending multiple values consumes resources,
which may be wasted if the receiver ignores them (see {{representation-digest}}).

While algorithm agility allows the migration to stronger algorithms
it does not prevent the use of weaker algorithms.
Integrity fields do not provide any mitigiations for downgrade or substitution
attacks (see Section 1 of {{?RFC6211}}) of the hashing algorithm.
To protect against such attacks, endpoints could restrict their set of supported algorithms
to stronger ones and protect the fields value by using TLS and/or digital signatures.

## Resource exhaustion

Digest fields validation consumes computational resources.
In order to avoid resource exhaustion, implementations can restrict
validation of the algorithm types, number of validations, or the size of content.

# IANA Considerations

## Establish the HTTP Structured Digest Algorithm Values Registry {#iana-digest-algorithm-registry}

This memo sets this specification to be the establishing document for the [HTTP Structured Digest
Algorithm](https://www.iana.org/assignments/http-structured-dig-alg/) registry.

IANA is asked to initialize the registry with the tokens
defined in {{algorithms}}.

This registry uses the Specification
Required policy ({{Section 4.6 of !RFC8126}}).

## Representation-Digest Field Registration

This section registers the `Representation-Digest` field in the "Hypertext Transfer Protocol
(HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Representation-Digest`

Status:  permanent

Specification document(s):  {{representation-digest}} of this document

## Content-Digest Field Registration

This section registers the `Content-Digest` field in the "Hypertext Transfer Protocol
(HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Content-Digest`

Status:  permanent

Specification document(s):  {{content-digest}} of this document

## Want-Representation-Digest Field Registration

This section registers the `Want-Representation-Digest` field in the "Hypertext Transfer
Protocol (HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Want-Representation-Digest`

Status:  permanent

Specification document(s):  {{want-fields}} of this document

## Want-Content-Digest Field Registration

This section registers the `Want-Content-Digest` field in the "Hypertext Transfer
Protocol (HTTP) Field Name Registry" {{SEMANTICS}}.

Field name:  `Want-Content-Digest`

Status:  permanent

Specification document(s):  {{want-fields}} of this document

--- back

# Resource Representation and Representation-Data {#resource-representation}

The following examples show how representation metadata, payload transformations
and method impacts on the message and content. When the content
contains non-printable characters (e.g. when it is compressed) it is shown as
a Base64-encoded string.

~~~ http-message
PUT /entries/1234 HTTP/1.1
Host: foo.example
Content-Type: application/json

{"hello": "world"}
~~~
{: title="Request containing a JSON object without any content coding"}

~~~ http-message
PUT /entries/1234 HTTP/1.1
Host: foo.example
Content-Type: application/json
Content-Encoding: gzip

H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=
~~~
{: title="Request containing a gzip-encoded JSON object"}

Now the same content conveys a malformed JSON object, because the request does
not indicate a content coding.

~~~ http-message
PUT /entries/1234 HTTP/1.1
Host: foo.example
Content-Type: application/json

H4sIAItWyFwC/6tWSlSyUlAypANQqgUAREcqfG0AAAA=
~~~
{: title="Request containing malformed JSON"}

A Range-Request alters the content, conveying a partial representation.

~~~ http-message
GET /entries/1234 HTTP/1.1
Host: foo.example
Range: bytes=1-7

~~~
{: title="Request for partial content"}

~~~ http-message
HTTP/1.1 206 Partial Content
Content-Encoding: gzip
Content-Type: application/json
Content-Range: bytes 1-7/18

iwgAla3RXA==
~~~
{: title="Partial response from a gzip-encoded representation"}

The method can also alter the content.  For example, the response
to a HEAD request does not carry content.

~~~ http-message
HEAD /entries/1234 HTTP/1.1
Host: foo.example
Accept: application/json
Accept-Encoding: gzip

~~~
{: title="HEAD request"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: gzip

~~~
{: title="Response to HEAD request (empty content)"}

Finally, the semantics of an HTTP response might decouple the effective request URI
from the enclosed representation. In the example response below, the
`Content-Location` header field indicates that the enclosed representation
refers to the resource available at `/authors/123`, even though the request is
directed to `/authors/`.

~~~ http-message
POST /authors/ HTTP/1.1
Host: foo.example
Accept: application/json
Content-Type: application/json

{"author": "Camilleri"}
~~~
{: title="POST request"}

~~~ http-message
HTTP/1.1 201 Created
Content-Type: application/json
Content-Location: /authors/123
Location: /authors/123

{"id": "123", "author": "Camilleri"}
~~~
{: title="Response with Content-Location header"}

# Examples of Unsolicited Digest {#examples-unsolicited}

The following examples demonstrate interactions where a server responds with a
`Representation-Digest` or `Content-Digest` fields even though the client did not solicit one using
`Want-Representation-Digest` or `Want-Content-Digest`.

Some examples include JSON objects in the content.
For presentation purposes, objects that fit completely within the line-length limits
are presented on a single line using compact notation with no leading space.
Objects that would exceed line-length limits are presented across multiple lines
(one line per key-value pair) with 2 spaced of leading indentation.

Checksum mechanisms defined in this document are media-type agnostic
and do not provide canonicalization algorithms for specific formats.
Examples are calculated inclusive of any space.
While examples can include both fields,
`Representation-Digest` and `Content-Digest` can be returned independently.

## Server Returns Full Representation Data {#example-full-representation}

In this example, the message content conveys complete representation data,
so `Representation-Digest` and `Content-Digest` have the same value.

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example

~~~
{: title="GET request for an item"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:
Content-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:

{"hello": "world"}
~~~
{: title="Response with Content-Digest"}

## Server Returns No Representation Data

In this example, a HEAD request is used to retrieve the checksum
of a resource.

The response `Representation-Digest` field-value is calculated over the JSON object
`{"hello": "world"}`, which is not shown because there is no payload
data.
`Content-Digest` is computed on empty content.

~~~ http-message
HEAD /items/123 HTTP/1.1
Host: foo.example

~~~
{: title="HEAD request for an item"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:
Content-Digest: sha-256=:47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=:

~~~
{: title="Response with both Content-Digest and Digest; empty content"}

## Server Returns Partial Representation Data

In this example, the client makes a range request and the server responds with
partial content. The `Representation-Digest` field-value represents the entire JSON object
`{"hello": "world"}`, while the `Content-Digest` field-value is computed on the
message content `"hello"`.

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Range: bytes=1-7

~~~
{: title="Request for partial content"}

~~~ http-message
HTTP/1.1 206 Partial Content
Content-Type: application/json
Content-Range: bytes 1-7/18
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:
Content-Digest: sha-256=:Wqdirjg/u3J688ejbUlApbjECpiUUtIwT8lY/z81Tno=:

"hello"
~~~
{: title="Partial response with both Content-Digest and Digest"}


## Client and Server Provide Full Representation Data

The request contains a `Representation-Digest` field-value calculated on the enclosed
representation. It also includes an `Accept-Encoding: br` header field that advertises the
client supports Brotli encoding.

The response includes a `Content-Encoding: br` that indicates the selected
representation is Brotli-encoded. The `Representation-Digest` field-value is therefore
different compared to the request.

For presentation purposes, the response body is displayed as a Base64-encoded string because it contains
non-printable characters.

~~~ http-message
PUT /items/123 HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept-Encoding: br
Representation-Digest: sha-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

{"hello": "world"}
~~~
{: title="PUT Request with Digest"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /items/123
Content-Encoding: br
Content-Length: 22
Representation-Digest: sha-256=:4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=:

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~
{: title="Response with Digest of encoded response"}


## Client Provides Full Representation Data, Server Provides No Representation Data

The request `Representation-Digest` field-value is calculated on the enclosed payload.

The response `Representation-Digest` field-value
depends on the representation metadata header fields, including
`Content-Encoding: br` even when the response does not contain content.


~~~ http-message
PUT /items/123 HTTP/1.1
Host: foo.example
Content-Type: application/json
Content-Length: 18
Accept-Encoding: br
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:

{"hello": "world"}
~~~
{: title="PUT Request with Digest}

~~~ http-message
HTTP/1.1 204 No Content
Content-Type: application/json
Content-Encoding: br
Representation-Digest: sha-256=4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

~~~
{: title="Empty response with Digest"}

## Client and Server Provide Full Representation Data

The response contains two digest values using different algorithms.

As the response body contains non-printable characters, it is displayed as a
base64-encoded string.

~~~ http-message
PUT /items/123 HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept-Encoding: br
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:

{"hello": "world"}
~~~
{: title="PUT Request with Digest"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Content-Encoding: br
Content-Location: /items/123
Representation-Digest: sha-256=:4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=:,
        sha-512=:pxo7aYzcGI88pnDnoSmAnaOEVys0MABhgvHY9+VI+ElE6
                0jBCwnMPyA/s3NF3ZO5oIWA7lf8ukk+\n5KJzm3p5og==:

iwiAeyJoZWxsbyI6ICJ3b3JsZCJ9Aw==
~~~
{: title="Response with Digest of Encoded Content"}

## POST Response does not Reference the Request URI {#post-not-request-uri}

The request `Representation-Digest` field-value is computed on the enclosed representation (see
{{state-changing-requests}}).

The representation enclosed in the response refers to the resource identified by
`Content-Location` (see {{Section 6.4.2 of SEMANTICS}}). `Representation-Digest` is thus computed on the enclosed representation.

~~~ http-message
POST /books HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept: application/json
Accept-Encoding: identity
Representation-Digest: sha-256=:bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=:

{"title": "New Title"}
~~~
{: title="POST Request with Digest"}

~~~ http-message
HTTP/1.1 201 Created
Content-Type: application/json
Content-Location: /books/123
Location: /books/123
Representation-Digest: sha-256=:yxOAqEeoj+reqygSIsLpT0LhumrNkIds5uLKtmdLyYE=:

{
  "id": "123",
  "title": "New Title"
}
~~~
{: title="Response with Digest of Resource"}

Note that a `204 No Content` response without content but with the same
`Representation-Digest` field-value would have been legitimate too.
In that case, `Content-Digest` would have been computed on an empty content.

## POST Response Describes the Request Status {#post-referencing-status}

The request `Representation-Digest` field-value is computed on the enclosed representation (see
{{state-changing-requests}}).

The representation enclosed in the response describes the status of the request,
so `Representation-Digest` is computed on that enclosed representation.

Response `Representation-Digest` has no explicit relation with the resource referenced by
`Location`.

~~~ http-message
POST /books HTTP/1.1
Host: foo.example
Content-Type: application/json
Accept: application/json
Accept-Encoding: identity
Representation-Digest: sha-256=:bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=:

{"title": "New Title"}
~~~
{: title="POST Request with Digest"}

~~~ http-message
HTTP/1.1 201 Created
Content-Type: application/json
Representation-Digest: sha-256=:2LBp5RKZGpsSNf8BPXlXrX4Td4Tf5R5bZ9z7kdi5VvY=:
Location: /books/123

{
  "status": "created",
  "id": "123",
  "ts": 1569327729,
  "instance": "/books/123"
}
~~~
{: title="Response with Digest of Representation"}


## Digest with PATCH

This case is analogous to a POST request where the target resource reflects the
effective request URI.

The PATCH request uses the `application/merge-patch+json` media type defined in
{{?RFC7396}}.

`Representation-Digest` is calculated on the enclosed payload, which corresponds to the patch
document.

The response `Representation-Digest` field-value is computed on the complete representation of the patched
resource.

~~~ http-message
PATCH /books/123 HTTP/1.1
Host: foo.example
Content-Type: application/merge-patch+json
Accept: application/json
Accept-Encoding: identity
Representation-Digest: sha-256=:bWopGGNiZtbVgHsG+I4knzfEJpmmmQHf7RHDXA3o1hQ=:

{"title": "New Title"}
~~~
{: #fig-patch title="PATCH Request with Digest"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Representation-Digest: sha-256=:yxOAqEeoj+reqygSIsLpT0LhumrNkIds5uLKtmdLyYE=:

{
  "id": "123",
  "title": "New Title"
}
~~~
{: title="Response with Digest of Representation"}

Note that a `204 No Content` response without content but with the same
`Representation-Digest` field-value would have been legitimate too.

## Error responses

In error responses, the representation-data does not necessarily refer to the
target resource. Instead, it refers to the representation of the error.

In the following example, a client sends the same request from {{fig-patch}} to
patch the resource located at /books/123. However, the resource does not exist
and the server generates a 404 response with a body that describes the error in
accordance with {{?RFC7807}}.

The response `Representation-Digest` field-value is computed on this enclosed representation.

~~~ http-message
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
Representation-Digest: sha-256=:KPqhVXAT25LLitV1w0O167unHmVQusu+fpxm65zAsvk=:

{
  "title": "Not Found",
  "detail": "Cannot PATCH a non-existent resource",
  "status": 404
}
~~~
{: title="Response with Digest of Error Representation"}

## Use with Trailer Fields and Transfer Coding

An origin server sends `Representation-Digest` as trailer field, so it can calculate digest-value
while streaming content and thus mitigate resource consumption.
The `Representation-Digest` field-value is the same as in {{example-full-representation}} because `Representation-Digest` is designed to
be independent from the use of one or more transfer codings (see {{representation-digest}}).

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example

~~~
{: title="GET Request"}

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
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:

~~~
{: title="Chunked Response with Digest"}


# Examples of Want-Representation-Digest Solicited Digest {#examples-solicited}

The following examples demonstrate interactions where a client solicits a
`Representation-Digest` using `Want-Representation-Digest`.
The behavior of `Content-Digest` and `Want-Content-Digest` is identical.

Some examples include JSON objects in the content.
For presentation purposes, objects that fit completely within the line-length limits
are presented on a single line using compact notation with no leading space.
Objects that would exceed line-length limits are presented across multiple lines
(one line per key-value pair) with 2 spaced of leading indentation.

Checksum mechanisms described in this document are media-type agnostic
and do not provide canonicalization algorithms for specific formats.
Examples are calculated inclusive of any space.

## Server Selects Client's Least Preferred Algorithm

The client requests a digest, preferring "sha". The server is free to reply with
"sha-256" anyway.

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Want-Representation-Digest: sha-256=3, sha=10

~~~
{: title="GET Request with Want-Representation-Digest"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Representation-Digest: sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:

{"hello": "world"}
~~~
{: title="Response with Different Algorithm"}

##  Server Selects Algorithm Unsupported by Client {#ex-server-selects-unsupported-algorithm}

The client requests a "sha" digest because that is the only algorithm it
supports. The server is not obliged to produce a response containing a "sha"
digest, it instead uses a different algorithm.

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Want-Representation-Digest: sha=1

~~~
{: title="GET Request with Want-Representation-Digest"}

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Representation-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm
                +AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew==:

{"hello": "world"}
~~~
{: title="Response with Unsupported Algorithm"}

## Server Does Not Support Client Algorithm and Returns an Error

{{ex-server-selects-unsupported-algorithm}} is an example where a server ignores
the client's preferred digest algorithm. Alternatively a server can also reject
the request and return an error.

In this example, the client requests a "sha" `Representation-Digest`, and the server returns an
error with problem details {{?RFC7807}} contained in the content. The problem
details contain a list of the digest algorithms that the server supports. This
is purely an example, this specification does not define any format or
requirements for such content.

~~~ http-message
GET /items/123 HTTP/1.1
Host: foo.example
Want-Representation-Digest: sha=1

~~~
{: title="GET Request with Want-Representation-Digest"}

~~~ http-message
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "title": "Bad Request",
  "detail": "Supported hashing algorithms: sha-256, sha-512",
  "status": 400
}
~~~
{: title="Response advertising the supported algorithms"}


# Acknowledgements
{:numbered="false"}
This document is based on ideas from [RFC3230], so thanks
to J. Mogul and A. Van Hoff for their great work.
The original idea of refreshing RFC3230 arose from an interesting
discussion with M. Nottingham, J. Yasskin and M. Thomson when reviewing
the MICE content coding.

Thanks to Julian Reschke for his valuable contributions to this document,
and to the following contributors that have helped improve this specification by reporting bugs,
asking smart questions, drafting or reviewing text, and evaluating open issues:
Mike Bishop,
Brian Campbell,
Matthew Kerwin,
James Manger,
Tommy Pauly,
Sean Turner,
and Erik Wilde.


# Code Samples
{:numbered="false"}

_RFC Editor: Please remove this section before publication._

How can I generate and validate the `Representation-Digest` values shown in the examples
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

print("Encoding | hashing algorithm | digest-value")
print("Identity | sha256 |", digest(item))
# Encoding | hashing algorithm | digest-value
# Identity | sha256 | X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=

print("Encoding | hashing algorithm | digest-value")
print("Brotli | sha256 |", digest(item, encoding=brotli.compress))
# Encoding | hashing algorithm | digest-value
# Brotli | sha256 | 4REjxQ4yrqUVicfSKYNO/cF9zNj5ANbzgDZt3/h3Qxo=

print("Encoding | hashing algorithm | digest-value")
print("Identity | sha512 |", digest(item, algorithm=hashlib.sha512))
print("Brotli | sha512 |", digest(item, algorithm=hashlib.sha512,
                                    encoding=brotli.compress))
# Encoding | hashing algorithm | digest-value
# Identity | sha512 |b'WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+TaPm'
#                     '+AbwAgBWnrIiYllu7BNNyealdVLvRwE\nmTHWXvJwew=='
# Brotli | sha512 | b'pxo7aYzcGI88pnDnoSmAnaOEVys0MABhgvHY9+VI+ElE6'
#                   '0jBCwnMPyA/s3NF3ZO5oIWA7lf8ukk+\n5KJzm3p5og=='

~~~

# Changes
{:numbered="false"}

_RFC Editor: Please remove this section before publication._

## Since draft-ietf-httpbis-digest-headers-06
{:numbered="false"}

* Remove id-sha-256 and id-sha-512 from the list of supported algorithms #855

## Since draft-ietf-httpbis-digest-headers-05
{:numbered="false"}

* Reboot digest-algorithm values registry #1567
* Add Content-Digest #1542
* Remove SRI section #1478

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
