---
title: The HTTP Wrap Up Capsule
docname: draft-ietf-httpbis-wrap-up-latest
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
  repo: https://github.com/httpwg/http-extensions/labels/wrap-up
  latest: "https://httpwg.org/http-extensions/draft-ietf-httpbis-wrap-up.html"
github-issue-label: wrap-up
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
    fullname: "Lucas Pardue"
    organization: Cloudflare
    email: "lucas@lucaspardue.com"

normative:

informative:
  H1:
    =: RFC9112
    display: HTTP/1.1
  H2:
    =: RFC9113
    display: HTTP/2
  H3:
    =: RFC9114
    display: HTTP/3


--- abstract

HTTP intermediaries sometimes need to terminate long-lived request streams in
order to facilitate load balancing or impose data limits. However, Web browsers
commonly cannot retry failed proxied requests when they cannot ascertain
whether an in-progress request was acted on. To avoid user-visible failures, it
is best for the intermediary to inform the client of upcoming request stream
terminations in advance of the actual termination so that the client can wrap
up existing operations related to that stream and start sending new work to a
different stream or connection. This document specifies a new "WRAP_UP" capsule
that allows a proxy to instruct a client that it should not start new requests
on a tunneled connection, while still allowing it to finish existing requests.

--- middle

# Introduction

{{H1}}, {{H2}} and {{H3}} all have the notion of persistent connections, where
a single connection can carry multiple request and response messages. While it
is expected that the connection persists, there are situations where a client
or server may wish to terminate the connection gracefully.

An HTTP/1.1 connection can be terminated by using a Connection header field
with the close option; see {{Section 9.6 of H1}}. When a connection has
short-lived requests/responses, this mechanism allows timely and non-disruptive
connection termination. However, when requests/responses are longer lived, the
opportunity to use headers happens less frequently (or not at all). There is no
way for client or server to signal a future intent to terminate the connection.
Instead, an abrupt termination, realized via a transport-layer close or reset,
is required, which is potentially disruptive and can lead to truncated content.

HTTP/2 and HTTP/3 support request multiplexing, making header-based connection
lifecycle control impractical. Connection headers are prohibited entirely.
Instead, a shutdown process using the GOAWAY frame is defined (see {{Section
6.8 of H2}} and {{Section 5.2 of H3}}). GOAWAY signals a future intent to
terminate the connection, supporting cases such as scheduled maintenance.
Active requests/responses can continue to run, while new requests need to be
sent on a new HTTP connection. Endpoints that use GOAWAY typically have a grace
period in which requests/responses can run naturally to completion. If they run
longer than the grace period, they are abruptly terminated when the
transport layer is closed or reset, which is potentially disruptive and can
lead to truncated content.

## The Need for a Request Termination Intent Signal

Intermediaries (see {{Section 3.7 of !HTTP=RFC9110}}) can provide a variety of
benefits to HTTP systems, such as load balancing, caching, and privacy
improvements. Deployments of intermediaries also need to be maintained, which
can sometimes require taking intermediaries temporarily offline. For example,
if a gateway has a client HTTP/2 connection and needs to go down for
maintenance, it can send a GOAWAY to stop the client issuing requests that
would be forwarded to the origin.

~~~ aasvg
+--------+      +---------+      +--------+
| Client |      | Gateway |      | Origin |
|        |      |       * |      |      * |
|        +======+ GOAWAY| +~~~~~~+      | |
|      <----------------+               | |
|                         HTTP Responses| |
|      <--------------------------------+ |
|        +======+         +~~~~~~+        |
+--------+  ^   +---------+   ^  +--------+
            |                 |
     TLS --'                   '-- TLS
~~~
{: #diagram-gateway title="Gateway Sends GOAWAY"}

The connection close details described above apply to an intermediary's
upstream and downstream connections. Since a proxy can do request aggregation
or fan out, there is no guarantee of a 1:1 ratio of upstream/downstream. As
such, the lifetimes of these connections are not coupled tightly. For example,
a gateway can terminate a client HTTP/2 connections and map individual requests
to an origin HTTP/1.1 connection pool. If any single origin connection
indicates an intent to close, it doesn't make sense for the gateway to issue a
GOAWAY to the client, or to respond to a client GOAWAY by closing connections
in the pool.

Long-lived requests pose a problem for maintenance, especially for HTTP/2 and
HTTP/3, and even more so for intermediaries. Sometimes they need to terminate
individual request streams in order to facilitate load balancing or impose data
limits, while leaving the connection still active. GOAWAY is not suitable for
this task.

Some applications using HTTP have their own control plane running over HTTP,
that could be used for a graceful termination. For example, WebSockets has
separate control and data frames. The Close frame ({{Section 5.5.1 of
?WEBSOCKET=RFC6455}}) is used for the WebSocket close sequence. However, in the
maintenance scenario, an intermediary that is not WebSocket aware cannot use
the formal sequence. Nor is there any standard for it to signal to the
endpoints to initiate that sequence. Some intermediaries are WebSocket aware,
and in theory could send Close frames. However, there can be other
considerations that prevent this working effectively in real deployments, since
the intermediary is a generic proxy that may invalidate endpoint expectations.

Many long-lived HTTP request types do not have control messages that could
signal an intent to terminate the request. For example, see CONNECT ({{Section
9.3.6 of HTTP}}) or connect-udp ({?CONNECT-UDP=RFC9298}}). In these models, the
client requests that a proxy create a tunnel to a target origin. On success,
the newly established tunnel is used as the underlying transport to then
establish a second HTTP connection directly to the origin. In that situation,
the proxy cannot inspect the contents of the tunnel, nor inject any data into
it; the proxy only sees a single long-lived request. The proxy is responsible
for managing the lifetime of the tunnel, but can only terminate it abortively.
Such abrupt termination can lead to truncated content, which the client cannot
safely request again. This is especially disruptive if the tunnelled HTTP
connection has many active requests. Web browsers, for example, commonly cannot
retry failed proxied requests when they cannot ascertain whether an in-progress
request was acted on.

To avoid user-visible failures, it is best for the proxy to inform the client
of upcoming request stream terminations in advance of the actual termination.
This allows the client to wrap up existing operations related to that stream
and start sending new work to a different stream or connection.

## The WRAP_UP Capsule

~~~ aasvg
+--------+      +---------+      +--------+
| Client |      |  Proxy  |      | Origin |
|        |      |       * |      |      * |
|        +======+WRAP_UP| |      |      | |
|      <----------------+ |      |      | |
|        +~~~~~~~~~~~~~~~~+~~~~~~+      | |
|                         HTTP Responses| |
|      <--------------------------------+ |
|        +~~~~~~+~~~~~~~~~+~~~~~~+        |
|        +======+         |   ^  +        |
+--------+  ^   +---------+   |  +--------+
            |                 |
     TLS --'                   '-- TLS
~~~
{: #diagram-proxy title="Proxy Sends WRAP_UP"}

This document specifies a new "WRAP_UP" capsule (see {{Section 3 of
!HTTP-DGRAM=RFC9297}}), which a server can send on an HTTP Data Stream, to
inform a client that it intends to close the stream.

An HTTP proxy can send a WRAP_UP capsule to instruct a client that it should
not start new requests on a tunneled connection, while still allowing it to
finish existing requests.

## Conventions and Definitions

{::boilerplate bcp14-tagged}

This document uses the terms "connection", "client", and "server" from
{{Section 3.3 of HTTP}} and the terms "intermediary", "proxy", and "gateway"
from {{Section 3.7 of HTTP}}.

# Mechanism

This document defines the "WRAP_UP" capsule (see {{iana}} for the value). The
WRAP_UP capsule allows a proxy to indicate to a client that it wishes to close
the request stream that the capsule was sent on. The WRAP_UP capsule has no
Capsule Value.

## Proxy Behavior

Proxies often know in advance that they will close a request stream. This can
be due to maintenance of the proxy itself, load balancing, or applying data
usage limits on a particular stream. When a proxy has advance notice that it
will soon close a request stream, it MAY send a WRAP_UP capsule to share that
information with the client. This can also be used when the proxy wishes to
release resources associated with a request stream, such as HTTP Datagrams (see
{{Section 2 of HTTP-DGRAM}}) or WebTransport streams (see
{{?WEBTRANSPORT=I-D.ietf-webtrans-http3}}).

## Client Handling

When a client receives a WRAP_UP capsule on a request stream, it SHOULD try to
wrap up its use of that stream. For example, if the stream carried a
connect-udp request and is used as the underlying transport for an HTTP/3
connection, then after receiving a WRAP_UP capsule the client SHOULD NOT send
any new requests on the proxied HTTP/3 connection - but existing in-progress
proxied requests are not affected by the WRAP_UP capsule.

## Minutiae

Clients MUST NOT send the WRAP_UP capsule. If a server receives a WRAP_UP
capsule, it MUST abort the corresponding request stream. Endpoints MUST NOT
send the WRAP_UP capsule with a non-zero Capsule Length. If an endpoint
receives a WRAP_UP capsule with a non-zero Capsule Length, it MUST abort the
corresponding request stream. Proxies MUST NOT send more than one WRAP_UP
capsule on a given stream. If a client receives a second WRAP_UP capsule on a
given request stream, it MUST abort the stream. Endpoints that abort the
request stream due to an unexpected or malformed WRAP_UP capsule MUST follow
the error-handling procedure defined in {{Section 3.3 of HTTP-DGRAM}}.

# Security Considerations

While it might be tempting for clients to implement the WRAP_UP capsule by
treating it as if they had received a GOAWAY inside the encryption of the
end-to-end connection, doing so has security implications. GOAWAY carries
semantics around which requests have been acted on, and those can have security
implications. Since WRAP_UP is sent by a proxy outside of the end-to-end
encryption, it cannot be trusted to ascertain whether any requests were handled
by the origin. Because of this, client implementations can only use receipt of
WRAP_UP as a hint and MUST NOT use it to make determinations on whether any
requests were handled by the origin or not.

# IANA Considerations {#iana}

This document (if approved) will request IANA to add the following entry to the
"HTTP Capsule Types" registry maintained at
<[](https://www.iana.org/assignments/masque)>.

Value:

: 0x272DDA5E (will be changed to a lower value if this document is approved)

Capsule Type:

: WRAP_UP

Status:

: provisional (will be permanent if this document is approved)

Reference:

: This document

Change Controller:

: IETF

Contact:

: ietf-http-wg@w3.org

Notes:

: None
{: spacing="compact" newline="false"}

--- back

# Acknowledgments
{:numbered="false"}

This mechanism was inspired by the GOAWAY frame from HTTP/2.
