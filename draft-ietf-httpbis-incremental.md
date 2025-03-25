---
title: "Incremental HTTP Messages"
docname: draft-ietf-httpbis-incremental-latest
category: std
wg: httpbis
ipr: trust200902
keyword: internet-draft
stand_alone: yes
pi: [toc, sortrefs, symrefs]
author:
 -
    fullname:
      :: 奥 一穂
      ascii: Kazuho Oku
    org: Fastly
    email: kazuhooku@gmail.com
 -
    fullname: Tommy Pauly
    organization: Apple
    email: tpauly@apple.com
 -
    fullname: Martin Thomson
    organization: Mozilla
    email: mt@lowentropy.net

normative:

informative:
  PROXY-STATUS: RFC9209
  SSE:
    target: https://html.spec.whatwg.org/multipage/server-sent-events.html
    title: Server-Sent Events
    author:
     -
        org: WHATWG



--- abstract

This document specifies the "Incremental" HTTP header field, which instructs
HTTP intermediaries to forward the HTTP message incrementally.


--- middle

# Introduction

HTTP {{!HTTP=RFC9110}} permits receivers to begin processing portions of HTTP
messages as they arrive, rather than requiring them to wait for the entire HTTP
message to be received before acting.

Some applications are specifically designed to take advantage of this
capability.

For example, Server-Sent Events {{SSE}} uses a long-running HTTP response, where
the server continually sends notifications as they become available.

In the case of Chunked Oblivious HTTP Messages
{{?CHUNKED-OHTTP=I-D.ietf-ohai-chunked-ohttp}}, the client opens an HTTP request
and incrementally sends application messages, while the server can start responding
even before the HTTP request is fully complete. In this way, the HTTP
request-response pair effectively serves as a bi-directional communication
channel.

However, these applications are fragile when HTTP intermediaries are involved.
This is because HTTP intermediaries are not only permitted but are frequently
deployed to buffer complete HTTP messages before forwarding them downstream
({{Section 7.6 of HTTP}}).

If such a buffering HTTP intermediary exists between the client and the server,
these applications may fail to function as intended.

In the case of Server-Sent Events, when an intermediary tries to buffer the HTTP
response completely before forwarding it, the client might time out before
receiving any portion of the HTTP response.

In the case of Chunked Oblivious HTTP Messages, when an intermediary tries to
buffer the entire HTTP request, the client will not start receiving application
messages from the server until the client closes the request, effectively
disrupting the intended incremental processing of the request.

To help avoid such behavior, this document specifies the "Incremental" HTTP header
field, which instructs HTTP intermediaries to begin forwarding the HTTP message
downstream before receiving the complete message.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

The term Boolean is imported from {{!STRUCTURED-FIELDS=RFC8941}}.


# The Incremental Header Field

The Incremental HTTP header field expresses the sender's intent for HTTP
intermediaries to start forwarding the message downstream before the entire
message is received.

This header field has just one valid value of type Boolean: "?1".

~~~
Incremental = ?1
~~~

Upon receiving a header section that includes the Incremental header field, HTTP
intermediaries SHOULD NOT buffer the entire message before forwarding it.
Instead, intermediaries SHOULD transmit the header section downstream and
continuously forward the bytes of the message body as they arrive.

The Incremental HTTP header field applies to each HTTP message. Therefore, if
both the HTTP request and response need to be forwarded incrementally, the
Incremental HTTP header field MUST be set for both the HTTP request and the
response.

The Incremental field is advisory. Intermediaries that are unaware of the field
or that do not support the field might buffer messages, even when explicitly
requested otherwise.  Clients and servers therefore cannot expect all
intermediaries to understand and respect a request to deliver messages
incrementally. Clients can rely on prior knowledge or probe for support on
individual resources.

# Security Considerations

## Applying Concurrency Limits

To conserve resources required to handle HTTP requests or connections, it is
common for intermediaries to impose limits on the maximum number of concurrent
HTTP requests that they forward, while buffering requests that exceed this
limit.

Such intermediaries could apply a more restrictive concurrency limit to requests
marked as incremental to ensure that capacity remains available for
non-incremental requests, even when the maximum number of incremental requests
is reached. This approach helps balance the processing of different types of
requests and maintains service availability across all requests.

When rejecting incremental requests due to reaching the concurrency limit,
intermediaries SHOULD respond with a 503 Service Unavailable error, accompanied
by a connection_limit_reached Proxy-Status response header field
({{Section 2.3.12 of PROXY-STATUS}}).


# IANA Considerations

The Incremental HTTP header field is added to the "HTTP Field Name" registry established in
{{Section 18.4 of HTTP}}:

Field Name:
: Incremental

Status:
: permanent

Structured Type:
: Boolean

Reference:
: This document

Comments:
: None
{: spacing="compact"}


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
