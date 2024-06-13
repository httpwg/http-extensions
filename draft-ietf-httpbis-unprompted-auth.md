---
title: The Concealed HTTP Authentication Scheme
docname: draft-ietf-httpbis-unprompted-auth-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
category: std
wg: HTTPBIS
area: "Web and Internet Transport"
venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/unprompted-auth
  latest: "https://httpwg.org/http-extensions/draft-ietf-httpbis-unprompted-auth.html"
github-issue-label: unprompted-auth
keyword:
  - secure
  - tunnels
  - masque
  - http-ng
author:
  -
    ins: D. Schinazi
    name: David Schinazi
    org: Google LLC
    street: 1600 Amphitheatre Parkway
    city: Mountain View
    region: CA
    code: 94043
    country: United States of America
    email: dschinazi.ietf@gmail.com
  -
    ins: D. Oliver
    name: David M. Oliver
    org: Guardian Project
    email: david@guardianproject.info
    uri: https://guardianproject.info
  -
    ins: J. Hoyland
    name: Jonathan Hoyland
    org: Cloudflare Inc.
    email: jonathan.hoyland@gmail.com

normative:
  FOLDING: RFC8792
  X.690:
    title: "Information technology - ASN.1 encoding Rules: Specification of Basic Encoding Rules (BER), Canonical Encoding Rules (CER) and Distinguished Encoding Rules (DER)"
    date: 2021-02
    author:
      org: ITU-T
    seriesinfo:
      ISO/IEC 8824-1:2021

informative:
  H2:
    =: RFC9113
    display: HTTP/2
  H3:
    =: RFC9114
    display: HTTP/3
  SEEMS-LEGIT:
    title: "Seems Legit: Automated Analysis of Subtle Attacks on Protocols That Use Signatures"
    author:
      -
        initials: D.
        surname: Jackson
        name: Dennis Jackson
      -
        initials: C.
        surname: Cremers
        name: Cas Cremers
      -
        initials: K.
        surname: Cohn-Gordon
        name: Katriel Cohn-Gordon
      -
        initials: R.
        surname: Sasse
        name: Ralf Sasse
    date: 2019
    refcontent:
      - "CCS '19: Proceedings of the 2019 ACM SIGSAC Conference on Computer and Communications Security"
      - "pp. 2165–2180"
    seriesinfo:
      DOI: 10.1145/3319535.3339813


--- abstract

Most HTTP authentication schemes are probeable in the sense that it is possible
for an unauthenticated client to probe whether an origin serves resources that
require authentication. It is possible for an origin to hide the fact that it
requires authentication by not generating Unauthorized status codes, however
that only works with non-cryptographic authentication schemes: cryptographic
signatures require a fresh nonce to be signed. At the time of writing, there
was no existing way for the origin to share such a nonce without exposing the
fact that it serves resources that require authentication. This document
proposes a new non-probeable cryptographic authentication scheme.

--- middle

# Introduction {#introduction}

HTTP authentication schemes (see {{Section 11 of !HTTP=RFC9110}}) allow origins
to restrict access for some resources to only authenticated requests. While
these schemes commonly involve a challenge where the origin asks the client to
provide authentication information, it is possible for clients to send such
information unprompted. This is particularly useful in cases where an origin
wants to offer a service or capability only to "those who know" while all
others are given no indication the service or capability exists. Such designs
rely on an externally-defined mechanism by which keys are distributed. For
example, a company might offer remote employee access to company services
directly via its website using their employee credentials, or offer access to
limited special capabilities for specific employees, while making discovering
(or probing for) such capabilities difficult. Members of less well-defined
communities might use more ephemeral keys to acquire access to geography- or
capability-specific resources, as issued by an entity whose user base is larger
than the available resources can support (by having that entity metering the
availability of keys temporally or geographically).

While digital-signature-based HTTP authentication schemes already exist (e.g.,
{{?HOBA=RFC7486}}), they rely on the origin explicitly sending a fresh
challenge to the client, to ensure that the signature input is fresh. That
makes the origin probeable as it sends the challenge to unauthenticated
clients. This document defines a new signature-based authentication scheme that
is not probeable.

## Conventions and Definitions {#conventions}

{::boilerplate bcp14-tagged}

This document uses the notation from {{Section 1.3 of !QUIC=RFC9000}}.

# The Concealed Authentication Scheme

This document defines the "Concealed" HTTP authentication scheme. It uses
asymmetric cryptography. Clients possess a key ID and a public/private key
pair, and origin servers maintain a mapping of authorized key IDs to their
associated public keys.

The client uses a TLS keying material exporter to generate data to be signed
(see {{client}}) then sends the signature using the Authorization or
Proxy-Authorization header field. The signature and additional information are
exchanged using authentication parameters (see {{auth-params}}).

# Client Handling {#client}

When a client wishes to uses the Concealed HTTP authentication scheme with a
request, it SHALL compute the authentication proof using a TLS keying material
exporter {{!KEY-EXPORT=RFC5705}} with the following parameters:

* the label is set to "EXPORTER-HTTP-Concealed-Authentication"

* the context is set to the structure described in {{context}}

* the exporter output length is set to 48 bytes (see {{output}})

## Key Exporter Context {#context}

The TLS key exporter context is described in {{fig-context}}:

~~~
  Signature Algorithm (16),
  Key ID Length (i),
  Key ID (..),
  Public Key Length (i),
  Public Key (..),
  Scheme Length (i),
  Scheme (..),
  Host Length (i),
  Host (..),
  Port (16),
  Realm Length (i),
  Realm (..),
~~~
{: #fig-context title="Key Exporter Context Format"}

The key exporter context contains the following fields:

Signature Algorithm:

: The signature scheme sent in the `s` Parameter (see {{parameter-s}}).

Key ID:

: The key ID sent in the `k` Parameter (see {{parameter-k}}).

Public Key:

: The public key used by the server to validate the signature provided by the
client. Its encoding is described in {{public-key-encoding}}.

Scheme:

: The scheme for this request, encoded using the format of the scheme portion
of a URI as defined in {{Section 3.1 of !URI=RFC3986}}.

Host:

: The host for this request, encoded using the format of the host portion of a
URI as defined in {{Section 3.2.2 of URI}}.

Port:

: The port for this request, encoded in network byte order. Note that the port
is either included in the URI, or is the default port for the scheme in use;
see {{Section 3.2.3 of URI}}.

Realm:

: The realm of authentication that is sent in the realm authentication
parameter ({{Section 11.5 of HTTP}}). If the realm authentication parameter is
not present, this SHALL be empty. This document does not define a means for the
origin to communicate a realm to the client. If a client is not configured to
use a specific realm, it SHALL use an empty realm and SHALL NOT send the realm
authentication parameter.

The Signature Algorithm and Port fields are encoded as unsigned 16-bit integers
in network byte order. The Key ID, Public Key, Scheme, Host, and Realm fields
are length prefixed strings; they are preceded by a Length field that
represents their length in bytes. These length fields are encoded using the
variable-length integer encoding from {{Section 16 of QUIC}} and MUST be
encoded in the minimum number of bytes necessary.

### Public Key Encoding {#public-key-encoding}

Both the "Public Key" field of the TLS key exporter context (see above) and the
`a` Parameter (see {{parameter-a}}) carry the same public key. The encoding of
the public key is determined by the Signature Algorithm in use as follows:

RSASSA-PSS algorithms:

: The public key is an RSAPublicKey structure {{!PKCS1=RFC8017}} encoded in DER
{{X.690}}. BER encodings which are not DER MUST be rejected.

ECDSA algorithms:

: The public key is a UncompressedPointRepresentation structure defined in
{{Section 4.2.8.2 of TLS}}, using the curve specified by the SignatureScheme.

EdDSA algorithms:

: The public key is the byte string encoding defined in {{!EdDSA=RFC8032}}.

This document does not define the public key encodings for other algorithms. In
order for a SignatureScheme to be usable with the Concealed HTTP authentication
scheme, its public key encoding needs to be defined in a corresponding document.

## Key Exporter Output {#output}

The key exporter output is 48 bytes long. Of those, the first 32 bytes are part
of the input to the signature and the next 16 bytes are sent alongside the
signature. This allows the recipient to confirm that the exporter produces the
right values. This is described in {{fig-output}}:

~~~
  Signature Input (256),
  Verification (128),
~~~
{: #fig-output title="Key Exporter Output Format"}

The key exporter context contains the following fields:

Signature Input:

: This is part of the data signed using the client's chosen asymmetric private
key (see {{computation}}).

Verification:

: The verification is transmitted to the server using the `v` Parameter (see
{{parameter-v}}).

## Signature Computation {#computation}

Once the Signature Input has been extracted from the key exporter output (see
{{output}}), it is prefixed with static data before being signed to mitigate
issues caused by key reuse. The signature is computed over the concatenation of:

* A string that consists of octet 32 (0x20) repeated 64 times

* The context string "HTTP Concealed Authentication"

* A single 0 byte which serves as a separator

* The Signature Input extracted from the key exporter output (see {{output}})

For example, if the Signature Input has all its 32 bytes set to 01, the content
covered by the signature (in hexadecimal format) would be:

~~~
2020202020202020202020202020202020202020202020202020202020202020
2020202020202020202020202020202020202020202020202020202020202020
48545450205369676E61747572652041757468656E7469636174696F6E
00
0101010101010101010101010101010101010101010101010101010101010101
~~~
{: #fig-sig-example title="Example Content Covered by Signature"}

This construction mirrors that of the TLS 1.3 CertificateVerify message
defined in {{Section 4.4.3 of TLS}}.

The resulting signature is then transmitted to the server using the `p`
Parameter (see {{parameter-p}}).

# Authentication Parameters {#auth-params}

This specification defines the following authentication parameters.

All of the byte sequences below are encoded using base64url (see {{Section 5 of
!BASE64=RFC4648}}) without quotes and without padding. In other words, the
values of these byte-sequence authentication parameters MUST NOT include any
characters other then ASCII letters, digits, dash and underscore.

The integer below is encoded without a minus and without leading zeroes. In
other words, the value of this integer authentication parameter MUST NOT
include any characters other than digits, and MUST NOT start with a zero unless
the full value is "0".

Using the syntax from {{!ABNF=RFC5234}}:

~~~
concealed-byte-sequence-param-value = *( ALPHA / DIGIT / "-" / "_" )
concealed-integer-param-value =  %x31-39 1*4( DIGIT ) / "0"
~~~
{: #fig-param title="Authentication Parameter Value ABNF"}

## The k Parameter {#parameter-k}

The REQUIRED "k" (key ID) Parameter is a byte sequence that identifies which
key the client wishes to use to authenticate. This can, for example, be used to
point to an entry in a server-side database of known keys.

## The a Parameter {#parameter-a}

The REQUIRED "a" (public key) Parameter is a byte sequence that specifies the
public key used by the server to validate the signature provided by the client.
This avoids key confusion issues (see {{SEEMS-LEGIT}}). The encoding of the
public key is described in {{public-key-encoding}}.

## The p Parameter {#parameter-p}

The REQUIRED "p" (proof) Parameter is a byte sequence that specifies the proof
that the client provides to attest to possessing the credential that matches
its key ID.

## The s Parameter {#parameter-s}

The REQUIRED "s" (signature) Parameter is an integer that specifies the
signature scheme used to compute the proof transmitted in the `p` Parameter.
Its value is an integer between 0 and 65535 inclusive from the IANA "TLS
SignatureScheme" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-signaturescheme)>.

## The v Parameter {#parameter-v}

The REQUIRED "v" (verification) Parameter is a byte sequence that specifies the
verification that the client provides to attest to possessing the key exporter
output (see {{output}} for details). This avoids issues with signature schemes
where certain keys can generate signatures that are valid for multiple inputs
(see {{SEEMS-LEGIT}}).

# Example {#example}

For example, the key ID "basement" authenticating using Ed25519
{{?ED25519=RFC8410}} could produce the following header field:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Authorization: Concealed \
  k=YmFzZW1lbnQ, \
  a=VGhpcyBpcyBh-HB1YmxpYyBrZXkgaW4gdXNl_GhlcmU, \
  s=2055, \
  v=dmVyaWZpY2F0aW9u_zE2Qg, \
  p=SW5zZXJ0_HNpZ25hdHVyZSBvZiBub25jZSBoZXJlIHdo\
    aWNoIHRha2VzIDUxMiBiaXRz-GZvciBFZDI1NTE5IQ
~~~
{: #fig-hdr-example title="Example Header Field"}

# Server Handling

In this section, we subdivide the server role in two:

* the "frontend" runs in the HTTP server that terminates the TLS or QUIC
  connection created by the client.

* the "backend" runs in the HTTP server that has access to the database of
  accepted key identifiers and public keys.

In most deployments, we expect the frontend and backend roles to both be
implemented in a single HTTP origin server (as defined in {{Section 3.6 of
HTTP}}). However, these roles can be split such that the frontend is an HTTP
gateway (as defined in {{Section 3.7 of HTTP}}) and the backend is an HTTP
origin server.

## Frontend Handling

If a frontend is configured to check the Concealed authentication scheme, it
will parse the Authorization (or Proxy-Authorization) header field. If the
authentication scheme is set to "Concealed", the frontend MUST validate that
all the required authentication parameters are present and can be parsed
correctly as defined in {{auth-params}}. If any parameter is missing or fails
to parse, the frontend MUST ignore the entire Authorization (or
Proxy-Authorization) header field.

The frontend then uses the data from these authentication parameters to compute
the key exporter output, as defined in {{output}}. The frontend then shares the
header field and the key exporter output with the backend.

## Communication between Frontend and Backend

If the frontend and backend roles are implemented in the same machine, this can
be handled by a simple function call.

If the roles are split between two separate HTTP servers, then the backend
won't be able to directly access the TLS keying material exporter from the TLS
connection between the client and frontend, so the frontend needs to explictly
send it. This document defines the "Concealed-Auth-Export" request header field
for this purpose. The Concealed-Auth-Export header field's value is a
Structured Field Byte Sequence (see {{Section 3.3.5 of
!STRUCTURED-FIELDS=RFC8941}}) that contains the 48-byte key exporter output
(see {{output}}), without any parameters. For example:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Concealed-Auth-Export: :VGhpcyBleGFtcGxlIFRMUyBleHBvcn\
  RlciBvdXRwdXQgaXMgNDggYnl0ZXMgI/+h:
~~~
{: #fig-int-hdr-example title="Example Concealed-Auth-Export Header Field"}

The frontend SHALL forward the HTTP request to the backend, including the
original unmodified Authorization (or Proxy-Authorization) header field and the
newly added Concealed-Auth-Export header field.

Note that, since the security of this mechanism requires the key exporter
output to be correct, backends need to trust frontends to send it truthfully.
This trust relationship is common because the frontend already needs access to
the TLS certificate private key in order to respond to requests. HTTP servers
that parse the Concealed-Auth-Export header field MUST ignore it unless they
have already established that they trust the sender. Similarly, frontends that
send the Concealed-Auth-Export header field MUST ensure that they do not
forward any Concealed-Auth-Export header field received from the client.

## Backend Handling {#backend}

Once the backend receives the Authorization (or Proxy-Authorization) header
field and the key exporter output, it looks up the key ID in its database of
public keys. The backend SHALL then perform the following checks:

* validate that all the required authentication parameters are present and can
  be parsed correctly as defined in {{auth-params}}

* ensure the key ID is present in the backend's database and maps to a
  corresponding public key

* validate that the public key from the database is equal to the one in the
  Authorization (or Proxy-Authorization) header field

* validate that the verification field from the Authorization (or
  Proxy-Authorization) header field matches the one extracted from the key
  exporter output

* verify the cryptographic signature as defined in {{computation}}

If all of these checks succeed, the backend can consider the request to be
properly authenticated, and can reply accordingly (the backend can also forward
the request to another HTTP server).

If any of the above checks fail, the backend MUST treat it as if the
Authorization (or Proxy-Authorization) header field was missing.

## Non-Probeable Server Handling

Servers that wish to introduce resources whose existence cannot be probed need
to ensure that they do not reveal any information about those resources to
unauthenticated clients. In particular, such servers MUST respond to
authentication failures with the exact same response that they would have used
for non-existent resources. For example, this can mean using HTTP status code
404 (Not Found) instead of 401 (Unauthorized).

The authentication checks described above can take time to compute, and an
attacker could detect use of this mechanism if that time is observable by
comparing the timing of a request for a known non-existent resource to the
timing of a request for a potentially authenticated resource. Servers can
mitigate this observability by slightly delaying responses to some non-existent
resources such that the timing of the authentication verification is not
observable. This delay needs to be carefully considered to avoid having the
delay itself leak the fact that this origin uses this mechanism at all.

Non-probeable resources also need to be non-discoverable for unauthenticated
users. For example, if a server operator wishes to hide an authenticated
resource by pretending it does not exist to unauthenticated users, then the
server operator needs to ensure there are no unauthenticated pages with links
to that resource, and no other out-of-band ways for unauthenticated users to
discover this resource.

# Requirements on TLS Usage

This authentication scheme is only defined for uses of HTTP with TLS
{{!TLS=RFC8446}}. This includes any use of HTTP over TLS as typically used for
HTTP/2 {{H2}}, or HTTP/3 {{H3}} where the transport protocol uses TLS as its
authentication and key exchange mechanism {{?QUIC-TLS=RFC9001}}.

Because the TLS keying material exporter is only secure for authentication when
it is uniquely bound to the TLS session {{!RFC7627}}, the Concealed
authentication scheme requires either one of the following properties:

* The TLS version in use is greater or equal to 1.3 {{TLS}}.

* The TLS version in use is 1.2 and the Extended Master Secret extension
  {{RFC7627}} has been negotiated.

Clients MUST NOT use the Concealed authentication scheme on connections that do
not meet one of the two properties above. If a server receives a request that
uses this authentication scheme on a connection that meets neither of the above
properties, the server MUST treat the request as if the authentication were not
present.

# Security Considerations {#security}

The Concealed HTTP authentication scheme allows a client to authenticate to an
origin server while guaranteeing freshness and without the need for the server
to transmit a nonce to the client. This allows the server to accept
authenticated clients without revealing that it supports or expects
authentication for some resources. It also allows authentication without the
client leaking the presence of authentication to observers due to clear-text
TLS Client Hello extensions.

Since the freshness described above is provided by a TLS key exporter, it can
be as old as the underlying TLS connection. Servers can require better
freshness by forcing clients to create new connections using mechanisms such as
the GOAWAY frame (see {{Section 5.2 of H3}}).

The authentication proofs described in this document are not bound to
individual HTTP requests; if the key is used for authentication proofs on
multiple requests on the same connection, they will all be identical. This
allows for better compression when sending over the wire, but implies that
client implementations that multiplex different security contexts over a single
HTTP connection need to ensure that those contexts cannot read each other's
header fields. Otherwise, one context would be able to replay the Authorization
header field of another. This constraint is met by modern Web browsers. If an
attacker were to compromise the browser such that it could access another
context's memory, the attacker might also be able to access the corresponding
key, so binding authentication to requests would not provide much benefit in
practice.

Key material used for the Concealed HTTP authentication scheme MUST NOT be
reused in other protocols. Doing so can undermine the security guarantees of
the authentication.

Origins offering this scheme can link requests that use the same key.
However, requests are not linkable across origins if the keys used are specific
to the individual origins using this scheme.

# IANA Considerations {#iana}

## HTTP Authentication Schemes Registry {#iana-schemes}

This document, if approved, requests IANA to register the following entry in
the "HTTP Authentication Schemes" Registry maintained at
<[](https://www.iana.org/assignments/http-authschemes)>:

Authentication Scheme Name:

: Concealed

Reference:

: This document

Notes:

: None
{: spacing="compact"}

## TLS Keying Material Exporter Labels {#iana-exporter-label}

This document, if approved, requests IANA to register the following entry in
the "TLS Exporter Labels" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#exporter-labels)>:

Value:

: EXPORTER-HTTP-Concealed-Authentication

DTLS-OK:

: N

Recommended:

: Y

Reference:

: This document
{: spacing="compact"}

## HTTP Field Name

This document, if approved, requests IANA to register the following entry in
the "Hypertext Transfer Protocol (HTTP) Field Name" registry maintained at
<[](https://www.iana.org/assignments/http-fields/http-fields.xhtml)>:

Field Name:

: Concealed-Auth-Export

Template:

: None

Status:

: permanent

Reference:

: This document

Comments:

: None
{: spacing="compact"}

--- back

# Acknowledgments {#acknowledgments}
{:numbered="false"}

The authors would like to thank many members of the IETF community, as this
document is the fruit of many hallway conversations. In particular, the authors
would like to thank {{{David Benjamin}}}, {{{Nick Harper}}}, {{{Dennis
Jackson}}}, {{{Ilari Liusvaara}}}, {{{François Michel}}}, {{{Lucas Pardue}}},
{{{Justin Richer}}}, {{{Ben Schwartz}}}, {{{Martin Thomson}}}, and
{{{Chris A. Wood}}} for their reviews and contributions. The mechanism
described in this document was originally part of the first iteration of MASQUE
{{?MASQUE-ORIGINAL=I-D.schinazi-masque-00}}.

