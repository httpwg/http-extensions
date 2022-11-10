---
title: "Client-Cert HTTP Header Field"
abbrev: Client-Cert Header
docname: draft-ietf-httpbis-client-cert-field-latest
submissionType: IETF
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

normative:
  RFC8941:
    display: STRUCTURED-FIELDS
  RFC9110:
    display: HTTP
informative:
  RFC9112:
    display: HTTP/1.1
  RFC9113:
    display: HTTP/2
  RFC9114:
    display: HTTP/3

--- abstract

This document defines HTTP extension header fields that allow a TLS
terminating reverse proxy to convey the client certificate information of a
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

This document aspires to standardize two HTTP header fields, `Client-Cert`
and `Client-Cert-Chain`,  which a TLS terminating reverse proxy (TTRP) adds to
requests sent to the backend origin servers. The `Client-Cert` field value
contains the end-entity client certificate from  the mutually-authenticated TLS
connection between the originating client and the TTRP. Optionally, the
`Client-Cert-Chain` field value contains the certificate chain used for
validation of the end-entity certificate. This enables the backend origin
server to utilize the client certificate
information in its application logic. While there may be additional proxies or
hops between the TTRP and the origin server (potentially even with
mutually-authenticated TLS connections between them), the scope of the
`Client-Cert` header field is intentionally limited to exposing to the origin
server the certificate that was presented by the originating client in its
connection to the TTRP.


## Requirements Notation and Conventions

{::boilerplate bcp14-tagged}

## Terminology and Applicability

This document uses the following terminology from {{Section 3 of RFC8941}}
to specify syntax and parsing: List and Byte Sequence.

Phrases like TLS client certificate authentication or mutually-authenticated TLS
are used throughout this document to refer to the process whereby, in addition
to the normal TLS server authentication with a certificate, a client presents
its X.509 certificate {{!RFC5280}} and proves possession of the corresponding
private key to a server when negotiating a TLS connection or the resumption of
such a connection.  In contemporary versions of TLS {{?TLS=RFC8446}}
{{?TLS1.2=RFC5246}} this requires that the client send the Certificate and
CertificateVerify messages during the handshake and for the server to verify the
CertificateVerify and Finished messages.

HTTP/2 restricts TLS 1.2 renegotiation ({{Section 9.2.1 of ?RFC9113}}) and
prohibits TLS 1.3 post-handshake authentication {{?RFC8740}}. However, they are
sometimes used to implement reactive client certificate authentication in HTTP/1.1
{{?RFC9112}} where the server decides whether to request a client certificate
based on the HTTP request. HTTP application data sent on such a connection
after receipt and verification of the client certificate is also
mutually-authenticated and thus suitable for the mechanisms described in this
document. With post-handshake authentication there is also the possibility, though
unlikely in practice, of multiple certificates and certificate chains from the
client on a connection, in which case only the certificate and chain
of the last post-handshake authentication are to be utilized for the header
fields described herein.

# HTTP Header Fields and Processing Rules {#headers}

This document designates the following headers, defined further in {{header}}
and {{chain-header}} respectively, to carry the client certificate information of a
mutually-authenticated TLS connection. The headers convey the information
from the reverse proxy to the origin server.

Client-Cert:
:  The end-entity certificate used by the client in the TLS handshake with
the reverse proxy.

Client-Cert-Chain:
: The certificate chain used for validation of the end-entity
certificate provided by the client in the TLS handshake with the reverse proxy.

## Encoding

The headers in this document encode certificates as Byte
Sequences ({{Section 3.3.5 of RFC8941}}) where the value of the binary data
is a DER encoded {{!ITU.X690.1994}} X.509 certificate {{!RFC5280}}.
In effect, this means that the binary DER certificate is encoded using base64
(without line breaks, spaces, or other characters outside the base64 alphabet)
and delimited with colons on either side.

Note that certificates are often stored encoded in a textual format, such as
the one described in {{Section 5.1 of ?RFC7468}}, which is already nearly
compatible with a Byte Sequence; if so, it will be sufficient to replace
`---(BEGIN|END) CERTIFICATE---` with `:` and remove line breaks in order
to generate an appropriate item.

## Client-Cert HTTP Header Field {#header}

In the context of a TLS terminating reverse proxy deployment, the proxy
makes the TLS client certificate available to the backend application with the
Client-Cert HTTP header field. This field contains the end-entity certificate
used by the client in the TLS handshake.

Client-Cert is a Byte Sequence with the value of
the header encoded as described in {{encoding}}.

The `Client-Cert` header field is only for use in HTTP requests and MUST NOT be
used in HTTP responses.  It is a singleton header field value as defined in
{{Section 5.5 of RFC9110}}, which MUST NOT have a list of values or occur
multiple times in a request.

## Client-Cert-Chain HTTP Header Field {#chain-header}

In the context of a TLS terminating reverse proxy deployment, the proxy
MAY make the certificate chain
available to the backend application with the Client-Cert-Chain HTTP header
field.

Client-Cert-Chain is a List ({{Section 3.3.1 of RFC8941}}).  Each item in the
list MUST be a Byte Sequence encoded as described in {{encoding}}. The order
is the same as the ordering in TLS (such as described in {{Section 4.4.2 of TLS}}).

The `Client-Cert-Chain` header field is only for use in HTTP requests and MUST
NOT be used in HTTP responses.  It MAY have a list of values or occur multiple
times in a request.  For header compression purposes, it might be advantageous
to split lists into multiple instances.



## Processing Rules

This section outlines the applicable processing rules for a TLS terminating
reverse proxy (TTRP) that has negotiated a mutually-authenticated TLS connection
to convey the client certificate from that connection to the backend origin
servers. Use of the technique is to be a configuration or deployment option and
the processing rules described herein are for servers operating with that option
enabled.

A TTRP negotiates the use of a mutually-authenticated TLS connection with the
client, such as is described in {{?TLS}} or {{?RFC5246}}, and validates the
client certificate per its policy and trusted certificate authorities.  Each
HTTP request on the underlying TLS connection are dispatched to the origin
server with the following modifications:

1. The client certificate is placed in the `Client-Cert` header field of the
   dispatched request, as described in {{header}}.
2. If so configured, the validation chain of the client certificate is placed in
   the `Client-Cert-Chain` header field of the request, as described in
   {{chain-header}}.
3. Any occurrence of the `Client-Cert` or `Client-Cert-Chain` header fields in
   the original incoming request MUST be removed or overwritten before
   forwarding the request. An incoming request that has a `Client-Cert` or
   `Client-Cert-Chain` header field MAY be rejected with an HTTP 400 response.

Requests made over a TLS connection where the use of client certificate
authentication was not negotiated MUST be sanitized by removing any and all
occurrences of the `Client-Cert` and `Client-Cert-Chain` header fields prior to
dispatching the request to the backend server.

Backend origin servers may then use the `Client-Cert` header field of the
request to determine if the connection from the client to the TTRP was
mutually-authenticated and, if so, the certificate thereby presented by the
client.
Access control decisions based on the client certificate (or lack thereof) can be
conveyed by selecting response content as appropriate or with an HTTP 403 response,
if the certificate is deemed unacceptable for the given context.
Note that TLS clients that rely on error indications at the TLS layer for an
unacceptable certificate will not receive those signals.

When the value of the `Client-Cert` request header field is used to select a response
(e.g., the response content is access-controlled), the response MUST either be
uncacheable (e.g., by sending `Cache-Control: no-store`) or be designated for
selective reuse only for subsequent requests with the same `Client-Cert`
header value by sending a `Vary: Client-Cert` response header.
If a TTRP encounters a response with a `client-cert` field name in the `Vary`
header field, it SHOULD prevent the user agent from caching the response by
transforming the value of the `Vary` response header field to `*`.

Forward proxies and other intermediaries MUST NOT add the `Client-Cert` or
`Client-Cert-Chain` header fields to requests, or modify an existing
`Client-Cert` or `Client-Cert-Chain` header field. Similarly, clients MUST NOT
employ the `Client-Cert` or `Client-Cert-Chain` header field in requests.

# Deployment Considerations {#deployment}

## Header Field Compression

If the client certificate header field is generated by an intermediary on a connection that
compresses fields (e.g., using HPACK {{?HPACK=RFC7541}} or QPACK {{?QPACK=RFC9204}})
and more than one client's requests are multiplexed into that connection, it can reduce
compression efficiency significantly, due to the typical size of the field value and
its variation between clients.
Recipients that anticipate connections with these characteristics can mitigate the
efficiency loss by increasing the size of the dynamic table.
If a recipient does not do so, senders may find it beneficial to always send the
field value as a literal, rather than entering it into the dynamic table.

## Header Block Size

A server in receipt of a larger header block than it is willing to handle can send
an HTTP 431 (Request Header Fields Too Large) status code per {{Section 5 of ?RFC6585}}.
Due to the typical size of the field values containing certificate data,
recipients may need to be configured to allow for a larger maximum header block size.
An intermediary generating client certificate header fields on connections that allow
for advertising the maximum acceptable header block size (e.g. HTTP/2 {{?RFC9113}}
or HTTP/3 {{?RFC9114}}) should account for the additional size of the header
block of the requests it sends vs. requests it receives by advertising a value to its
clients that is sufficiently smaller so as to allow for the addition of certificate data.

## TLS Session Resumption

Some TLS implementations do not retain client certificate information when resuming.
Providing inconsistent values of Client-Cert and Client-Cert-Chain when resuming might
lead to errors, so implementations that are unable to provide these values SHOULD
either disable resumption for connections with client certificates or initially omit a
`Client-Cert` or `Client-Cert-Chain` field if it might not be available after resuming.

# Security Considerations {#sec}

The header fields described herein enable a TTRP and backend or origin server to
function together as though, from the client's perspective, they are a single
logical server side deployment of HTTPS over a mutually-authenticated TLS
connection. Use of the header fields outside that intended use
case, however, may undermine the protections afforded by TLS client certificate
authentication. Therefore, steps MUST be taken to prevent unintended use, both in
sending the header field and in relying on its value.

Producing and consuming the `Client-Cert` and `Client-Cert-Chain` header
fields SHOULD be configurable
options, respectively, in a TTRP and backend server (or individual application in
that server). The default configuration for both should be to not use the
header fields thus requiring an "opt-in" to the functionality.

In order to prevent field injection, backend servers MUST only accept the
`Client-Cert` and `Client-Cert-Chain` header fields from a trusted
TTRP (or other proxy in a trusted path
from the TTRP). A TTRP MUST sanitize the incoming request before forwarding it
on by removing or overwriting any existing instances of the fields. Otherwise,
arbitrary clients can control the field values as seen and used by the backend
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
way with the insertion and consumption of the `Client-Cert`
and `Client-Cert-Chain` header fields occurring
only on that connection. Alternatively the network topology might dictate a
private network such that the backend application is only able to accept
requests from the TTRP and the proxy can only make requests to that server.
Other deployments that meet the requirements set forth herein are also possible.


# IANA Considerations

## HTTP Field Name Registrations

Please register the following entries in the "Hypertext Transfer Protocol (HTTP) Field
Name Registry" defined by HTTP Semantics {{RFC9110}}:

* Field name: Client-Cert
* Status: permanent
* Specification document: {{headers}} of \[this document]
<br>

* Field name: Client-Cert-Chain
* Status: permanent
* Specification document: {{headers}} of \[this document]

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

If the proxy were configured to also include the certificate chain, it would
also include this header:

~~~
Client-Cert-Chain: :MIIB5jCCAYugAwIBAgIBFjAKBggqhkjOPQQDAjBWMQsw
 CQYDVQQGEwJVUzEbMBkGA1UECgwSTGV0J3MgQXV0aGVudGljYXRlMSowKAYDVQQ
 DDCFMZXQncyBBdXRoZW50aWNhdGUgUm9vdCBBdXRob3JpdHkwHhcNMjAwMTE0Mj
 EzMjMwWhcNMzAwMTExMjEzMjMwWjA6MRswGQYDVQQKDBJMZXQncyBBdXRoZW50a
 WNhdGUxGzAZBgNVBAMMEkxBIEludGVybWVkaWF0ZSBDQTBZMBMGByqGSM49AgEG
 CCqGSM49AwEHA0IABJf+aA54RC5pyLAR5yfXVYmNpgd+CGUTDp2KOGhc0gK91zx
 hHesEYkdXkpS2UN8Kati+yHtWCV3kkhCngGyv7RqjZjBkMB0GA1UdDgQWBBRm3W
 jLa38lbEYCuiCPct0ZaSED2DAfBgNVHSMEGDAWgBTEA2Q6eecKu9g9yb5glbkhh
 VINGDASBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBhjAKBggqhkjO
 PQQDAgNJADBGAiEA5pLvaFwRRkxomIAtDIwg9D7gC1xzxBl4r28EzmSO1pcCIQC
 JUShpSXO9HDIQMUgH69fNDEMHXD3RRX5gP7kuu2KGMg==:, :MIICBjCCAaygAw
 IBAgIJAKS0yiqKtlhoMAoGCCqGSM49BAMCMFYxCzAJBgNVBAYTAlVTMRswGQYDV
 QQKDBJMZXQncyBBdXRoZW50aWNhdGUxKjAoBgNVBAMMIUxldCdzIEF1dGhlbnRp
 Y2F0ZSBSb290IEF1dGhvcml0eTAeFw0yMDAxMTQyMTI1NDVaFw00MDAxMDkyMTI
 1NDVaMFYxCzAJBgNVBAYTAlVTMRswGQYDVQQKDBJMZXQncyBBdXRoZW50aWNhdG
 UxKjAoBgNVBAMMIUxldCdzIEF1dGhlbnRpY2F0ZSBSb290IEF1dGhvcml0eTBZM
 BMGByqGSM49AgEGCCqGSM49AwEHA0IABFoaHU+Z5bPKmGzlYXtCf+E6HYj62fOR
 aHDOrt+yyh3H/rTcs7ynFfGn+gyFsrSP3Ez88rajv+U2NfD0o0uZ4PmjYzBhMB0
 GA1UdDgQWBBTEA2Q6eecKu9g9yb5glbkhhVINGDAfBgNVHSMEGDAWgBTEA2Q6ee
 cKu9g9yb5glbkhhVINGDAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBh
 jAKBggqhkjOPQQDAgNIADBFAiEAmAeg1ycKHriqHnaD4M/UDBpQRpkmdcRFYGMg
 1Qyrkx4CIB4ivz3wQcQkGhcsUZ1SOImd/lq1Q0FLf09rGfLQPWDc:
~~~
{: #example-chain-header title="Certificate Chain in HTTP Request to Origin Server"}



# Considerations Considered

## Field Injection

This draft requires that the TTRP sanitize the fields of the incoming request by
removing or overwriting any existing instances of the `Client-Cert`
and `Client-Cert-Chain` header fields
before dispatching that request to the backend application. Otherwise, a client
could inject its own values that would appear to the backend to
have come from the TTRP. Although numerous other methods of detecting/preventing
field injection are possible; such as the use of a unique secret value as part
of the field name or value or the application of a signature, HMAC, or AEAD,
there is no common general standardized mechanism. The potential problem of
client field injection is not at all unique to the functionality of this draft,
and it would therefore be inappropriate for this draft to define a one-off
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
HTTP requests, whereas the `Client-Cert` and `Client-Cert-Chain`
header fields of this document are concerned
only with conveying information about the certificate presented by the
originating client on the TLS connection to the TTRP (which appears as the
server from that client's perspective) to backend applications.  The multi-hop
syntax of the `Forwarded` field is expressive but also more complicated, which
would make processing it more cumbersome, and more importantly, make properly
sanitizing its content as required by {{sec}} to prevent field injection
considerably more difficult and error-prone. Thus, this draft opted for a
flatter and more straightforward structure.

## The Whole Certificate and Certificate Chain

Different applications will have varying requirements about what information
from the client certificate is needed, such as the subject and/or issuer
distinguished name, subject alternative name(s), serial number, subject public
key info, fingerprint, etc.. Furthermore, some applications, such as
{{?RFC8705}}, make use of the entire certificate. In order to accommodate the
latter and ensure wide applicability by not trying to cherry-pick particular
certificate information, this draft opted to pass the full encoded certificate
as the value of the `Client-Cert` field.

The validation of the client certificate and chain of the mutually-authenticated
TLS connection is typically performed by the TTRP during the handshake.  With the
responsibility of certificate validation falling on the TTRP, the
end-entity certificate is oftentimes sufficient for the needs of the origin server.
The separate `Client-Cert-Chain` field can convey the certificate chain for
origin server deployments that require this additional information.

# Acknowledgements

The authors would like to thank the following individuals who've contributed in various ways ranging from just being generally supportive of bringing forth the draft to providing specific feedback or content:

- Evan Anderson
- Annabelle Backman
- Alan Frindell
- Rory Hewitt
- Fredrik Jeansson
- Benjamin Kaduk
- Torsten Lodderstedt
- Kathleen Moriarty
- Mark Nottingham
- Erik Nygren
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
- Willy Tarreau
- Martin Thomson
- Peter Wu
- Hans Zandbelt


# Document History

   > To be removed by the RFC Editor before publication as an RFC

   draft-ietf-httpbis-client-cert-field-03

   * State that the certificate chain is in the same order as it appears in TLS rather than copying the language from TLS
   * Update references for HTTP Semantics, HTTP/3, and QPACK to point to the now RFCs 9110/9114/9204
   * HTTP Semantics now a normative ref
   * Mention that origin server access control decisions can be
     conveyed by selecting response content or with a 403

   draft-ietf-httpbis-client-cert-field-02

   * Add a note about cert retention on TLS session resumption
   * Say to use only the last one in the case of multiple post-handshake client cert authentications

   draft-ietf-httpbis-client-cert-field-01

   * Use RFC 8941 Structured Field Values for HTTP
   * Introduce a separate header that can convey the certificate chain
   * Add considerations on header compression and size
   * Describe interaction with caching
   * Fill out IANA Considerations with HTTP field name registrations
   * Discuss renegotiation

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
