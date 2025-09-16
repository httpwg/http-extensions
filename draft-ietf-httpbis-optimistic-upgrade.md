---
title: "Security Considerations for Optimistic Protocol Transitions in HTTP/1.1"
abbrev: "Optimistic HTTP Upgrade Security"
category: std

docname: draft-ietf-httpbis-optimistic-upgrade-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: "Web and Internet Transport"
workgroup: "HTTPBIS"
keyword:
venue:
  github: "httpwg/http-extensions"
updates: 9112, 9298

author:
 -
    fullname: Benjamin M. Schwartz
    organization: Meta Platforms, Inc.
    email: ietf@bemasc.net

normative:
  RFC9112:
    display: HTTP/1.1
informative:
  RFC9113:
    display: HTTP/2
  RFC9114:
    display: HTTP/3
  IANA-UPGR:
    title: Hypertext Transfer Protocol (HTTP) Upgrade Token Registry
    target: https://www.iana.org/assignments/http-upgrade-tokens/
    author:
      org: IANA


--- abstract

In HTTP/1.1, the client can request a change to a new protocol on the existing connection.  This document discusses the security considerations that apply to data sent by the client before this request is confirmed, and adds new requirements to RFC 9112 and RFC 9298 to avoid related security issues.


--- middle

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Overview

This document discusses certain security considerations that arise when switching from HTTP/1.1 to a different protocol on the same connection.  It provides:

* A review of the relevant standards.
* A discussion of the security risks that may apply if a client sends data before the transition is confirmed.
* Security evaluation of existing upgrade tokens.
* Guidance for implementations and future standards documents.

Updates to RFC 9112 and RFC 9298, including new normative requirements, are provided in {{connect}} and {{connect-udp}}.

# Background {#background}

In HTTP/1.1 {{RFC9112}} and later, a single connection can be used for many requests.  In HTTP/2 {{RFC9113}} and HTTP/3 {{RFC9114}}, these requests can be multiplexed, as each request is distinguished explicitly by its stream ID.  However, in HTTP/1.1, requests are strictly sequential, and each new request is distinguished implicitly by the closure of the preceding request.

HTTP/1.1 is also the only version of HTTP that allows the client to change the protocol used for the remainder of the connection.  There are two mechanisms to request such a protocol transition.  One mechanism is the Upgrade request header field ({{!HTTP=RFC9110, Section 7.8}}), which indicates that the client would like to use this connection for a protocol other than HTTP/1.1.  The server replies with a 101 (Switching Protocols) status code if it accepts the protocol change ({{HTTP, Section 15.2.2}}).

The other mechanism is the HTTP CONNECT method ({{Section 9.3.6 of HTTP}}).  This method indicates that the client wishes to establish a TCP connection to the specified host and port.  If accepted, the server replies with a 2xx (Successful) response to indicate that the request was accepted and a TCP connection was established.  After this point, the TCP connection is acting as a TCP tunnel, not an HTTP/1.1 connection.

Both of these mechanisms also permit the server to reject the request.  For example, {{HTTP}} says:

> A server MAY ignore a received Upgrade header field if it wishes to continue using the current protocol on that connection.
{:quote quotedFrom="HTTP, Section 7.8" cite="https://www.rfc-editor.org/rfc/rfc9110.html#section-7.8-2"}

and

> A server MUST reject a CONNECT request that targets an empty or invalid port number, typically by responding with a 400 (Bad Request) status code.
{:quote quotedFrom="HTTP, Section 9.3.6" cite="https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.6-4"}

Rejected upgrades are common and can happen for a variety of reasons, such as:

* The server does not support any of the client's indicated upgrade tokens (i.e., the client's proposed new protocols), so it continues to use HTTP/1.1.
* The server knows that an upgrade to the offered protocol will not provide any improvement over HTTP/1.1 for this request to this resource, so it chooses to respond in HTTP/1.1.
* The server requires the client to authenticate before upgrading the protocol, so it replies with the status code 401 (Authentication Required) and provides a challenge in an Authorization response header field ({{!HTTP, Section 11.6.2}}).
* The resource has moved, so the server replies with a 3xx (Redirection) status code ({{!HTTP, Section 3.4}}).

Similarly, servers frequently reject HTTP CONNECT requests, such as when:

* The server does not support HTTP CONNECT.
* The specified destination is not allowed under server policy.
* The destination cannot be resolved, is unreachable, or does not accept the connection.
* The proxy requires the client to authenticate before proceeding.

After rejecting a request, the server will continue to interpret bytes received on that connection in accordance with HTTP/1.1.

{{!HTTP}} also states:

> A client cannot begin using an upgraded protocol on the connection until it has completely sent the request message (i.e., the client can't change the protocol it is sending in the middle of a message).
{:quote quotedFrom="HTTP, Section 7.8" cite="https://www.rfc-editor.org/rfc/rfc9110.html#section-7.8-15"}

In other words, completion of the request message is a **necessary** condition for the client to begin using the new protocol.  However, it is important to clarify that this is not a **sufficient** condition, because the server might reject the request.

In some cases, the client might predict that the server is likely to accept a requested protocol transition.  For example, if a request using an upgrade token recently succeeded, the client might expect that subsequent requests with the same upgrade token will also succeed.  If this expectation is correct, the client can often reduce delay by immediately sending the first bytes of the new protocol "optimistically", without waiting for the server's response.  This document explores the security implications of this "optimistic" behavior.

# Possible Security Issues

When there are only two distinct parties involved in an HTTP/1.1 connection (i.e., the client and the server), protocol transitions introduce no new security issues: each party must already be prepared for the other to send arbitrary data on the connection at any time.  However, HTTP connections often involve more than two parties, if the requests or responses include third-party data.  For example, a browser (party 1) might send an HTTP request to an origin (party 2) with path, headers, or content controlled by a website from a different origin (party 3).  Post-transition protocols such as WebSocket {{?WEBSOCKET=RFC6455}} similarly are often used to convey data chosen by a third party.

If the third-party data source is untrusted, then the data it provides is potentially "attacker-controlled".  The combination of attacker-controlled data and optimistic protocol transitions results in two significant security issues.

## Request Smuggling

In a Request Smuggling attack ({{RFC9112, Section 11.2}}) the attacker-controlled data is chosen in such a way that it is interpreted by the server as an additional HTTP request.  These attacks allow the attacker to speak on behalf of the client while bypassing the client's own rules about what requests it will issue.  Request Smuggling can occur if the client and server have distinct interpretations of the data that flows between them.

If the server accepts a protocol transition request, it interprets the subsequent bytes in accordance with the new protocol.  If it rejects the request, it interprets those bytes as HTTP/1.1.  However, the client cannot know which interpretation the server will take until it receives the server's response status code.  If it uses the new protocol optimistically, this creates a risk that the server will interpret attacker-controlled data in the new protocol as an additional HTTP request issued by the client.

As a trivial example, consider an HTTP CONNECT client providing connectivity to an untrusted application.  If the client is authenticated to the proxy server using a connection-level authentication method such as TLS Client Certificates ({{?TLS=RFC8446, Section 4.4.2}}), the attacker could send an HTTP/1.1 POST request ({{HTTP, Section 9.3.3}}) for the proxy server at the beginning of its TCP connection.  If the client delivers this data optimistically, and the CONNECT request fails, the server would misinterpret the application's data as a subsequent authenticated request issued by the client.

~~~
## REQUESTS ##

# The malicious application requests a TCP connection to a nonexistent
# destination, which will fail.
CONNECT no-such-destination.example:443 HTTP/1.1
Host: no-such-destination.example:443

# Before connection fails, the malicious application sends data on the
# proxied TCP connection that forms a valid POST request to the proxy.
# The vulnerable client optimistically forwards this data to the proxy.
POST /upload HTTP/1.1
Host: proxy.example
Content-Length: 123456

<POST body controlled by the malicious application>

## RESPONSES ##

# When TCP connection establishment fails, the proxy responds by
# rejecting the CONNECT request, but the client has already forwarded
# the malicious TCP payload data to the proxy.
HTTP/1.1 504 Gateway Timeout
Content-Length: 0

# The proxy interprets the smuggled POST request as coming from the
# client.  If connection-based authentication is in use (e.g., using
# TLS client certificate authentication), the proxy treats this
# malicious request as authenticated.
HTTP/1.1 200 OK
Content-Length: 0

~~~
{:figure title="Example request smuggling attack using HTTP CONNECT"}

## Parser Exploits

A related category of attacks use protocol disagreement to exploit vulnerabilities in the server's request parsing logic.  These attacks apply when the HTTP client is trusted by the server, but the post-transition data source is not.  If the server software was developed under the assumption that some or all of the HTTP request data is not attacker-controlled, optimistic transmission can cause this assumption to be violated, exposing vulnerabilities in the server's HTTP request parser.

# Operational Issues

If the server rejects the transition request, the connection can continue to be used for HTTP/1.1.  There is no general requirement to close the connection in response to a rejected transition, and keeping the connection open has performance advantages if additional HTTP requests to this server are likely.  Thus, it is normally inappropriate to close the connection in response to a rejected transition.

# Impact on HTTP Upgrade with Existing Upgrade Tokens {#existing}

This section describes the impact of this document's considerations on some registered upgrade tokens {{IANA-UPGR}} that are believed to be in use at the time of writing.

## "TLS"

The "TLS" family of upgrade tokens was defined in {{?RFC2817}}, which correctly highlights the possibility of the server rejecting the upgrade. If a client ignores this possibility and sends TLS data optimistically, the result cannot be valid HTTP/1.1: the first octet of a TLS connection must be 22 (ContentType.handshake), but this is not an allowed character in an HTTP/1.1 method (see {{TLS, Section 5.1}} and {{RFC9112, Section 3}}).  A compliant HTTP/1.1 server will treat this as a parsing error and close the connection without processing further requests.

## "WebSocket"/"websocket"

{{Section 4.1 of ?WEBSOCKET}} says:

> Once the client's opening handshake has been sent, the client MUST wait for a response from the server before sending any further data.
{:quote}

Thus, optimistic use of HTTP Upgrade is already forbidden in the WebSocket protocol.  Additionally, the WebSocket protocol requires high-entropy masking of client-to-server frames ({{Section 5.1 of ?WEBSOCKET}}).

## "connect-udp" {#connect-udp}

{{Section 5 of !CONNECT-UDP=RFC9298}} says:

> A client MAY optimistically start sending UDP packets in HTTP Datagrams before receiving the response to its UDP proxying request.
{:quote}

However, in HTTP/1.1, this "proxying request" is an HTTP Upgrade request.  This upgrade is likely to be rejected in certain circumstances, such as when the UDP destination address (which is attacker-controlled) is invalid.  Additionally, the contents of the "connect-udp" protocol stream can include untrusted material (i.e., the UDP packets, which might come from other applications on the client device).  This creates the possibility of Request Smuggling attacks.  To avoid these concerns, this document replaces that text to exclude HTTP/1.1 from any optimistic sending, as follows:

> A client MAY optimistically start sending UDP packets in HTTP Datagrams before receiving the response to its UDP proxying request, but only if the HTTP version in use is HTTP/2 or later. Clients MUST NOT send UDP packets optimistically in HTTP/1.x due to the risk of request smuggling attacks.

## "connect-ip"

The "connect-ip" upgrade token is defined in {{?CONNECT-IP=RFC9484}}.  {{Section 11 of ?CONNECT-IP}} forbids clients from sending packets optimistically in HTTP/1.1, avoiding this issue.

# Guidance for Future Upgrade Tokens

There are now several good examples of designs that reduce or eliminate the security concerns discussed in this document and may be applicable in future specifications:

* Forbid optimistic use of HTTP Upgrade ({{Section 4.1 of ?WEBSOCKET}}, {{Section 11 of ?CONNECT-IP}}).
* Embed a fixed preamble that deliberately terminates HTTP/1.1 processing ({{Section 3.4 of RFC9113}}).
* Apply high-entropy masking of client-to-server data ({{Section 5.1 of ?WEBSOCKET}}).

Future specifications for upgrade tokens should account for the security issues discussed here and provide clear guidance on how implementations can avoid them.

## Selection of Request Methods

Some upgrade tokens, such as "TLS", are defined for use with any ordinary HTTP method.  The upgraded protocol continues to provide HTTP semantics, and will convey the response to this HTTP request.

The other upgrade tokens mentioned in {{existing}} do not preserve HTTP semantics, so the method is not relevant.  All of these upgrade tokens are specified only for GET requests with no content.

Future specifications for upgrade tokens should restrict their use to GET requests with no content if the HTTP method is otherwise irrelevant and the request does not need to carry any message content.  This improves consistency with other upgrade tokens and simplifies server implementation.

# Requirements for HTTP CONNECT {#connect}

This document updates RFC 9112 to include the remaining text of this section.  The requirements in this section apply only to HTTP/1.1.

Proxy clients that send CONNECT requests on behalf of untrusted TCP clients MUST do one or both of the following:

1. Wait for a 2xx (Successful) response before forwarding any TCP payload data.
1. Send a "Connection: close" request header.

Proxy clients that don't implement at least one of these two behaviors are vulnerable to a trivial request smuggling attack ({{RFC9112, Section 11.2}}).

At the time of writing, some proxy clients are believed to be vulnerable as described.  As a mitigation, proxy servers MUST close the underlying connection when rejecting a CONNECT request, without processing any further requests on that connection, unless the client is known to wait for a 2xx (Successful) response before forwarding TCP payload data (i.e., complying with item 1 above).  This requirement applies whether or not the request includes a "close" connection option.  Proxy servers can identify compliant clients using the request's User-Agent header field and the user-agent vendor's documentation regarding its compliance.

Note that this mitigation will frequently impair the performance of correctly implemented clients, especially when returning a 407 (Proxy Authentication Required) response.  This performance loss can be avoided by using HTTP/2 or HTTP/3, which are not vulnerable to this attack.

# Security Considerations

This document describes security considerations related to optimistic use of protocol transitions in HTTP/1.1.

# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

This document benefited from valuable reviews and suggestions by:

* Mike Bishop
* Mohamed Boucadair
* Gorry Fairhurst
* Mark Nottingham
* Kazuho Oku
* Lucas Pardue
* David Schinazi
* Glenn Strauss
* Michael Sweet
* Willy Tarreau
* Martin Thomson
