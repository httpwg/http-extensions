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
updates: 9298

author:
 -
    fullname: Benjamin M. Schwartz
    organization: Meta Platforms, Inc.
    email: ietf@bemasc.net

normative:

informative:


--- abstract

In HTTP/1.1, the client can request a change to a new protocol on the existing connection.  This document discusses the security considerations that apply to data sent by the client before this request is confirmed, and updates RFC 9298 to avoid related security issues.


--- middle

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Background {#background}

In HTTP/1.1, a single connection is often used for many requests, one after another.  After each request, the connection is returned to its initial state, ready to send more HTTP requests.  However, HTTP/1.1 also contains two mechanisms that allow the client to change the protocol used for the remainder of the connection.

One such mechanism is the "Upgrade" request header field ({{!RFC9110, Section 7.8}}), which indicates that the client would like to use this connection for a protocol other than HTTP/1.1.  The server replies with a "101 (Switching Protocols)" status code if it accepts the protocol change.

The other mechanism is the HTTP "CONNECT" method.  This method indicates that the client wishes to establish a TCP connection to the specified host and port.  The server replies with a 2xx (Successful) response to indicate that the request was accepted and a TCP connection was established.  After this point, the TCP connection is acting as a TCP tunnel, not an HTTP/1.1 connection.

Both of these mechanisms also permit the server to reject the request.  For example, {{RFC9110}} says:

> A server MAY ignore a received Upgrade header field if it wishes to continue using the current protocol on that connection.

and

> A server MUST reject a CONNECT request that targets an empty or invalid port number, typically by responding with a 400 (Bad Request) status code.

Rejections are common, and can happen for a variety of reasons.  An "upgrade" request might be rejected if:

* The server does not support any of the client's indicated Upgrade Tokens (i.e., the client's proposed new protocols), so it continues to use HTTP/1.1.
* The server knows that an upgrade to the offered protocol will not provide any improvement over HTTP/1.1 for this request to this resource, so it chooses to respond in HTTP/1.1.
* The server requires the client to authenticate before upgrading the protocol, so it replies with the status code "401 (Authentication Required)" and provides a challenge in an "Authorization" response header ({{!RFC9110, Section 11.6.2}}).
* The resource has moved, so the server replies with a 3XX redirect status code ({{!RFC9110, Section 3.4}}).

Similarly, a CONNECT request might be rejected if:

* The server does not support HTTP CONNECT.
* The specified destination is not allowed under server policy.
* The destination cannot be resolved, is unreachable, or does not accept the connection.
* The proxy requires the client to authenticate before proceeding.

After rejecting a request, the server will continue to interpret subsequent bytes on that connection in accordance with HTTP/1.1.

{{!RFC9110}} also states:

> A client cannot begin using an upgraded protocol on the connection until it has completely sent the request message (i.e., the client can't change the protocol it is sending in the middle of a message).

However, because of the possibility of rejection, the converse is not true: a client cannot necessarily begin using a new protocol merely because it has finished sending the corresponding request message.

In some cases, the client might expect that the protocol transition will succeed.  If this expectation is correct, the client might be able to reduce delay by immediately sending the first bytes of the new protocol "optimistically", without waiting for the server's response.  This document explores the security implications of this "optimistic" behavior.

# Possible Security Issues

When there are only two distinct parties involved in an HTTP/1.1 connection (i.e., the client and the server), protocol transitions introduce no new security issues: each party must already be prepared for the other to send arbitrary data on the connection at any time.  However, HTTP connections often involve more than two parties, if the requests or responses include third-party data.  For example, a browser (party 1) might send an HTTP request to an origin (party 2) with path, headers, or body controlled by a website from a different origin (party 3).  Post-transition protocols such as WebSocket similarly are often used to convey data chosen by a third party.

If the third-party data source is untrusted, we call the data it provides "attacker-controlled".  The combination of attacker-controlled data and optimistic protocol transitions results in two significant security issues.

## Request Smuggling

In a Request Smuggling attack ({{?RFC9112, Section 11.2}}) the attacker-controlled data is chosen in such a way that it is interpreted by the server as an additional HTTP request.  These attacks allow the attacker to speak on behalf of the client while bypassing the client's own rules about what requests it will issue.  Request Smuggling can occur if the client and server have distinct interpretations of the data that flows between them.

If the server accepts a protocol transition request, it interprets the subsequent bytes in accordance with the new protocol.  If it rejects the request, it interprets those bytes as HTTP/1.1.  However, the client doesn't know which interpretation the server will take until it receives the server's response status code.  If it uses the new protocol optimistically, this creates a risk that the server will interpret attacker-controlled data in the new protocol as an additional HTTP request issued by the client.

As a trivial example, consider an HTTP CONNECT client providing connectivity to an untrusted application.  If the client is authenticated to the proxy server using a connection-level authentication method such as TLS Client Certificates, the attacker could send an HTTP/1.1 POST request for the proxy server at the beginning of its TCP connection.  If the client delivers this data optimistically, and the CONNECT request fails, the server would misinterpret the application's data as a subsequent authenticated request issued by the client.

## Parser Exploits

A related category of attacks use protocol disagreement to exploit vulnerabilities in the server's request parsing logic.  These attacks apply when the HTTP client is trusted by the server, but the post-transition data source is not.  If the server software was developed under the assumption that some or all of the HTTP request data is not attacker-controlled, optimistic transmission can cause this assumption to be violated, exposing vulnerabilities in the server's HTTP request parser.

# Operational Issues

If the server rejects the transition request, the connection can continue to be used for HTTP/1.1.  There is no requirement to close the connection in response to a rejected transition, and keeping the connection open has performance advantages if additional HTTP requests to this server are likely.  Thus, it is normally inappropriate to close the connection in response to a rejected transition.

# Impact on HTTP Upgrade with Existing Upgrade Tokens {#existing}

This section describes the impact of this document's considerations on some registered Upgrade Tokens that are believed to be in use at the time of writing.

## "TLS"

The "TLS" family of Upgrade Tokens was defined in {{?RFC2817}}, which correctly highlights the possibility of the server rejecting the upgrade. If a client ignores this possibility and sends TLS data optimistically, the result cannot be valid HTTP/1.1: the first octet of a TLS connection must be 22 (ContentType.handshake), but this is not an allowed character in an HTTP/1.1 method.  A compliant HTTP/1.1 server will treat this as a parsing error and close the connection without processing further requests.

## "WebSocket"/"websocket"

{{Section 4.1 of ?RFC6455}} says:

> Once the client's opening handshake has been sent, the client MUST wait for a response from the server before sending any further data.

Thus, optimistic use of HTTP Upgrade is already forbidden in the WebSocket protocol.  Additionally, the WebSocket protocol requires high-entropy masking of client-to-server frames ({{Section 5.1 of ?RFC6455}}).

## "connect-udp"

{{Section 5 of !RFC9298}} says:

> A client MAY optimistically start sending UDP packets in HTTP Datagrams before receiving the response to its UDP proxying request.

However, in HTTP/1.1, this "proxying request" is an HTTP Upgrade request.  This upgrade is likely to be rejected in certain circumstances, such as when the UDP destination address (which is attacker-controlled) is invalid.  Additionally, the contents of the "connect-udp" protocol stream can include untrusted material (i.e., the UDP packets, which might come from other applications on the client device).  This creates the possibility of Request Smuggling attacks.  To avoid these concerns, this text is updated as follows:

> When using HTTP/2 or later, a client MAY optimistically ...

{{Section 3.3 of !RFC9298}} describes the requirement for a successful proxy setup response, including upgrading to the "connect-udp" protocol, and says:

> If any of these requirements are not met, the client MUST treat this proxying attempt as failed and abort the connection.

However, this could be interpreted as an instruction to abort the underlying TLS and TCP connections in the event of an unsuccessful response such as "407 ("Proxy Authentication Required)".  To avoid an unnecessary delay in this case, this text is hereby updated as follows:

> If any of these requirements are not met, the client MUST treat this proxying attempt as failed.  If the "Upgrade" response header field is absent, the client MAY reuse the connection for further HTTP/1.1 requests; otherwise it MUST abort the underlying connection.

## "connect-ip"

The "connect-ip" Upgrade Token is defined in {{!RFC9484}}.  {{Section 11 of !RFC9484}} forbids clients from using optimistic upgrade, avoiding this issue.

# Guidance for Future Upgrade Tokens

There are now several good examples of designs that reduce or eliminate the security concerns discussed in this document and may be applicable in future specifications:

* Forbid optimistic use of HTTP Upgrade (WebSocket, {{Section 4.1 of ?RFC6455}}).
* Embed a fixed preamble that terminates HTTP/1.1 processing (HTTP/2, {{Section 3.4 of ?RFC9113}}).
* Apply high-entropy masking of client-to-server data (WebSocket, {{Section 5.1 of ?RFC6455}}).

Future specifications for Upgrade Tokens should account for the security issues discussed here and provide clear guidance on how implementations can avoid them.

## Selection of Request Methods

Some Upgrade Tokens, such as "TLS", are defined for use with any ordinary HTTP Method.  The upgraded protocol continues to provide HTTP semantics, and will convey the response to this HTTP request.

The other Upgrade Tokens mentioned in {{existing}} do not preserve HTTP semantics, so the method is not relevant.  All of these Upgrade Tokens are specified only for use with the "GET" method.

Future specifications for Upgrade Tokens should restrict their use to "GET" requests if the HTTP method is otherwise irrelevant and a request body is not required.  This improves consistency with other Upgrade Tokens and reduces the likelihood that a faulty server implementation might process the request body as the new protocol.

# Guidance for HTTP CONNECT

Clients that send HTTP CONNECT requests on behalf of untrusted TCP clients MUST wait for a 2xx (Successful) response before sending any TCP payload data.

To mitigate vulnerabilities from any clients that do not conform to this requirement, proxy servers MAY close the underlying connection when rejecting an HTTP CONNECT request, without processing any further data sent to the proxy server on that connection.  Note that this behavior may impair performance, especially when returning a "407 (Proxy Authentication Required)" response.

# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

Thanks to Mark Nottingham and Lucas Pardue for early reviews of this document.
