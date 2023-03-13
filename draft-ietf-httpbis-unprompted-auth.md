---
title: HTTP Unprompted Authentication
docname: draft-ietf-httpbis-unprompted-auth-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
category: std
wg: HTTPBIS
area: "Applications and Real-Time"
venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/unprompted-auth
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

informative:
  H2:
    =: RFC9113
    display: HTTP/2
  H3:
    =: RFC9114
    display: HTTP/3

--- abstract

Existing HTTP authentication mechanisms are probeable in the sense that it is
possible for an unauthenticated client to probe whether an origin serves
resources that require authentication. It is possible for an origin to hide the
fact that it requires authentication by not generating Unauthorized status
codes, however that only works with non-cryptographic authentication schemes:
cryptographic schemes (such as signatures or message authentication codes)
require a fresh nonce to be signed, and there is no existing way for the origin
to share such a nonce without exposing the fact that it serves resources that
require authentication. This document proposes a new non-probeable cryptographic
authentication scheme.

--- middle

# Introduction {#introduction}

Existing HTTP authentication mechanisms (see {{Section 11 of !HTTP=RFC9110}})
are probeable in the sense that it is possible for an unauthenticated client to
probe whether an origin serves resources that require authentication. It is
possible for an origin to hide the fact that it requires authentication by not
generating Unauthorized status codes, however that only works with
non-cryptographic authentication schemes: cryptographic schemes (such as
signatures or message authentication codes) require a fresh nonce to be signed,
and there is no existing way for the origin to share such a nonce without
exposing the fact that it serves resources that require authentication. This
document proposes a new non-probeable cryptographic authentication scheme.

Unprompted Authentication serves use cases in which a site wants to offer a
service or capability only to "those who know" while all others are given no
indication the service or capability exists. The conceptual model is that of a
"speakeasy". "Knowing" is via an externally-defined mechanism by which user
identifiers are distributed. For example, a company might offer remote employee
access to company services directly via its website using their employee ID, or
offer access to limited special capabilities for specific employees, while
making discovering (probing for) such capabilities difficult. Members of
less well-defined communities might more ephemeral identifiers to acquire access
to geography- or capability-specific resources, as issued by an entity whose
user base is larger than the available resources can support (by that entity
metering the availability of user identifiers temporally or geographically).
Unprompted Authentication is also useful for cases where a service provider
wants to distribute user-provisioning information for its resources without
exposing the provisioning location to non-users.

There are scenarios where servers may want to expose the fact that
authentication is required for access to specific resources. This is left for
future work.

## Conventions and Definitions {#conventions}

{::boilerplate bcp14-tagged}

This document uses the following terminology from {{Section 3 of
!STRUCTURED-FIELDS=RFC8941}} to specify syntax and parsing: Integer and Byte
Sequence.

# Computing the Authentication Proof {#compute-proof}

This document only defines the Signature and HMAC authentication schemes for
uses of HTTP with TLS {{!TLS=RFC8446}}. This includes any use of HTTP over TLS
as typically used for HTTP/2 {{H2}}, or HTTP/3 {{H3}} where the transport
protocol uses TLS as its authentication and key exchange mechanism
{{?QUIC-TLS=RFC9001}}.

The user agent leverages a TLS keying material exporter {{!KEY-EXPORT=RFC5705}}
to generate a nonce which can be signed using the chosen key. The keying
material exporter uses a label that starts with the characters
"EXPORTER-HTTP-Unprompted-Authentication-" (see {{schemes}} for the labels and
contexts used by each scheme). The TLS keying material exporter is used to
generate a 32-byte key which is then used as a nonce.

Because the TLS keying material exporter is only secure for authentication when
it is uniquely bound to the TLS session {{!RFC7627}}, the Signature and HMAC
authentication schemes require either one of the following properties:

* The TLS version in use is greater or equal to 1.3 {{TLS}}.
* The TLS version in use is greater or equal to 1.2 and the Extended
Master Secret extension {{RFC7627}} has been negotiated.

Clients MUST NOT use the Signature and HMAC authentication
schemes on connections that do not meet one of the two properties
above. If a server receives a request that uses these authentication
schemes on a connection that meets neither of the above properties,
the server MUST treat the request as malformed.

# Header Field Definition {#header-definition}

The "Unprompted-Authentication" header field allows a user agent to authenticate
with an origin server. The authentication is scoped to the HTTP request
associated with this header field. The value of the Unprompted-Authentication
header field is a credentials object, as defined in {{Section 11.4 of HTTP}}.
Credentials contain an authentication scheme followed by optional authentication
parameters.

# Authentication Parameters

This specification defines the following authentication parameters, they can be
used by the authentication schemes defined in {{schemes}}.

## The k Parameter {#parameter-k}

The OPTIONAL "k" (key ID) parameter is a byte sequence that identifies which key
the user agent wishes to use to authenticate. This can for example be used to
point to an entry into a server-side database of known keys.

## The p Parameter {#parameter-p}

The OPTIONAL "p" (proof) parameter is a byte sequence that specifies the proof
that the user agent provides to attest to possessing the credential that matches
its key ID.

## The s Parameter {#parameter-s}

The OPTIONAL "s" (signature) parameter is an integer that specifies the
signature algorithm used to compute the proof transmitted in the "p" directive.
Its value is an integer between 0 and 255 inclusive from the IANA "TLS
SignatureAlgorithm" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#tls-parameters-16)>.

## The h Parameter {#parameter-h}

The OPTIONAL "h" (hash) parameter is an integer that specifies the hash
algorithm used to compute the proof transmitted in the "p" directive. Its value
is an integer between 0 and 255 inclusive from the IANA "TLS HashAlgorithm"
registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#tls-parameters-18)>.

# Authentication Schemes {#schemes}

This document defines the "Signature" and "HMAC" HTTP authentication schemes.

## Signature {#signature}

The "Signature" HTTP Authentication Scheme uses asymmetric cryptography.
User agents possess a key ID and a public/private key pair, and origin servers
maintain a mapping of authorized key IDs to their associated public keys. When
using this scheme, the "k", "p", and "s" parameters are REQUIRED. The TLS keying
material export label for this scheme is
"EXPORTER-HTTP-Unprompted-Authentication-Signature" and the associated context
is empty. The nonce is then signed using the selected asymmetric signature
algorithm and transmitted as the proof directive.

For example, the key ID "basement" authenticating using Ed25519
{{?ED25519=RFC8410}} could produce the following header field (lines are folded
to fit):

~~~
Unprompted-Authentication: Signature k=:YmFzZW1lbnQ=:;s=7;
p=:SW5zZXJ0IHNpZ25hdHVyZSBvZiBub25jZSBoZXJlIHdo
aWNoIHRha2VzIDUxMiBiaXRzIGZvciBFZDI1NTE5IQ==:
~~~

## HMAC {#hmac}

The "HMAC" HTTP Authentication Scheme uses symmetric cryptography. User
agents possess a key ID and a secret key, and origin servers maintain a mapping
of authorized key IDs to their associated secret key. When using this scheme,
the "k", "p", and "h" parameters are REQUIRED. The TLS keying material export
label for this scheme is "EXPORTER-HTTP-Unprompted-Authentication-HMAC" and the
associated context is empty. The nonce is then HMACed using the selected HMAC
algorithm and transmitted as the proof directive.

For example, the key ID "basement" authenticating using HMAC-SHA-512
{{?SHA=RFC6234}} could produce the following header field (lines are folded to
fit):

~~~
Unprompted-Authentication: HMAC k="YmFzZW1lbnQ=";h=6;
p="SW5zZXJ0IEhNQUMgb2Ygbm9uY2UgaGVyZSB3aGljaCB0YWtl
cyA1MTIgYml0cyBmb3IgU0hBLTUxMiEhISEhIQ=="
~~~

## Other HTTP Authentication Schemes

The HTTP Authentication Scheme registry maintained by IANA at
<[](https://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml)>
contains entries not defined in this document. Those entries MAY be used with
Unprompted Authentication.

# Server Handling

Servers that wish to introduce resources whose existence cannot be probed need
to ensure that they do not reveal any information about those resources to
unauthenticated clients. In particular, such servers MUST respond to
authentication failures with the exact same response that they would have used
for non-existent resources. For example, this can mean using HTTP status code
404 (Not Found) instead of 401 (Unauthorized). Such authentication failures
can be caused for example by:
* absence of the Unprompted-Authentication field
* failure to parse the Unprompted-Authentication field
* use of Unprompted Authentication with an unknown key ID
* failure to validate the signature or MAC.

Such servers MUST also ensure that the timing of their request handling does
not leak any information. This can be accomplished by delaying responses to
all non-existent resources such that the timing of the authentication
verification is not observable.

# Intermediary Considerations {#intermediary}

Since the Signature and HMAC HTTP Authentication Schemes leverage TLS keying
material exporters, their output
cannot be transparently forwarded by HTTP intermediaries. HTTP intermediaries
that support this specification will validate the authentication received from
the client themselves, then inform the upstream HTTP server of the presence of
valid authentication using some other mechanism.

# Security Considerations {#security}

Unprompted Authentication allows a user agent to authenticate to an origin
server while guaranteeing freshness and without the need for the server
to transmit a nonce to the user agent. This allows the server to accept
authenticated clients without revealing that it supports or expects
authentication for some resources. It also allows authentication without
the user agent leaking the presence of authentication to observers due to
clear-text TLS Client Hello extensions.

The authentication proofs described in this document are not bound to individual
HTTP requests; if the key is used for authentication proofs on multiple
requests they will all be identical. This allows for better compression when
sending over the wire, but implies that client implementations that multiplex
different security contexts over a single HTTP connection need to ensure that
those contexts cannot read each other's header fields. Otherwise, one context
would be able to replay the unprompted authentication header field of another.
This constraint is met by modern Web browsers. If an attacker were to compromise
the browser such that it could access another context's memory, the attacker
might also be able to access the corresponding key, so binding authentication to
requests would not provide much benefit in practice.

Key material used for authentication in unprompted authentication, whether
symmetric or asymmetric MUST NOT be reused in other protocols. Doing so can
undermine the security guarantees of the authentication.

Sites offering Unprompted Authentication are able to link requests from
individuals clients via the Authentication Schemes provided. However,
requests are not linkable across other sites if the credentials used are
private to the individual sites using Unprompted Authentication.

# IANA Considerations {#iana}

## Unprompted-Authentication Header Field {#iana-header}

This document will request IANA to register the following entry in the "HTTP
Field Name" registry maintained at
<[](https://www.iana.org/assignments/http-fields)>:

Field Name:

: Unprompted-Authentication

Template:

: None

Status:

: provisional (permanent if this document is approved)

Reference:

: This document

Comments:

: None
{: spacing="compact"}

## HTTP Authentication Schemes Registry {#iana-schemes}

This document, if approved, requests IANA to add two new entries to the
"HTTP Authentication Schemes" Registry maintained at
<[](https://www.iana.org/assignments/http-authschemes)>.
Both entries have the Reference set to this document, and the Notes empty.
The Authentication Scheme Name of the entries are:

* Signature

* HMAC

## TLS Keying Material Exporter Labels {#iana-exporter-label}

This document, if approved, requests IANA to register the following entries in
the "TLS Exporter Labels" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#exporter-labels)>:

* EXPORTER-HTTP-Unprompted-Authentication-Signature

* EXPORTER-HTTP-Unprompted-Authentication-HMAC

Both of these entries are listed with the following qualifiers:

DTLS-OK:

: N

Recommended:

: Y

Reference:

: This document
{: spacing="compact"}

--- back

# Acknowledgments {#acknowledgments}
{:numbered="false"}

The authors would like to thank many members of the IETF community, as this
document is the fruit of many hallway conversations. Ben Schwartz contributed
ideas to this document.

