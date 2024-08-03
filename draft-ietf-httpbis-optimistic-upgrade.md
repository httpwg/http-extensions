---
title: "Security Considerations for Optimistic Use of HTTP Upgrade"
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

The HTTP/1.1 Upgrade mechanism allows the client to request a change to a new protocol.  This document discusses the security considerations that apply to data sent by the client before this request is confirmed, and updates RFC 9298 to avoid related security issues.


--- middle

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Background {#background}

In HTTP/1.1, a client is permitted to send an "Upgrade" request header field ({{!RFC9110, Section 7.8}}) to indicate that it would like to use this connection for a protocol other than HTTP/1.1.  The server replies with a "101 (Switching Protocols)" status code if it accepts the protocol change.  However, that specification also permits the server to reject the upgrade request:

> A server MAY ignore a received Upgrade header field if it wishes to continue using the current protocol on that connection.

This rejection of the upgrade is common, and can happen for a variety of reasons:

* The server does not support any of the client's indicated Upgrade Tokens (i.e., the client's proposed new protocols), so it continues to use HTTP/1.1.
* The server knows that an upgrade to the offered protocol will not provide any improvement over HTTP/1.1 for this request to this resource, so it chooses to respond in HTTP/1.1.
* The server requires the client to authenticate before upgrading the protocol, so it replies with the status code "401 (Authentication Required)" and provides a challenge in an "Authorization" response header ({{!RFC9110, Section 11.6.2}}).
* The resource has moved, so the server replies with a 3XX redirect status code ({{!RFC9110, Section 3.4}}).

After rejecting the upgrade, the server will continue to interpret subsequent bytes on that connection in accordance with HTTP/1.1.

{{!RFC9110}} also states:

> A client cannot begin using an upgraded protocol on the connection until it has completely sent the request message (i.e., the client can't change the protocol it is sending in the middle of a message).

However, because of the possibility of rejection, the converse is not true: a client cannot necessarily begin using an upgraded protocol merely because it has finished sending the upgrade request message.

In some cases, the client might expect that the upgrade will succeed.  If this expectation is correct, the client might be able to reduce delay by immediately sending the first bytes of the upgraded protocol "optimistically", without waiting for the server's response.  This document explores the security implications of this "optimistic" behavior.

# Possible Security Issues

When there are only two distinct parties involved in an HTTP/1.1 connection (i.e., the client and the server), HTTP Upgrade introduces no new security issues: each party must already be prepared for the other to send arbitrary data on the connection at any time.  However, HTTP connections often involve more than two parties, if the requests or responses include third-party data.  For example, a browser (party 1) might send an HTTP request to an origin (party 2) with path, headers, or body controlled by a website from a different origin (party 3).  Post-upgrade protocols such as WebSocket similarly are often used to convey data chosen by a third party.

If the third-party data source is untrusted, we call the data it provides "attacker-controlled".  The combination of attacker-controlled data and optimistic HTTP Upgrade results in two significant security issues.

## Request Smuggling

In a Request Smuggling attack ({{?RFC9112, Section 11.2}}) the attacker-controlled data is chosen in such a way that it is interpreted by the server as an additional HTTP request.  These attacks allow the attacker to speak on behalf of the client while bypassing the client's own rules about what requests it will issue.  Request Smuggling can occur if the client and server have distinct interpretations of the data that flows between them.

If the server accepts an HTTP Upgrade, it interprets the subsequent bytes in accordance with the new protocol.  If it rejects the upgrade, it interprets those bytes as HTTP/1.1.  However, the client doesn't know which interpretation the server will take until it receives the server's response status code.  If it uses the new protocol optimistically, this creates a risk that the server will interpret attacker-controlled data in the upgraded protocol as an additional HTTP request issued by the client.

As a trivial example, consider an upgraded protocol in which the entire post-upgrade content might be freely attacker-controlled (e.g., "connect-tcp" {{?I-D.ietf-httpbis-connect-tcp}}).  If the client is authenticated to the server using a connection-level authentication method such as TLS Client Certificates, the attacker could send an HTTP/1.1 POST request in the post-upgrade payload.  If the client delivers this payload optimistically, and the upgrade request fails, the server would interpret the payload as a subsequent authenticated request issued by the client.

## Parser Exploits

A related category of attacks use protocol disagreement to exploit vulnerabilities in the server's request parsing logic.  These attacks apply when the HTTP client is trusted by the server, but the post-upgrade data source is not.  If the server software was developed under the assumption that some or all of the HTTP request data is not attacker-controlled, optimistic use of HTTP Upgrade can cause this assumption to be violated, exposing vulnerabilities in the server's HTTP request parser.

# Operational Issues

If the server rejects the upgrade, the connection can continue to be used for HTTP/1.1.  There is no requirement to close the connection in response to an upgrade rejection, and keeping the connection open has performance advantages if additional HTTP requests to this server are likely.  Thus, it is normally inappropriate to close the connection in response to a rejected upgrade.

# Impact on Existing Upgrade Tokens {#existing}

At the time of writing, there are four distinct Upgrade Tokens that are registered, associated with published documents, and not marked obsolete.  This section considers the impact of this document's considerations on each registered Upgrade Token.

## "HTTP"

{{!RFC9110}} is the source of the requirement quoted in {{background}}.  It also defines the "HTTP/\*.\*" family of Upgrade Tokens.  In HTTP/1.1, the only potentially applicable versions of this token are "0.9", "1.0", "1.1", and "2.0".

Versions "0.9" and "1.0" are sufficiently syntactically similar to HTTP/1.1 that any such "downward upgrade" would be unlikely to result in the security concerns discussed here.  (An "upgrade" to version 1.1 has no effect at all.)

A version number of "2.0" corresponds to HTTP/2.  Every HTTP/2 connection begins with a Client Connection Preface ({{Section 3.4 of ?RFC9113}}) that was selected to ensure that a compliant HTTP/1.1 server will not process further data on this connection.  This avoids security issues if an "HTTP/2.0" Upgrade Token is used optimistically.

## "TLS"

{{?RFC2817}} defines the "TLS/*.*" family of Upgrade Tokens, and correctly highlights the possibility of the server rejecting the upgrade.  The security considerations documented here are applicable to any use of the "TLS" Upgrade Token, but no change is required in {{?RFC2817}}.

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

There are now several good examples of designs that prevent the security concerns discussed in this document and may be applicable in future specifications:

* Forbid optimistic use of HTTP Upgrade (WebSocket, {{Section 4.1 of ?RFC6455}}).
* Embed a fixed preamble that terminates HTTP/1.1 processing (HTTP/2, {{Section 3.4 of ?RFC9113}}).
* Apply high-entropy masking of client-to-server data (WebSocket, {{Section 5.1 of ?RFC6455}}).

Future specifications for Upgrade Tokens MUST account for the security issues discussed here and provide clear guidance on how clients can avoid them.

## Selection of Request Methods with Upgrade

<!-- If #2845 is merged, change this to:
Some Upgrade Tokens, such as "TLS", are defined for use with any ordinary HTTP Method.  The upgraded protocol continues to provide HTTP semantics, and will convey the response to this HTTP request.

The other Upgrade Tokens mentioned in {{existing}} do not preserve HTTP semantics, so the method is not relevant.  All of these Upgrade Tokens are specified only for use with the "GET" method.
-->

The "HTTP" and "TLS" Upgrade Tokens can be used with any ordinary HTTP Method.  The upgraded protocol continues to provide HTTP semantics, and will convey the response to this HTTP request.

The other Upgrade Tokens presently defined do not preserve HTTP semantics, so the method is not relevant.  All of these Upgrade Tokens are specified only for use with the "GET" method.

Future specifications for Upgrade Tokens should restrict their use to "GET" requests if the HTTP method is otherwise irrelevant and a request body is not required.  This improves consistency with other Upgrade Tokens and avoids the possibility that a faulty server implementation might process the request body as the new protocol.

# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

Thanks to Mark Nottingham and Lucas Pardue for early reviews of this document.
