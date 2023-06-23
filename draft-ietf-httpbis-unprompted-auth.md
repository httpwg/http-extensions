---
title: The Signature HTTP Authentication Scheme
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

Existing HTTP authentication schemes are probeable in the sense that it is
possible for an unauthenticated client to probe whether an origin serves
resources that require authentication. It is possible for an origin to hide the
fact that it requires authentication by not generating Unauthorized status
codes, however that only works with non-cryptographic authentication schemes:
cryptographic signatures require a fresh nonce to be signed, and there is no
existing way for the origin to share such a nonce without exposing the fact
that it serves resources that require authentication. This document proposes a
new non-probeable cryptographic authentication scheme.

--- middle

# Introduction {#introduction}

Existing HTTP authentication schemes (see {{Section 11 of !HTTP=RFC9110}}) are
probeable in the sense that it is possible for an unauthenticated client to
probe whether an origin serves resources that require authentication. It is
possible for an origin to hide the fact that it requires authentication by not
generating Unauthorized status codes, however that only works with
non-cryptographic authentication schemes: cryptographic signatures require a
fresh nonce to be signed, and there is no existing way for the origin to share
such a nonce without exposing the fact that it serves resources that require
authentication. This document proposes a new non-probeable cryptographic
authentication scheme.

The Signature HTTP authentication scheme serves use cases in which a site wants
to offer a service or capability only to "those who know" while all others are
given no indication the service or capability exists. The conceptual model is
that of a "speakeasy". "Knowing" is via an externally-defined mechanism by
which keys are distributed. For example, a company might offer remote employee
access to company services directly via its website using their employee
credentials, or offer access to limited special capabilities for specific
employees, while making discovering (probing for) such capabilities difficult.
Members of less well-defined communities might use more ephemeral keys to
acquire access to geography- or capability-specific resources, as issued by an
entity whose user base is larger than the available resources can support (by
having that entity metering the availability of keys temporally or
geographically). The Signature HTTP authentication scheme is also useful for
cases where a service provider wants to distribute user-provisioning
information for its resources without exposing the provisioning location to
non-users.

There are scenarios where servers may want to expose the fact that
authentication is required for access to specific resources. This is left for
future work.

## Conventions and Definitions {#conventions}

{::boilerplate bcp14-tagged}

This document uses the following terminology from {{Section 3 of
!STRUCTURED-FIELDS=RFC8941}} to specify syntax and parsing: Integer and Byte
Sequence.

# The Signature Authentication Scheme

This document defines the "Signature" HTTP authentication scheme. It uses
asymmetric cryptography. User agents possess a key ID and a public/private key
pair, and origin servers maintain a mapping of authorized key IDs to their
associated public keys.

This authentication scheme is only defined for uses of HTTP with TLS
{{!TLS=RFC8446}}. This includes any use of HTTP over TLS as typically used for
HTTP/2 {{H2}}, or HTTP/3 {{H3}} where the transport protocol uses TLS as its
authentication and key exchange mechanism {{?QUIC-TLS=RFC9001}}.

Because the TLS keying material exporter is only secure for authentication when
it is uniquely bound to the TLS session {{!RFC7627}}, the Signature
authentication scheme requires either one of the following properties:

* The TLS version in use is greater or equal to 1.3 {{TLS}}.
* The TLS version in use is greater or equal to 1.2 and the Extended
Master Secret extension {{RFC7627}} has been negotiated.

Clients MUST NOT use the Signature authentication scheme on connections that do
not meet one of the two properties above. If a server receives a request that
uses this authentication scheme on a connection that meets neither of the above
properties, the server MUST treat the request as malformed.

# Computing the Authentication Proof {#compute-proof}

The user agent leverages a TLS keying material exporter {{!KEY-EXPORT=RFC5705}}
with the label "EXPORTER-HTTP-Signature-Authentication" to generate a 32-byte
symmetric key. That symmetric key is then used as nonce which can be signed
using the client's chosen asymmetric private key. The resulting signature is
then transmitted to the server using the Authorization field.

# Authentication Parameters

This specification defines the following authentication parameters:

## The k Parameter {#parameter-k}

The REQUIRED "k" (key ID) parameter is a byte sequence that identifies which key
the user agent wishes to use to authenticate. This can for example be used to
point to an entry into a server-side database of known keys.

## The p Parameter {#parameter-p}

The REQUIRED "p" (proof) parameter is a byte sequence that specifies the proof
that the user agent provides to attest to possessing the credential that matches
its key ID.

## The s Parameter {#parameter-s}

The REQUIRED "s" (signature) parameter is an integer that specifies the
signature scheme used to compute the proof transmitted in the "p" directive.
Its value is an integer between 0 and 65535 inclusive from the IANA "TLS
SignatureScheme" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-signaturescheme)>.

For example, the key ID "basement" authenticating using Ed25519
{{?ED25519=RFC8410}} could produce the following header field (lines are folded
to fit):

~~~
Authorization: Signature k=:YmFzZW1lbnQ=:;s=2055;
p=:SW5zZXJ0IHNpZ25hdHVyZSBvZiBub25jZSBoZXJlIHdo
aWNoIHRha2VzIDUxMiBiaXRzIGZvciBFZDI1NTE5IQ==:
~~~

# Server Handling

Servers that wish to introduce resources whose existence cannot be probed need
to ensure that they do not reveal any information about those resources to
unauthenticated clients. In particular, such servers MUST respond to
authentication failures with the exact same response that they would have used
for non-existent resources. For example, this can mean using HTTP status code
404 (Not Found) instead of 401 (Unauthorized). Such authentication failures
can be caused for example by:
* absence of the Authorization field
* failure to parse the Authorization field
* use of the Signature authentication scheme with an unknown key ID
* failure to validate the signature.

Such servers MUST also ensure that the timing of their request handling does
not leak any information. This can be accomplished by delaying responses to
all non-existent resources such that the timing of the authentication
verification is not observable.

# Intermediary Considerations {#intermediary}

Since the Signature HTTP authentication scheme leverages TLS keying material
exporters, its output cannot be transparently forwarded by HTTP intermediaries.
HTTP intermediaries that support this specification have two options:

* The intermediary can validate the authentication received from the client,
then inform the upstream HTTP server of the presence of valid authentication.

* The intermediary can export the nonce (see {{compute-proof}}}), and forward
it to the upstream HTTP server, then the upstream server performs the
validation.

The mechanism for the intermediary to communicate this information to the
upstream HTTP server is out of scope for this document.

# Security Considerations {#security}

The Signature HTTP authentication scheme allows a user agent to authenticate to
an origin server while guaranteeing freshness and without the need for the
server to transmit a nonce to the user agent. This allows the server to accept
authenticated clients without revealing that it supports or expects
authentication for some resources. It also allows authentication without the
user agent leaking the presence of authentication to observers due to
clear-text TLS Client Hello extensions.

The authentication proofs described in this document are not bound to
individual HTTP requests; if the key is used for authentication proofs on
multiple requests they will all be identical. This allows for better
compression when sending over the wire, but implies that client implementations
that multiplex different security contexts over a single HTTP connection need
to ensure that those contexts cannot read each other's header fields.
Otherwise, one context would be able to replay the Authorization header field
of another. This constraint is met by modern Web browsers. If an attacker were
to compromise the browser such that it could access another context's memory,
the attacker might also be able to access the corresponding key, so binding
authentication to requests would not provide much benefit in practice.

Key material used for the Signature HTTP authentication scheme MUST NOT be
reused in other protocols. Doing so can undermine the security guarantees of
the authentication.

Origins offering this scheme are able to link requests that use the same key.
However, requests are not linkable across origins if the keys used are specific
to the individual origins using this scheme.

# IANA Considerations {#iana}

## HTTP Authentication Schemes Registry {#iana-schemes}

This document, if approved, requests IANA to register the following entry in
the "HTTP Authentication Schemes" Registry maintained at
<[](https://www.iana.org/assignments/http-authschemes)>:

Authentication Scheme Name:

: Signature

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

: EXPORTER-HTTP-Signature-Authentication

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

