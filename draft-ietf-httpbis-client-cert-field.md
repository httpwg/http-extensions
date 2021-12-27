---
title: "Client-Cert HTTP Header Field: Conveying Client Certificate Information from TLS Terminating Reverse Proxies to Origin Server Applications"
abbrev: Client-Cert Field
docname: draft-ietf-httpbis-client-cert-field-latest
date: {DATE}
category: info

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword:
- http
- client certificate

stand_alone: yes
smart_quotes: no

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/client-cert-field
github-issue-label: client-cert-field

author:
  -
    ins: B. Campbell
    name: Brian Campbell
    organization: Ping Identity
    email: bcampbell@pingidentity.com
  -
    ins: M. Bishop
    name: Mike Bishop
    org: Akamai
    email: mbishop@evequefou.be
    role: editor


--- abstract

This document defines the HTTP header field `Client-Cert` that allows a TLS
terminating reverse proxy to convey the client certificate of a
mutually-authenticated TLS connection to the origin server in a common and
predictable manner.

--- middle

# Introduction {#Introduction}

A fairly common deployment pattern for HTTPS applications is to have the origin
HTTP application servers sit behind a reverse proxy that terminates TLS
connections from clients. The proxy is accessible to the internet and dispatches
client requests to the appropriate origin server within a private or protected
network. The origin servers are not directly accessible by clients and are only
reachable through the reverse proxy. The backend details of this type of
deployment are typically opaque to clients who make requests to the proxy server
and see responses as though they originated from the proxy server itself.
Although HTTPS is also usually employed between the proxy and the origin server,
the TLS connection that the client establishes for HTTPS is only between itself
and the reverse proxy server.

The deployment pattern is found in a number of varieties such as n-tier
architectures, content delivery networks, application load balancing services,
and ingress controllers.

Although not exceedingly prevalent, TLS client certificate authentication is
sometimes employed and in such cases the origin server often requires
information about the client certificate for its application logic. Such logic
might include access control decisions, audit logging, and binding issued tokens
or cookies to a certificate, and the respective validation of such bindings. The
specific details from the certificate needed also vary with the application
requirements. In order for these types of application deployments to work in
practice, the reverse proxy needs to convey information about the client
certificate to the origin application server. A common way this information is
conveyed in practice today is by using non-standard fields to carry the
certificate (in some encoding) or individual parts thereof in the HTTP request
that is dispatched to the origin server. This solution works but
interoperability between independently developed components can be cumbersome or
even impossible depending on the implementation choices respectively made (like
what field names are used or are configurable, which parts of the certificate
are exposed, or how the certificate is encoded). A well-known predictable
approach to this commonly occurring functionality could improve and simplify
interoperability between independent implementations.

This document aspires to standardize an HTTP header field named `Client-Cert`
that a TLS terminating reverse proxy (TTRP) adds to requests that it sends to
the backend origin servers. The field value contains the client certificate from
the mutually-authenticated TLS connection between the originating client and the
TTRP. This enables the backend origin server to utilize the client certificate
information in its application logic. While there may be additional proxies or
hops between the TTRP and the origin server (potentially even with
mutually-authenticated TLS connections between them), the scope of the
`Client-Cert` header field is intentionally limited to exposing to the origin
server the certificate that was presented by the originating client in its
connection to the TTRP.


## Requirements Notation and Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 {{!RFC2119}} {{!RFC8174}}
when, and only when, they appear in all capitals, as shown here.

## Terminology

Phrases like TLS client certificate authentication or mutually-authenticated TLS
are used throughout this document to refer to the process whereby, in addition
to the normal TLS server authentication with a certificate, a client presents
its X.509 certificate {{!RFC5280}} and proves possession of the corresponding
private key to a server when negotiating a TLS connection or the resumption of
such a connection.  In contemporary versions of TLS {{?RFC8446}} {{?RFC5246}} this
requires that the client send the Certificate and CertificateVerify messages
during the handshake and for the server to verify the CertificateVerify and
Finished messages.


# HTTP Header Field and Processing Rules

## Encoding

The headers in this document encode certificates as Structured Field Byte
Sequences ({{Section 3.3.5 of RFC8941}}).

The binary sequence is always a DER {{!ITU.X690.1994}} PKIX certificate. The
encoded value MUST NOT include any line breaks, whitespace, or other additional
characters. A binary sequence which cannot be successfully parsed as a
certificate MUST be ignored.

Note that DER certificates are often stored in a format which is already
compatible with {{!RFC8941}}; if so, it will be sufficient to replace
`---(BEGIN|END) CERTIFICATE---` with `:` and remove line breaks in order
to generate an appropriate item.

## Client-Cert HTTP Header Field {#header}

In the context of a TLS terminating reverse proxy (TTRP) deployment, the proxy
makes the TLS client certificate available to the backend application with the
Client-Cert HTTP header field. This field contains the end-entity certificate
used by the client in the TLS handshake.

Client-Cert is an Item Structured Header {{!RFC8941}}.  Its value MUST be a
Byte Sequence ({{Section 3.3.5 of RFC8941}}).  Its ABNF is:

~~~
 Client-Cert = sf-binary
~~~

The value of the header is encoded as described in {{encoding}}.

The `Client-Cert` header field is only for use in HTTP requests and MUST NOT be
used in HTTP responses.  It is a single HTTP header field value as defined in
Section 3.2 of {{?RFC7230}}, which MUST NOT have a list of values or occur
multiple times in a request.

## Client-Cert-Chain HTTP Header Field {#chain-header}

In the context of a TLS terminating reverse proxy (TTRP) deployment, the proxy
MAY make the certificate chain used for validation of the end-entity certificate
available to the backend application with the Client-Cert-Chain HTTP header
field. This field contains certificates used by the proxy to validate the
certificate used by the client in the TLS handshake. These certificates might or
might not have been provided by the client during the TLS handshake.

Client-Cert-Chain is a List Structured Header {{!RFC8941}}.  Each item in the
list MUST be a Byte Sequence ({{Section 3.3.5 of RFC8941}}) encoded as described
in {{encoding}}.

The header's ABNF is:

~~~
 Client-Cert-Chain = sf-list
~~~

The `Client-Cert-Chain` header field is only for use in HTTP requests and MUST
NOT be used in HTTP responses.  It MAY have a list of values or occur multiple
times in a request.  For header compression purposes, it might be advantageous
to split lists into multiple instances.

The first certificate in the list SHOULD directly certify the end-entity
certificate provided in the `Client-Cert` header; each following certificate
SHOULD directly certify the one immediately preceding it.  Because certificate
validation requires that trust anchors be distributed independently, a
certificate that specifies a trust anchor MAY be omitted from the chain,
provided that the server is known to possess any omitted certificates.

However, for maximum compatibility, servers SHOULD be prepared to handle
potentially extraneous certificates and arbitrary orderings.

## Processing Rules

This section outlines the applicable processing rules for a TLS terminating
reverse proxy (TTRP) that has negotiated a mutually-authenticated TLS connection
to convey the client certificate from that connection to the backend origin
servers. Use of the technique is to be a configuration or deployment option and
the processing rules described herein are for servers operating with that option
enabled.

A TTRP negotiates the use of a mutually-authenticated TLS connection with the
client, such as is described in {{?RFC8446}} or {{?RFC5246}}, and validates the
client certificate per its policy and trusted certificate authorities.  Each
HTTP request on the underlying TLS connection are dispatched to the origin
server with the following modifications:

1. The client certificate is be placed in the `Client-Cert` header field of the
   dispatched request as defined in {{header}}.
1. Any occurrence of the `Client-Cert` header field in the original incoming
   request MUST be removed or overwritten before forwarding the request. An
   incoming request that has a `Client-Cert` header field MAY be rejected with
   an HTTP 400 response.

Requests made over a TLS connection where the use of client certificate
authentication was not negotiated MUST be sanitized by removing any and all
occurrences `Client-Cert` header field prior to dispatching the request to the
backend server.

Backend origin servers may then use the `Client-Cert` header field of the
request to determine if the connection from the client to the TTRP was
mutually-authenticated and, if so, the certificate thereby presented by the
client.

Forward proxies and other intermediaries MUST NOT add the `Client-Cert` header
field to requests, or modify an existing `Client-Cert` header field. Similarly,
clients MUST NOT employ the `Client-Cert` header field in requests.

A server that receives a request with a `Client-Cert` header field value that it
considers to be too large can respond with an HTTP 431 status code per Section 5
of {{?RFC6585}}.


# Security Considerations {#sec}

The header field described herein enable a TTRP and backend or origin server to
function together as though, from the client's perspective, they are a single
logical server side deployment of HTTPS over a mutually-authenticated TLS
connection. Use of the `Client-Cert` header field outside that intended use
case, however, may undermine the protections afforded by TLS client certificate
authentication. Therefore steps MUST be taken to prevent unintended use, both in
sending the header field and in relying on its value.

Producing and consuming the `Client-Cert` header field SHOULD be a configurable
option, respectively, in a TTRP and backend server (or individual application in
that server). The default configuration for both should be to not use the
`Client-Cert` header field thus requiring an "opt-in" to the functionality.

In order to prevent field injection, backend servers MUST only accept the
`Client-Cert` header field from a trusted TTRP (or other proxy in a trusted path
from the TTRP). A TTRP MUST sanitize the incoming request before forwarding it
on by removing or overwriting any existing instances of the field. Otherwise
arbitrary clients can control the field value as seen and used by the backend
server. It is important to note that neglecting to prevent field injection does
not "fail safe" in that the nominal functionality will still work as expected
even when malicious actions are possible. As such, extra care is recommended in
ensuring that proper field sanitation is in place.

The communication between a TTRP and backend server needs to be secured against
eavesdropping and modification by unintended parties.

The configuration options and request sanitization are necessarily functionally
of the respective servers. The other requirements can be met in a number of
ways, which will vary based on specific deployments. The communication between a
TTRP and backend or origin server, for example, might be authenticated in some
way with the insertion and consumption of the `Client-Cert` field occurring
only on that connection. Alternatively the network topology might dictate a
private network such that the backend application is only able to accept
requests from the TTRP and the proxy can only make requests to that server.
Other deployments that meet the requirements set forth herein are also possible.


# IANA Considerations

The `Client-Cert` HTTP header field will be added to the registry defined by http-core.

--- back

# Example

In a hypothetical example where a TLS client presents the client and
intermediate certificate from {{example-chain}} when establishing a
mutually-authenticated TLS connection with the TTRP, the proxy would send the
`Client-Cert` field shown in {#example-header} to the backend. Note that line
breaks and whitespace have been added to the field value in {{example-header}}
for display and formatting purposes only.

~~~
-----BEGIN CERTIFICATE-----
MIIBqDCCAU6gAwIBAgIBBzAKBggqhkjOPQQDAjA6MRswGQYDVQQKDBJMZXQncyBB
dXRoZW50aWNhdGUxGzAZBgNVBAMMEkxBIEludGVybWVkaWF0ZSBDQTAeFw0yMDAx
MTQyMjU1MzNaFw0yMTAxMjMyMjU1MzNaMA0xCzAJBgNVBAMMAkJDMFkwEwYHKoZI
zj0CAQYIKoZIzj0DAQcDQgAE8YnXXfaUgmnMtOXU/IncWalRhebrXmckC8vdgJ1p
5Be5F/3YC8OthxM4+k1M6aEAEFcGzkJiNy6J84y7uzo9M6NyMHAwCQYDVR0TBAIw
ADAfBgNVHSMEGDAWgBRm3WjLa38lbEYCuiCPct0ZaSED2DAOBgNVHQ8BAf8EBAMC
BsAwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0RAQH/BBMwEYEPYmRjQGV4YW1w
bGUuY29tMAoGCCqGSM49BAMCA0gAMEUCIBHda/r1vaL6G3VliL4/Di6YK0Q6bMje
SkC3dFCOOB8TAiEAx/kHSB4urmiZ0NX5r5XarmPk0wmuydBVoU4hBVZ1yhk=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIB5jCCAYugAwIBAgIBFjAKBggqhkjOPQQDAjBWMQswCQYDVQQGEwJVUzEbMBkG
A1UECgwSTGV0J3MgQXV0aGVudGljYXRlMSowKAYDVQQDDCFMZXQncyBBdXRoZW50
aWNhdGUgUm9vdCBBdXRob3JpdHkwHhcNMjAwMTE0MjEzMjMwWhcNMzAwMTExMjEz
MjMwWjA6MRswGQYDVQQKDBJMZXQncyBBdXRoZW50aWNhdGUxGzAZBgNVBAMMEkxB
IEludGVybWVkaWF0ZSBDQTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJf+aA54
RC5pyLAR5yfXVYmNpgd+CGUTDp2KOGhc0gK91zxhHesEYkdXkpS2UN8Kati+yHtW
CV3kkhCngGyv7RqjZjBkMB0GA1UdDgQWBBRm3WjLa38lbEYCuiCPct0ZaSED2DAf
BgNVHSMEGDAWgBTEA2Q6eecKu9g9yb5glbkhhVINGDASBgNVHRMBAf8ECDAGAQH/
AgEAMA4GA1UdDwEB/wQEAwIBhjAKBggqhkjOPQQDAgNJADBGAiEA5pLvaFwRRkxo
mIAtDIwg9D7gC1xzxBl4r28EzmSO1pcCIQCJUShpSXO9HDIQMUgH69fNDEMHXD3R
RX5gP7kuu2KGMg==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICBjCCAaygAwIBAgIJAKS0yiqKtlhoMAoGCCqGSM49BAMCMFYxCzAJBgNVBAYT
AlVTMRswGQYDVQQKDBJMZXQncyBBdXRoZW50aWNhdGUxKjAoBgNVBAMMIUxldCdz
IEF1dGhlbnRpY2F0ZSBSb290IEF1dGhvcml0eTAeFw0yMDAxMTQyMTI1NDVaFw00
MDAxMDkyMTI1NDVaMFYxCzAJBgNVBAYTAlVTMRswGQYDVQQKDBJMZXQncyBBdXRo
ZW50aWNhdGUxKjAoBgNVBAMMIUxldCdzIEF1dGhlbnRpY2F0ZSBSb290IEF1dGhv
cml0eTBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABFoaHU+Z5bPKmGzlYXtCf+E6
HYj62fORaHDOrt+yyh3H/rTcs7ynFfGn+gyFsrSP3Ez88rajv+U2NfD0o0uZ4Pmj
YzBhMB0GA1UdDgQWBBTEA2Q6eecKu9g9yb5glbkhhVINGDAfBgNVHSMEGDAWgBTE
A2Q6eecKu9g9yb5glbkhhVINGDAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQE
AwIBhjAKBggqhkjOPQQDAgNIADBFAiEAmAeg1ycKHriqHnaD4M/UDBpQRpkmdcRF
YGMg1Qyrkx4CIB4ivz3wQcQkGhcsUZ1SOImd/lq1Q0FLf09rGfLQPWDc
-----END CERTIFICATE-----
~~~
{: #example-chain title="Certificate Chain (with client certificate first)"}

~~~
Client-Cert: :MIIBqDCCAU6gAwIBAgIBBzAKBggqhkjOPQQDAjA6MRswGQYDVQQKDBJ
 MZXQncyBBdXRoZW50aWNhdGUxGzAZBgNVBAMMEkxBIEludGVybWVkaWF0ZSBDQTAeFw0
 yMDAxMTQyMjU1MzNaFw0yMTAxMjMyMjU1MzNaMA0xCzAJBgNVBAMMAkJDMFkwEwYHKoZ
 Izj0CAQYIKoZIzj0DAQcDQgAE8YnXXfaUgmnMtOXU/IncWalRhebrXmckC8vdgJ1p5Be
 5F/3YC8OthxM4+k1M6aEAEFcGzkJiNy6J84y7uzo9M6NyMHAwCQYDVR0TBAIwADAfBgN
 VHSMEGDAWgBRm3WjLa38lbEYCuiCPct0ZaSED2DAOBgNVHQ8BAf8EBAMCBsAwEwYDVR0
 lBAwwCgYIKwYBBQUHAwIwHQYDVR0RAQH/BBMwEYEPYmRjQGV4YW1wbGUuY29tMAoGCCq
 GSM49BAMCA0gAMEUCIBHda/r1vaL6G3VliL4/Di6YK0Q6bMjeSkC3dFCOOB8TAiEAx/k
 HSB4urmiZ0NX5r5XarmPk0wmuydBVoU4hBVZ1yhk=:
~~~
{: #example-header title="Header Field in HTTP Request to Origin Server"}





# Considerations Considered

## Field Injection

This draft requires that the TTRP sanitize the fields of the incoming request by
removing or overwriting any existing instances of the `Client-Cert` header field
before dispatching that request to the backend application. Otherwise, a client
could inject its own `Client-Cert` field that would appear to the backend to
have come from the TTRP. Although numerous other methods of detecting/preventing
field injection are possible; such as the use of a unique secret value as part
of the field name or value or the application of a signature, HMAC, or AEAD,
there is no common general standardized mechanism. The potential problem of
client field injection is not at all unique to the functionality of this draft
and it would therefor be inappropriate for this draft to define a one-off
solution. In the absence of a generic standardized solution existing currently,
stripping/sanitizing the fields is the de facto means of protecting against
field injection in practice today. Sanitizing the fields is sufficient when
properly implemented and is a normative requirement of {{sec}}.

## The Forwarded HTTP Extension

The `Forwarded` HTTP header field defined in {{?RFC7239}} allows proxy
components to disclose information lost in the proxying process. The TLS client
certificate information of concern to this draft could have been communicated
with an extension parameter to the `Forwarded` field; however, doing so
would have had some disadvantages that this draft endeavored to avoid. The
`Forwarded` field syntax allows for information about a full chain of proxied
HTTP requests, whereas the `Client-Cert` field of this document is concerned
only with conveying information about the certificate presented by the
originating client on the TLS connection to the TTRP (which appears as the
server from that client's perspective) to backend applications.  The multi-hop
syntax of the `Forwarded` field is expressive but also more complicated, which
would make processing it more cumbersome, and more importantly, make properly
sanitizing its content as required by {{sec}} to prevent field injection
considerably more difficult and error prone. Thus, this draft opted for the
flatter and more straightforward structure of a single `Client-Cert` header.

## The Whole Certificate and Only the Whole Certificate

Different applications will have varying requirements about what information
from the client certificate is needed, such as the subject and/or issuer
distinguished name, subject alternative name(s), serial number, subject public
key info, fingerprint, etc.. Furthermore some applications, such as "OAuth 2.0
Mutual-TLS Client Authentication and Certificate-Bound Access Tokens"
{{?RFC8705}}, make use of the entire certificate. In order to accommodate the
latter and ensure wide applicability by not trying to cherry-pick particular
certificate information, this draft opted to pass the full encoded certificate
as the value of the `Client-Cert` field.

The handshake and validation of the client certificate (chain) of the
mutually-authenticated TLS connection is performed by the TTRP.  With the
responsibility of certificate validation falling on the TTRP, only the
end-entity certificate is passed to the backend - the root Certificate Authority
is not included nor are any intermediates.


# Acknowledgements

The author would like to thank the following individuals who've contributed in various ways ranging from just being generally supportive of bringing forth the draft to providing specific feedback or content:

- Evan Anderson
- Annabelle Backman
- Mike Bishop
- Rory Hewitt
- Fredrik Jeansson
- Benjamin Kaduk
- Torsten Lodderstedt
- Kathleen Moriarty
- Mark Nottingham
- Mike Ounsworth
- Matt Peterson
- Eric Rescorla
- Justin Richer
- Michael Richardson
- Joe Salowey
- Rich Salz
- Mohit Sethi
- Rifaat Shekh-Yusef
- Travis Spencer
- Nick Sullivan
- Peter Wu
- Hans Zandbelt


# Document History

   > To be removed by the RFC Editor before publication as an RFC

   draft-ietf-httpbis-client-cert-field-00

   * Initial WG revision
   * Mike Bishop added as co-editor

   draft-bdc-something-something-certificate-05

   * Change intended status of the draft to Informational
   * Editorial updates and (hopefully) clarifications

   draft-bdc-something-something-certificate-04

   * Update reference from draft-ietf-oauth-mtls to RFC8705

   draft-bdc-something-something-certificate-03

   * Expanded further discussion notes to capture some of the feedback in and around the presentation of the draft in SECDISPATCH at IETF 107 and add those who've provided such feedback to the acknowledgements

   draft-bdc-something-something-certificate-02

   * Editorial tweaks + further discussion notes

   draft-bdc-something-something-certificate-01

   * Use the RFC v3 Format or die trying

   draft-bdc-something-something-certificate-00

   * Initial draft after a time constrained and rushed [secdispatch
     presentation](https://datatracker.ietf.org/meeting/106/materials/slides-106-secdispatch-securing-protocols-between-proxies-and-backend-http-servers-00)
     at IETF 106 in Singapore with the recommendation to write up a draft (at
     the end of the
     [minutes](https://datatracker.ietf.org/meeting/106/materials/minutes-106-secdispatch))
     and some folks expressing interest despite the rather poor presentation
