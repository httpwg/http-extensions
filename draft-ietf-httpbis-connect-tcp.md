---
title: "Template-Driven HTTP CONNECT Proxying for TCP"
abbrev: "Templated CONNECT-TCP"
category: std

docname: draft-ietf-httpbis-connect-tcp-latest
ipr: trust200902
area: art
submissiontype: IETF
workgroup: httpbis
keyword: Internet-Draft

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

author:
 -
    name: Benjamin M. Schwartz
    organization: Meta Platforms, Inc.
    email: ietf@bemasc.net

normative:

informative:
  CAPABILITY:
    title: Good Practices for Capability URLs
    date: 18 February 2014
    target: https://www.w3.org/TR/capability-urls/
  CLEAR-SITE-DATA:
    title: Clear Site Data
    date: 30 November 2017
    target: https://www.w3.org/TR/clear-site-data/

--- abstract

TCP proxying using HTTP CONNECT has long been part of the core HTTP specification.  However, this proxying functionality has several important deficiencies in modern HTTP environments.  This specification defines an alternative HTTP proxy service configuration for TCP connections.  This configuration is described by a URI Template, similar to the CONNECT-UDP and CONNECT-IP protocols.

--- middle

# Introduction

## History

HTTP has used the CONNECT method for proxying TCP connections since HTTP/1.1.  When using CONNECT, the request target specifies a host and port number, and the proxy forwards TCP payloads between the client and this destination ({{?RFC9110, Section 9.3.6}}).  To date, this is the only mechanism defined for proxying TCP over HTTP.  In this specification, this is referred to as a "classic HTTP CONNECT proxy".

HTTP/3 uses a UDP transport, so it cannot be forwarded using the pre-existing CONNECT mechanism.  To enable forward proxying of HTTP/3, the MASQUE effort has defined proxy mechanisms that are capable of proxying UDP datagrams {{?CONNECT-UDP=RFC9298}}, and more generally IP datagrams {{?CONNECT-IP=RFC9484}}.  The destination host and port number (if applicable) are encoded into the HTTP resource path, and end-to-end datagrams are wrapped into HTTP Datagrams {{?RFC9297}} on the client-proxy path.

## Problems

HTTP clients can be configured to use proxies by selecting a proxy hostname, a port, and whether to use a security protocol. However, Classic HTTP CONNECT requests using the proxy do not carry this configuration information. Instead, they only indicate the hostname and port of the target. This prevents any HTTP server from hosting multiple distinct proxy services, as the server cannot distinguish them by path (as with distinct resources) or by origin (as in "virtual hosting").

The absence of an explicit origin for the proxy also rules out the usual defenses against server port misdirection attacks (see {{Section 7.4 of ?RFC9110}}) and creates ambiguity about the use of origin-scoped response header fields (e.g., "Alt-Svc" {{?RFC7838}}, "Strict-Transport-Security" {{?RFC6797}}).

Classic HTTP CONNECT requests cannot carry in-stream metadata. For example, the WRAP_UP capsule {{?I-D.schinazi-httpbis-wrap-up}} cannot be used with Classic HTTP CONNECT.

## Overview

This specification describes an alternative mechanism for proxying TCP in HTTP.  Like {{?CONNECT-UDP}} and {{?CONNECT-IP}}, the proxy service is identified by a URI Template.  Proxy interactions reuse standard HTTP components and semantics, avoiding changes to the core HTTP protocol.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Specification

A template-driven TCP transport proxy for HTTP is identified by a URI Template {{!RFC6570}} containing variables named "target_host" and "target_port".  This URI Template and its variable values MUST meet all the same requirements as for UDP proxying ({{!RFC9298, Section 2}}), and are subject to the same validation rules.  The client MUST substitute the destination host and port number into this template to produce the request URI.  The derived URI serves as the destination of a Capsule Protocol connection using the Upgrade Token "connect-tcp" (see registration in {{new-upgrade-token}}).

When using "connect-tcp", TCP payload data is sent in the payload of a new Capsule Type named DATA (see registration in {{data-capsule}}).  The ordered concatenation of DATA capsule payloads represents the TCP payload data.

An intermediary MAY merge and split successive DATA capsules, subject to the following requirements:

* There are no intervening capsules of other types.
* The order of payload content is preserved.

## In HTTP/1.1

In HTTP/1.1, the client uses the proxy by issuing a request as follows:

* The method SHALL be "GET".
* The request's target SHALL correspond to the URI derived from expansion of the proxy's URI Template.
* The request SHALL include a single "Host" header field containing the origin of the proxy.
* The request SHALL include a "Connection" header field with the value "Upgrade".  (Note that this requirement is case-insensitive as per {{Section 7.6.1 of !RFC9110}}.)
* The request SHALL include an "Upgrade" header field with the value "connect-tcp".
* The request SHOULD include a "Capsule-Protocol: ?1" header.

If the request is well-formed and permissible, the proxy MUST attempt to establish the TCP connection before sending any response status code other than "100 (Continue)" (see {{conveying-metadata}}).  If the TCP connection is successful, the response SHALL be as follows:

* The HTTP status code SHALL be "101 (Switching Protocols)".
* The response SHALL include a "Connection" header field with the value "Upgrade".
* The response SHALL include a single "Upgrade" header field with the value "connect-tcp".
* The response SHOULD include a "Capsule-Protocol: ?1" header.

If the request is malformed or impermissible, the proxy MUST return a 4XX error code.  If a TCP connection was not established, the proxy MUST NOT switch protocols to "connect-tcp", and the client MAY reuse this connection for additional HTTP requests.

~~~
Client                                                 Proxy

GET /proxy?target_host=192.0.2.1&target_port=443 HTTP/1.1
Host: example.com
Connection: Upgrade
Upgrade: connect-tcp
Capsule-Protocol: ?1

** Proxy establishes a TCP connection to 192.0.2.1:443 **

                            HTTP/1.1 101 Switching Protocols
                            Connection: Upgrade
                            Upgrade: connect-tcp
                            Capsule-Protocol: ?1
~~~
{: title="Templated TCP proxy example in HTTP/1.1"}

## In HTTP/2 and HTTP/3

In HTTP/2 and HTTP/3, the proxy MUST include SETTINGS_ENABLE_CONNECT_PROTOCOL in its SETTINGS frame {{!RFC8441}}{{!RFC9220}}.  The client uses the proxy by issuing an "extended CONNECT" request as follows:

* The :method pseudo-header field SHALL be "CONNECT".
* The :protocol pseudo-header field SHALL be "connect-tcp".
* The :authority pseudo-header field SHALL contain the authority of the proxy.
* The :path and :scheme pseudo-header fields SHALL contain the path and scheme of the request URI derived from the proxy's URI Template.

A templated TCP proxying request that does not conform to all of these requirements represents a client error (see {{!RFC9110, Section 15.5}}) and may be malformed (see {{Section 8.1.1 of !RFC9113}} and {{Section 4.1.2 of !RFC9114}}).

~~~
HEADERS
:method = CONNECT
:scheme = https
:authority = request-proxy.example
:path = /proxy?target_host=2001%3Adb8%3A%3A1&target_port=443
:protocol = connect-tcp
capsule-protocol = ?1
...
~~~
{: title="Templated TCP proxy example in HTTP/2"}

## Use of Other Relevant Headers

### Origin-scoped Headers

Ordinary HTTP headers apply only to the single resource identified in the request or response.  An origin-scoped HTTP header is a special response header that is intended to change the client's behavior for subsequent requests to any resource on this origin.

Unlike classic HTTP CONNECT proxies, a templated TCP proxy has an unambiguous origin of its own.  Origin-scoped headers apply to this origin when they are associated with a templated TCP proxy response.  Here are some origin-scoped headers that could potentially be sent by a templated TCP proxy:

* "Alt-Svc" {{?RFC7838}}
* "Strict-Transport-Security" {{?RFC6797}}
* "Public-Key-Pins" {{?RFC7469}}
* "Accept-CH" {{?RFC8942}}
* "Set-Cookie" {{?RFC6265}}, which has configurable scope.
* "Clear-Site-Data" {{CLEAR-SITE-DATA}}

### Authentication Headers

Authentication to a templated TCP proxy normally uses ordinary HTTP authentication via the "401 (Unauthorized)" response code, the "WWW-Authenticate" response header field, and the "Authorization" request header field ({{!RFC9110, Section 11.6}}).  A templated TCP proxy does not use the "407 (Proxy Authentication Required)" response code and related header fields ({{?RFC9110, Section 11.7}}) because they do not traverse HTTP gateways (see {{operational-considerations}}).

Clients SHOULD assume that all proxy resources generated by a single template share a protection space (i.e., a realm) ({{?RFC9110, Section 11.5}}).  For many authentication schemes, this will allow the client to avoid waiting for a "401 (Unauthorized)" response before each new connection through the proxy.

## Closing Connections

In each HTTP version, any requirements related to closing connections in Classic HTTP CONNECT also apply to "connect-tcp", with the following modifications:

* In HTTP/1.1, endpoints SHOULD close the connection in an error state to indicate receipt of a TCP connection error (e.g., a TCP RST or timeout).  Acceptable error states include sending an incomplete DATA capsule (as defined in {{Section 3.3 of !RFC9297}}), a TLS Error Alert ({{!RFC8446, Section 6.2}}), or a TCP RST (if TLS is not in use).  When a connection is terminated in an error state, the receiving endpoint SHOULD send a TCP RST if the underlying TCP implementation permits it.
* In HTTP/2 and HTTP/3, senders MAY use an incomplete DATA capsule to indicate a TCP connection error, instead of (or in addition to) the signals defined for TCP connection errors in Classic HTTP CONNECT.  Recipients MUST recognize any incomplete capsule as a TCP connection error.
* Intermediaries MUST propagate connection shutdown errors, including when translating between different HTTP versions.

# Additional Connection Setup Behaviors

This section discusses some behaviors that are permitted or recommended in order to enhance the performance or functionality of connection setup.

## Latency optimizations

When using this specification in HTTP/2 or HTTP/3, clients MAY start sending TCP stream content optimistically, subject to flow control limits ({{Section 5.2 of !RFC9113}} or {{Section 4.1 of !RFC9000}}).  Proxies MUST buffer this "optimistic" content until the TCP stream becomes writable, and discard it if the TCP connection fails.  (Clients MUST NOT use "optimistic" behavior in HTTP/1.1, as this would interfere with reuse of the connection after an error response such as "401 (Unauthorized)".)

Servers that host a proxy under this specification MAY offer support for TLS early data in accordance with {{!RFC8470}}.  Clients MAY send "connect-tcp" requests in early data, and MAY include "optimistic" TCP content in early data (in HTTP/2 and HTTP/3).  At the TLS layer, proxies MAY ignore, reject, or accept the `early_data` extension ({{!RFC8446, Section 4.2.10}}).  At the HTTP layer, proxies MAY process the request immediately, return a "425 (Too Early)" response ({{!RFC8470, Section 5.2}}), or delay some or all processing of the request until the handshake completes.  For example, a proxy with limited anti-replay defenses might choose to perform DNS resolution of the `target_host` when a request arrives in early data, but delay the TCP connection until the TLS handshake completes.

## Conveying metadata

This specification supports the "Expect: 100-continue" request header ({{?RFC9110, Section 10.1.1}}) in any HTTP version.  The "100 (Continue)" status code confirms receipt of a request at the proxy without waiting for the proxy-destination TCP handshake to succeed or fail.  This might be particularly helpful when the destination host is not responding, as TCP handshakes can hang for several minutes before failing.  Clients MAY send "Expect: 100-continue", and proxies MUST respect it by returning "100 (Continue)" if the request is not immediately rejected.

Proxies implementing this specification SHOULD include a "Proxy-Status" response header {{!RFC9209}} in any success or failure response (i.e., status codes 101, 2XX, 4XX, or 5XX) to support advanced client behaviors and diagnostics.  In HTTP/2 or HTTP/3, proxies MAY additionally send a "Proxy-Status" trailer in the event of an unclean shutdown.

# Applicability

## Servers

For server operators, template-driven TCP proxies are particularly valuable in situations where virtual-hosting is needed, or where multiple proxies must share an origin.  For example, the proxy might benefit from sharing an HTTP gateway that provides DDoS defense, performs request sanitization, or enforces user authorization.

The URI template can also be structured to generate high-entropy Capability URLs {{CAPABILITY}}, so that only authorized users can discover the proxy service.

## Clients

Clients that support both classic HTTP CONNECT proxies and template-driven TCP proxies MAY accept both types via a single configuration string.  If the configuration string can be parsed as a URI Template containing the required variables, it is a template-driven TCP proxy.  Otherwise, it is presumed to represent a classic HTTP CONNECT proxy.

In some cases, it is valuable to allow "connect-tcp" clients to reach "connect-tcp"-only proxies when using a legacy configuration method that cannot convey a URI Template.  To support this arrangement, clients SHOULD treat certain errors during classic HTTP CONNECT as indications that the proxy might only support "connect-tcp":

* In HTTP/1.1: the response status code is "426 (Upgrade Required)", with an "Upgrade: connect-tcp" response header.
* In any HTTP version: the response status code is "501 (Not Implemented)".
  - Requires SETTINGS_ENABLE_CONNECT_PROTOCOL to have been negotiated in HTTP/2 or HTTP/3.

If the client infers that classic HTTP CONNECT is not supported, it SHOULD retry the request using the registered default template for "connect-tcp":

~~~
https://$PROXY_HOST:$PROXY_PORT/.well-known/masque
                 /tcp/{target_host}/{target_port}/
~~~
{: title="Registered default template"}

If this request succeeds, the client SHOULD record a preference for "connect-tcp" to avoid further retry delays.

# Security Considerations

Template-driven TCP proxying is largely subject to the same security risks as classic HTTP CONNECT.  For example, any restrictions on authorized use of the proxy (see {{?RFC9110, Section 9.3.6}}) apply equally to both.

A small additional risk is posed by the use of a URI Template parser on the client side.  The template input string could be crafted to exploit any vulnerabilities in the parser implementation.  Client implementers should apply their usual precautions for code that processes untrusted inputs.

# Operational Considerations

Templated TCP proxies can make use of standard HTTP gateways and path-routing to ease implementation and allow use of shared infrastructure.  However, current gateways might need modifications to support TCP proxy services.  To be compatible, a gateway must:

* support Extended CONNECT (if acting as an HTTP/2 or HTTP/3 server).
* support HTTP/1.1 Upgrade to "connect-tcp" (if acting as an HTTP/1.1 server)
  - only after forwarding the upgrade request to the origin and observing a success response.
* forward the "connect-tcp" protocol to the origin.
* convert "connect-tcp" requests between all supported HTTP server and client versions.
* allow any "Proxy-Status" headers to traverse the gateway.

# IANA Considerations

## New Upgrade Token

IF APPROVED, IANA is requested to add the following entry to the HTTP Upgrade Token Registry:

| Value | Description | Reference |
| ----- | ----------- | --------- |
| "connect-tcp" | Proxying of TCP payloads | (This document) |

For interoperability testing of this draft version, implementations SHALL use the value "connect-tcp-07".

## New MASQUE Default Template {#iana-template}

IF APPROVED, IANA is requested to add the following entry to the "MASQUE URI Suffixes" registry:

| ------------ | ------------ | --------------- |
| Path Segment | Description  | Reference       |
| tcp          | TCP Proxying | (This document) |

## New Capsule Type {#data-capsule}

IF APPROVED, IANA is requested to add the following entry to the "HTTP Capsule Types" registry:

| ----- | ------------ | --------- | ---------------------------------- | ----------------- | ------- |
| Value | Capsule Type | Status    | Reference                          | Change Controller | Contact |
| (TBD) | DATA         | permanent | (This document), {{specification}} | IETF              | HTTPBIS |

For this draft version of the protocol, the Capsule Type value `0x2028d7ee` shall be used provisionally for testing, under the name "DATA-07".

--- back

# Acknowledgments
{:numbered="false"}

Thanks to Amos Jeffries, Tommy Pauly, Kyle Nekritz, David Schinazi, and Kazuho Oku for close review and suggested changes.
