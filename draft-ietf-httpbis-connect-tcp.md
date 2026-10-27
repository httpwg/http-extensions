---
title: "Template-Driven HTTP CONNECT Proxying for TCP"
abbrev: "Templated CONNECT-TCP"
category: std

docname: draft-ietf-httpbis-connect-tcp-latest
ipr: trust200902
area: wit
submissiontype: IETF
workgroup: httpbis

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

author:
 -
    name: Benjamin M. Schwartz
    organization: Meta Platforms, Inc.
    email: ietf@bemasc.net

normative:
  RFC9110:
    display: HTTP
  RFC9112:
    display: HTTP/1.1
  RFC9113:
    display: HTTP/2
  RFC9114:
    display: HTTP/3
informative:
  CAPABILITY:
    title: Good Practices for Capability URLs
    date: 18 February 2014
    target: https://www.w3.org/TR/capability-urls/
  CLEAR-SITE-DATA:
    title: Clear Site Data
    date: 30 November 2017
    target: https://www.w3.org/TR/clear-site-data/
  SYSCTL:
    title: IP Sysctl -- The Linux Kernel documentation
    date: 14 June 2026
    target: https://www.kernel.org/doc/html/v7.1/networking/ip-sysctl.html

--- abstract

TCP tunneling using HTTP CONNECT has long been part of the core HTTP specification.  However, this tunneling functionality has several important deficiencies due to the lack of a well-defined HTTP origin or path.  This specification defines an alternative HTTP proxy service configuration for TCP connections.  This configuration is described by a URI Template, similar to the CONNECT-UDP and CONNECT-IP protocols.

--- middle

# Introduction

## History

HTTP has used the CONNECT method for tunneling TCP connections since HTTP/1.1.  When using CONNECT, the request target specifies a host and port number, and the proxy forwards TCP payloads between the client and the target destination ({{!RFC9110, Section 9.3.6}}). To date, this is the only mechanism defined for proxying TCP over HTTP.  In this specification, this is referred to as a "classic HTTP CONNECT proxy".

HTTP/3 {{!RFC9114}} uses a UDP transport, so it cannot be forwarded using the pre-existing CONNECT mechanism.  To enable forward proxying of HTTP/3, the MASQUE effort has defined proxy mechanisms that are capable of tunneling UDP datagrams {{!CONNECT-UDP=RFC9298}}, and more generally IP datagrams {{?CONNECT-IP=RFC9484}}.  The destination host and port number (if applicable) are encoded into the HTTP resource path, and end-to-end datagrams are wrapped into HTTP Datagrams {{CAPSULE}} on the client-proxy path.

## Problems

HTTP clients can be configured to use proxies by selecting a proxy hostname, a port number, and whether to use a security protocol. However, classic HTTP CONNECT requests using the proxy do not carry this configuration information. Instead, they only indicate the hostname and port of the target. This prevents any HTTP server from hosting multiple distinct proxy services, as the server cannot distinguish them by path (as with distinct resources) or by origin (as in "virtual hosting").

The absence of an explicit origin for the proxy also rules out the usual defenses against server port misdirection attacks (see {{Section 7.4 of !RFC9110}}) and creates ambiguity about the use of origin-scoped response header fields (e.g., "Alt-Svc" {{?ALT-SVC=RFC7838}} or "Strict-Transport-Security" {{?HSTS=RFC6797}}).

Classic HTTP CONNECT requests are not extensible to carry in-stream metadata. For example, the WRAP_UP capsule {{?I-D.ietf-httpbis-wrap-up}} cannot be used with classic HTTP CONNECT.

## Overview

This specification describes an alternative mechanism for tunneling TCP in HTTP.  Like {{?CONNECT-UDP}} and {{?CONNECT-IP}}, the proxy service is identified by a URI Template.  Proxy interactions reuse standard HTTP components and semantics, avoiding changes to the core HTTP protocol.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

In this document, the term "proxy" refers to the HTTP server that acts upon a client's TCP tunneling request. If there are HTTP intermediaries (as defined in Section 3.7 of [HTTP]) between the client and the proxy, those are referred to as "intermediaries" or "gateways" in this document.

The term "endpoint" describes an implementation of this specification in either client or proxy role.

The term "templated TCP proxy" refers to a proxy that is identified by a URI Template in accordance with this specification.

# Specification

A template-driven TCP transport proxy for HTTP is identified by a URI Template {{!RFC6570}} containing variables named "target_host" and "target_port".  This URI Template and its variable values MUST meet all the same requirements as for UDP proxying ({{!CONNECT-UDP, Section 2}}), and are subject to the same validation rules.  Clients MUST substitute the destination host and port number into this template to produce a request URI.  The derived URI serves as the destination of a Capsule Protocol connection using the Upgrade Token "connect-tcp" (see registration in {{new-upgrade-token}}).

When using "connect-tcp", TCP payload data is sent in the payload of new Capsule Types named DATA and FINAL_DATA (see {{fig-capsules}} and registrations in {{data-capsule}}).  The ordered concatenation of these capsule payloads, which MAY be empty, represents the TCP payload data.  A FINAL_DATA capsule additionally indicates that the sender has closed this stream, semantically equivalent to TCP FIN.  After sending a FINAL_DATA capsule, an endpoint MUST NOT send any more DATA or FINAL_DATA capsules on this data stream. See {{closing-connections}} for related requirements.

~~~
DATA Capsule {
  Type (i) = 0x08,
  Length (i),  # may be zero
  TCP Payload (..),
}

FINAL_DATA Capsule {
  Type (i) = 0x09,
  Length (i),  # may be zero
  TCP Payload (..),
}
~~~
{: #fig-capsules title="DATA and FINAL_DATA Capsule Formats"}

The boundaries between DATA and FINAL_DATA capsules are not significant, and are not expected to match TCP segments, TLS records, HTTP DATA frames, QUIC STREAM frames, etc.  Recipients SHOULD begin forwarding payload from a DATA or FINAL_DATA capsule without waiting to receive the entire capsule, especially if the capsule is large.

An intermediary MAY merge and split successive DATA and FINAL_DATA capsules, subject to the following requirements:

* There are no intervening capsules of other types.
* The order of payload content is preserved.
* The final emitted capsule uses the same capsule type (DATA or FINAL_DATA) as the final input capsule, and all others use the DATA capsule type.

For example, an intermediary holding two successive DATA capsules in its transmission buffer could merge them, saving at least 2 bytes of encapsulation overhead when they are forwarded.

This protocol supports backward-compatible extensions via additional Capsule Types, as described in {{Section 3.2 of !CAPSULE=RFC9297}}.

## In HTTP/1.1

In HTTP/1.1 {{RFC9112}}, the client uses the proxy by issuing a request as follows:

* The method SHALL be "GET".
* The request's target SHALL correspond to the URI derived from expansion of the proxy's URI Template.
* The request SHALL include a single "Host" header field whose value identifies the proxy.
* The request SHALL include a "Connection" header field with the value "Upgrade".  (Note that this requirement is case-insensitive as per {{Section 7.6.1 of !RFC9110}}.)
* The request SHALL include an "Upgrade" header field with the value "connect-tcp".
* The request SHOULD include a "Capsule-Protocol: ?1" header (as recommended in {{CAPSULE, Section 3.4}}).

If the request is well-formed and permissible, the proxy MUST attempt to establish the TCP connection before sending any response status code other than "100 (Continue)" (see {{conveying-metadata}}).  If the TCP connection is successful, the response SHALL be as follows:

* The HTTP status code SHALL be "101 (Switching Protocols)".
* The response SHALL include a "Connection" header field with the value "Upgrade".
* The response SHALL include a single "Upgrade" header field with the value "connect-tcp".
* The response SHOULD include a "Capsule-Protocol: ?1" header (as above).

If a TCP connection was not established, the proxy MUST NOT switch protocols to "connect-tcp", and the client MAY reuse this connection for additional HTTP requests.

~~~
Client                                                 Proxy

GET /proxy?target_host=192.0.2.1&target_port=443 HTTP/1.1
Host: example.com
Connection: Upgrade
Upgrade: connect-tcp
Capsule-Protocol: ?1

                            HTTP/1.1 100 Continue

** Proxy establishes a TCP connection to 192.0.2.1:443 **

                            HTTP/1.1 101 Switching Protocols
                            Connection: Upgrade
                            Upgrade: connect-tcp
                            Capsule-Protocol: ?1
                            Proxy-Status: example.com
~~~
{: title="Templated TCP proxy example in HTTP/1.1"}

## In HTTP/2 and HTTP/3

In HTTP/2 and HTTP/3, the proxy MUST include SETTINGS_ENABLE_CONNECT_PROTOCOL in its SETTINGS frame {{!RFC8441}}{{!RFC9220}}.  The client uses the proxy by issuing an "extended CONNECT" request as follows:

* The :method pseudo-header field SHALL be "CONNECT".
* The :protocol pseudo-header field SHALL be "connect-tcp".
* The :authority pseudo-header field SHALL contain the authority of the proxy.
* The :path and :scheme pseudo-header fields SHALL contain the path and scheme of the request URI derived from the proxy's URI Template.

A templated TCP proxying request that does not conform to all of these requirements represents a client error (see {{!RFC9110, Section 15.5}}) and may be malformed (see {{Section 8.1.1 of !RFC9113}} and {{Section 4.1.2 of !RFC9114}}).

Additionally, the "capsule-protocol" header field SHOULD be present with a value of "?1" (as recommended in {{CAPSULE, Section 3.4}}).

~~~
HEADERS
:method = CONNECT
:scheme = https
:authority = templated-proxy.example
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

* "Alt-Svc" {{ALT-SVC}}
* "Strict-Transport-Security" {{HSTS}}
* "Accept-CH" {{?RFC8942}}
* "Set-Cookie" {{?RFC6265}}, which has configurable scope.
* "Clear-Site-Data" {{CLEAR-SITE-DATA}}

### Authentication Headers

Authentication to a templated TCP proxy normally uses ordinary HTTP authentication via the "401 (Unauthorized)" response code, the "WWW-Authenticate" response header field, and the "Authorization" request header field ({{!RFC9110, Section 11.6}}).  A templated TCP proxy does not use the "407 (Proxy Authentication Required)" response code and related header fields ({{?RFC9110, Section 11.7}}) because they do not traverse HTTP gateways (see {{gateway-compatibility}}).

Clients SHOULD assume that all proxy resources generated by a single template share a protection space (i.e., a realm) ({{!RFC9110, Section 11.5}}).  For many authentication schemes, this will allow the client to avoid waiting for a "401 (Unauthorized)" response before each new connection through the proxy.

TLS Client Certificate authentication can also be used (see {{gateway-compatibility}}).

### Caching Headers

In HTTP/2 and HTTP/3, this specification uses the CONNECT method, which is not subject to caching ({{?RFC9110, Section 9.3.6}}).  However, in HTTP/1.1, the method is GET, which in other usages can be cacheable.  To minimize discrepancies between HTTP versions, the following requirements apply when using HTTP/1.1:

* If the response has a heuristically cacheable status code ({{!RFC9110, Section 15.1}}), it SHOULD also carry a `Cache-Control: no-store` header field.
  - This can occur if the request is rejected or the connection fails.
* The proxy SHOULD NOT attach any other caching-related header fields to the response.

## Closing Connections

Connection termination is essentially symmetrical for proxies and their clients, which we refer to here as the "endpoints" of a request.

When closing connections, endpoints are subject to the following requirements:

* When an endpoint receives a valid TCP FIN, it MUST send a FINAL_DATA capsule.
* When an endpoint receives a valid FINAL_DATA capsule, it MUST send a TCP FIN.
* When a TCP connection reaches the TIME-WAIT or CLOSED state, the associated endpoint MUST close its send stream.
  - If the connection closed gracefully, the endpoint MUST close the send stream gracefully.
  - Otherwise, the endpoint SHOULD close the send stream abruptly, using a mechanism appropriate to the HTTP version:
    - HTTP/3: reset the stream with H3_CONNECT_ERROR; see {{!QUIC=RFC9000, Section 19.4}} and {{?RFC9114, Section 8.1}}.
    - HTTP/2: reset the stream with CONNECT_ERROR; see {{!RFC9113}}, Sections 6.4 and 7.
    - HTTP/1.1 over TLS: TCP shutdown without a TLS closure alert; see {{!TLS=RFC9846, Section 6.1}}.
    - HTTP/1.1 without TLS: TCP RST.
* When the receive stream is closed abruptly or without a FINAL_DATA capsule received, the endpoint SHOULD send a TCP RST if the TCP subsystem permits it.

Any locally imposed timeout ({{timeouts}}) MUST be treated as an abrupt closure of the affected stream or connection.

The mandatory behaviors above enable endpoints to detect any truncation of incoming TCP data.  The recommended behaviors propagate any TCP errors through the tunnel.

In HTTP/3, endpoints MAY negotiate and use the RESET_STREAM_AT frame in order to reduce data loss during an abrupt closure {{?I-D.ietf-quic-reliable-stream-reset}}.  However, RESET_STREAM_AT may not be very effective in this case, as TCP implementations will typically discard pending data when a RST is received.

~~~ aasvg
+-------+    +------------+     +------------+    +-------+
| TCP A |    | Endpoint A |     | Endpoint B |    | TCP B |
+-+-----+    +-+----------+     +----------+-+    +-----+-+
  +---"abc"--->+--------DATA{"abc"}------->+---"abc"--->|
  +----FIN---->+------FINAL_DATA{""}------>+----FIN---->|
  |<---FIN-----+<-----FINAL_DATA{""}-------+<---FIN-----+
  |            |<----QUIC.STREAM{FIN}------+            |
  +---FINACK-->+-----QUIC.STREAM{FIN}----->|            |
  |            |                           |            |
~~~
{: title="Simple graceful termination example (HTTP/3)"}

~~~ aasvg
+-------+    +------------+     +------------+    +-------+
| TCP A |    | Endpoint A |     | Endpoint B |    | TCP B |
+-+-----+    +-+----------+     +----------+-+    +-----+-+
  +----RST---->+----RST_STREAM{CON_ERR}--->+----RST---->|
  |            |                           |            |
~~~
{: title="Simple TCP RST termination example (HTTP/2)"}

~~~ aasvg
+-------+    +------------+     +------------+    +-------+
| TCP A |    | Endpoint A |     | Endpoint B |    | TCP B |
+-+-----+    +-+----------+     +----------+-+    +-----+-+
  +---"abc"--->+--------DATA{"abc"}------->+---"abc"--->|
  |            |   (... timeout @ A ...)   |            |
  |            +--FIN (no close_notify) -->+----RST---->|
  |            |                           |            |
~~~
{: title="Timeout example (HTTP/1.1)"}

~~~ aasvg
+-------+    +------------+     +------------+    +-------+
| TCP A |    | Endpoint A |     | Endpoint B |    | TCP B |
+-+-----+    +-+----------+     +----------+-+    +-----+-+
  +-----FIN--->+-------FINAL_DATA{""}----->+-----FIN--->|
  |            |                           |            |
  |    (FIN)   |                           |    (FIN)   |
  |<---"abc"---+<----FINAL_DATA{"abc"}-----+<---"abc"---+
  |            |<----QUIC.STREAM{FIN}------+            |
  +-----RST--->+-----H3_CONNECT_ERROR----->+-----RST--->|
  |            |                           |            |
~~~
{: title="RST after FIN example (HTTP/3)"}

### Handling Invalid Data

An endpoint that receives invalid data from its peer is subject to the same requirements as when receiving an abrupt closure of the receive stream (see {{closing-connections}}).  Some examples of invalid data include:

 * A second FINAL_DATA capsule.
 * A DATA capsule after FINAL_DATA.
 * Data that results in a parsing error under the Capsule Protocol.
 * A capsule that is truncated by the end of the stream.
 * A capsule that would require unreasonable effort to process.

Note that very large DATA and FINAL_DATA capsules are still valid, as they can be forwarded incrementally using a bounded memory buffer.

# Additional Connection Setup Behaviors

This section discusses some behaviors that are permitted or recommended in order to enhance the performance or functionality of connection setup.

## Latency optimizations

When using this specification in HTTP/2 or HTTP/3, clients MAY start sending TCP stream content optimistically, subject to flow control limits ({{Section 5.2 of !RFC9113}} or {{Section 4.1 of !QUIC}}).  Proxies MUST buffer this "optimistic" content until the TCP stream becomes writable, and discard it if the TCP connection fails.  (Clients MUST NOT use "optimistic" behavior in HTTP/1.1, as this would interfere with reuse of the connection after an error response such as "401 (Unauthorized)".)

Servers that host a proxy under this specification MAY offer support for TLS early data in accordance with {{!RFC8470}}.  Clients MAY send "connect-tcp" requests in early data, and MAY include "optimistic" TCP content in early data (in HTTP/2 and HTTP/3).  At the TLS layer, proxies MAY ignore, reject, or accept the `early_data` extension ({{TLS, Section 4.3.10}}).  At the HTTP layer, proxies MAY process the request immediately, return a "425 (Too Early)" response ({{!RFC8470, Section 5.2}}), or delay some or all processing of the request until the handshake completes.  For example, a proxy with limited anti-replay defenses might choose to perform DNS resolution of the `target_host` when a request arrives in early data, but delay the TCP connection until the TLS handshake completes.

When DNS resolution of `target_host` produces multiple IP addresses, proxies SHOULD use a racing procedure such as Happy Eyeballs {{?HEv2=RFC8305}} to accelerate connection establishment.  Proxies that race multiple connection attempts MUST buffer any optimistic content until a connection is selected and MUST NOT transmit any payload data on the other connections.

## Indicating Failure

Failure to initiate a tunnel is indicated by the HTTP response status code.

A 4XX status code indicates the the request is malformed or impermissible.  For example, if the proxy performs DNS resolution of `target_host` and receives an IP address that is disallowed by the proxy's policy, it might return 403 (Forbidden).

A 5XX status code indicates a failure in the attempt, such as when a TCP connection was attempted but did not succeed.  The 502 (Bad Gateway) and 504 (Gateway Timeout) status codes are commonly used.

The 429 (Too Many Requests) and 503 (Service Unavailable) status codes indicate a temporary failure, and can carry a "Retry-After" response header field.  If included, this field applies to all requests using this URI Template.

## Conveying metadata

This specification supports the "100 (Continue)" response status code ({{?RFC9110, Section 15.2.1}}) in any HTTP version.  Proxies SHOULD send this status code whenever they accept a request, without waiting for the proxy-destination TCP handshake to succeed or fail.  This allows for a few useful improvements:

* Clients can provide a clearer status indication while waiting for the destination host to respond.  (TCP handshakes can hang for several minutes before failing.)
* Clients can apply separate timeouts to the tunneling request and connection establishment.
* In HTTP/2 and HTTP/3, clients have the option to delay some or all of the optimistic payload data until after confirming that the request is permissible.  This strategy reduces wasted effort when the request is rejected.

Note that a client in this specification cannot send an "Expect: 100-continue" request header field, because the request does not include any "content" ({{?RFC9110, Section 10.1.1}}).

Proxies implementing this specification SHOULD include a "Proxy-Status" response header field {{!PROXY-STATUS=RFC9209}} in any success or failure response (i.e., status codes 101, 2XX, 4XX, or 5XX) to support advanced client behaviors and diagnostics.  Clients and proxies MUST NOT send trailer fields on "connect-tcp" streams.

# Applicability

## Servers

For server operators, templated TCP proxies are particularly valuable in situations where virtual-hosting is needed, or where multiple proxies must share an origin.  For example, the proxy might benefit from sharing an HTTP gateway that provides DDoS defense, performs request sanitization, or enforces user authorization ({{gateway-compatibility}}).

Templated TCP proxies can also be made invisible to probes from unauthorized clients:

* The URI template can include a high-entropy path, similar to Capability URLs {{CAPABILITY}}.
* The proxy can require HTTP Concealed Authentication ({{?CONCEALED=RFC9729, Section 6.4}}).

## Clients

This specification does not require any specific type of configuration input.  Suitable configuration input types include:

* A URI Template string, as described in {{specification}}.
* An IP address or hostname, with optional or required port and scheme (as often used to describe classic HTTP CONNECT proxies).  A corresponding templated TCP proxy might be found in two ways:
  - At the default template for "connect-tcp" ({{fig-default}}).
  - In the "proxy" dictionary of a provisioning domain resource at the corresponding .well-known URI ({{?I-D.ietf-intarea-proxy-config, Section 2}}).
* A provisioning domain resource, configured directly or identified by a local or remote URI (e.g., using "file://" or "https://").

~~~
https://$PROXY_HOST:$PROXY_PORT/.well-known/masque
                 /tcp/{target_host}/{target_port}/
~~~
{: #fig-default title="Registered default template"}

All of these input types MAY share a single input string, as they can be disambiguated reliably by parsing and probing.  However, it may be preferable to indicate the configuration input type explicitly, to reduce probing delays while supporting clients with differing capabilities.

Clients SHOULD treat certain errors during classic HTTP CONNECT as indications that the proxy might only support "connect-tcp":

* In HTTP/1.1: the response status code is "426 (Upgrade Required)", with an "Upgrade: connect-tcp" response header.
* In any HTTP version: the response status code is "501 (Not Implemented)".
  - Requires SETTINGS_ENABLE_CONNECT_PROTOCOL to have been negotiated in HTTP/2 or HTTP/3.

If the client infers that classic HTTP CONNECT is not supported, it SHOULD retry the request using the registered default template for "connect-tcp" ({{fig-default}}).  If this request succeeds, the client SHOULD record a preference for "connect-tcp" to avoid further retry delays.

## Gateways {#gateway-compatibility}

Templated TCP proxy requests can traverse standard HTTP gateways to ease implementation and allow use of shared infrastructure.  However, current gateways might need modifications to support TCP proxy services.  To be compatible, a gateway MUST:

* support Extended CONNECT (if acting as an HTTP/2 or HTTP/3 server).
* support HTTP/1.1 Upgrade to "connect-tcp" (if acting as an HTTP/1.1 server)
  - only after forwarding the upgrade request to the origin and observing a success response.
* forward the "connect-tcp" protocol to the origin.
* convert "connect-tcp" requests between all supported HTTP server and client versions.
* allow any "Proxy-Status" headers to traverse the gateway.

If the proxy relies on TLS Client Certificates for client authentication, the gateway MUST perform this authentication itself or pass the relevant information to the origin (e.g., using a "Client-Cert" request header field {{?RFC9440}}).

# Security Considerations

Template-driven TCP proxying is largely subject to the same security risks as classic HTTP CONNECT.  For example, any restrictions on authorized use of the proxy (see {{?RFC9110, Section 9.3.6}}) apply equally to both.  The `destination_ip_prohibited` Proxy Error Type from {{Section 2.3.5 of PROXY-STATUS}} can be useful when rejecting unauthorized requests.

A small additional risk is posed by the use of a URI Template parser on the client side.  The template input string could be crafted to exploit any vulnerabilities in the parser implementation.  Client implementers should apply their usual precautions for code that processes untrusted inputs.

See {{Section 7 of CONNECT-UDP}} for a comparison of the risks of operating a TCP or UDP proxy.

## Resource Exhaustion attacks {#resource-exhaustion}

A malicious client can cause highly asymmetric resource usage at the proxy by colluding with a destination server and violating the ordinary rules of TCP or HTTP.  Some example attacks, and mitigations that proxies can apply:

* **Connection Pileup**: A malicious client can attempt to open a large number of connections to exhaust the proxy's memory, port, or file descriptor limits. When using HTTP/2 or HTTP/3, each incremental TCP connection imposes a much higher cost on the proxy than on the attacker.
  - Mitigation: Limit the number of concurrent connections per client.
* **Window Bloat**: An attacker can grow the receive window size by simulating a "long, fat network" ({{?RFC7323, Section 1.1}}), then fill the window (from the sender) and stop acknowledging it (at the receiver).  This leaves the proxy buffering up to 1 GiB of TCP data until some timeout, while the attacker does not have to retain a large buffer.
  - Mitigation: Limit the maximum receive window for TCP and HTTP connections, and the size of userspace buffers used for forwarding data.  Alternatively, monitor the connections' send queues and limit the total buffered data per client.
* **WAIT Abuse**: An attacker can force the proxy into a TIME-WAIT, CLOSE-WAIT, or FIN-WAIT state until the timer expires, tying up a proxy-to-destination 4-tuple for up to four minutes after the client's connection is closed.
  - Mitigations:
    * Enable the PAWS optimization ({{?RFC7323, Section 5}}) across successive connections (e.g., Linux's `tcp_tw_reuse=1` {{SYSCTL}}).  This makes TIME-WAIT 4-tuples rapidly reusable if the destination enables TCP Timestamps, which most do.
    * Allocate a large range of IP addresses for TCP connections (especially in IPv6).
    * Limit the number of connections for each client to each destination, even if those connections are in a waiting state and the corresponding CONNECT stream is closed.
    * If necessary, perform an abrupt TCP closure that destroys the Transmission Control Block.  Note that reusing a 4-tuple in this way can increase the risk of interference between successive connections.

# Operational Considerations

## Avoiding HTTP/1.1

While this specification is fully functional under HTTP/1.1, performance-sensitive deployments SHOULD use HTTP/2 or HTTP/3 instead.  When using HTTP/1.1:

* Each CONNECT request requires a new TCP and TLS connection, imposing a higher cost in setup latency, congestion control convergence, CPU time, and data transfer.
* The graceful and abrupt closure signals ({{closing-connections}}) are more likely to be missing or corrupted:
  - Some implementations may be unable to emit the recommended abrupt closure signals, due to limitations in their TCP and TLS subsystems.
  - Faulty implementations may fail to send a TLS closure alert during graceful shutdown, or fail to report an error when the expected closure alert is not received.  These misbehaviors are not compliant with {{TLS}}, but they are common nonetheless among HTTP/1.1 implementations today.
* The number of active connections through each client may be limited by the number of available TCP client ports, especially if:
  - The client only has one IP address that can be used to reach the proxy.
  - The client is shared between many parties, such as when acting as a gateway or concentrator.
  - The tunneled connections are often closed by the destination. This causes the client to initiate closure of the client-to-proxy connection, leaving the client in a TIME-WAIT state for up to four minutes.

## Timeouts

Except when actively sending or receiving data, an endpoint is always waiting for an event from its peer or its TCP connection.  HTTP and TCP are designed to ensure that such an event always arrives, so the connection is never permanently stuck in any state until it is fully closed.  However, for efficient operation, it may be necessary to adjust the settings for TCP keep-alives ({{!TCP=RFC9293, Section 3.8.4}}), QUIC idle timeouts ({{?QUIC, Section 10.1}}), HTTP/2 PING frames ({{?RFC9113, Section 6.7}}), and other transport options.

Endpoints MAY impose additional timeouts, especially as a defense against certain resource exhaustion attacks ({{resource-exhaustion}}).  However, operators should apply timeouts cautiously to minimize the impact on connections that are functioning but slow.   See {{closing-connections}} for related requirements.

For example, enabling PING frames on idle HTTP/2 connections allows the operator to prevent some kinds of failures and detect failed connections faster, but it uses more bandwidth, CPU time, and radio power, and increases the risk of false-positive connection failures.  Optimal transport settings will depend on the network environment (e.g., mobile vs. fixed), characteristics of the tunneled application, and many other considerations.

## Scope of Packet-Level Metadata

This specification does not provide a way to pass packet-level metadata such as IPv6 Extension Headers {{?RFC2460, Section 4}}, DiffServ Codepoints (DSCP) {{?RFC2474}}, or Explicit Congestion Notification (ECN) marks {{?RFC3168}} through the tunnel.  TCP options and non-fatal ICMP messages (e.g., Packet Too Big) are similarly not relayed.  Instead, these signals are processed by the relevant endpoint of this specification, which is also the TCP endpoint and only relays payload data through the tunnel.

Consumption and generation of these signals on each connection is controlled by the endpoint, and is independent from any behaviors of the other endpoint and any similar signals on the tunnel's HTTP connection.  If the operator has requirements related to these behaviors, it must configure the relevant endpoint (typically the proxy) accordingly.

## IP address sharing

A TCP proxy typically uses the same IP address to establish connections on behalf of multiple clients, especially in IPv4. {{?RFC6269}} provides guidance regarding difficulties that can arise from IP address sharing, including in this arrangement.

# IANA Considerations

## New Upgrade Token

IANA is requested to add the following entry to the "HTTP Upgrade Tokens" registry under "Hypertext Transfer Protocol (HTTP) Upgrade Token Registry" registry group:

| Value | Description | Expected Version Tokens | Reference |
| ----- | ----------- | ----------------------- | --------- |
| "connect-tcp" | Proxying of TCP payloads | (None) |(This document) |

### Interop testing
{:removeInRFC="true"}

For interoperability testing of this draft version, implementations SHALL use the value "connect-tcp-12".

## New MASQUE Default Template {#iana-template}

IANA is requested to add the following entry to the "MASQUE URI Suffixes" registry under "Multiplexed Application Substrate over QUIC Encryption (MASQUE)" registry group:

| ------------ | ------------ | --------------- |
| Path Segment | Description  | Reference       |
| tcp          | TCP Proxying | (This document) |

## New Capsule Type {#data-capsule}

IANA is requested to add the following entry to the "HTTP Capsule Types" registry under "Multiplexed Application Substrate over QUIC Encryption (MASQUE)" registry group:

| ------ | ------------ | --------- | ---------------------------------- | ----------------- | ------- |
| Value  | Capsule Type | Status    | Reference                          | Change Controller | Contact |
| 0x08   | DATA         | permanent | (This document), {{specification}} | IETF              | HTTPBIS |
| 0x09   | FINAL_DATA   | permanent | (This document), {{specification}} | IETF              | HTTPBIS |

--- back

# Acknowledgments
{:numbered="false"}

This document benefited from close review and suggested changes by:

* Mohamed Boucadair
* Gorry Fairhurst
* Thomas Fossati
* Amos Jeffries
* Antun Jurkovic
* Eric Kinnear
* Kyle Nekritz
* Kazuho Oku
* Tommy Pauly
* Yaroslav Romakho
* David Schinazi
* Ketan Talaulikar
* Willy Tarreau
