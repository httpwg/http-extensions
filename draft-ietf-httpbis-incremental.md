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
  PREFER: RFC7240

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


# The Signalling Scheme

This specification defines two HTTP header fields that allow endpoints to
signal their preference regarding the incremental delivery of HTTP requests or
responses.


## The Incremental Header Field

The Incremental HTTP header field expresses the sender's intent for HTTP
intermediaries to begin forwarding the message downstream before the entire
message has been received.

This header field has a single valid value of type Boolean: "?1".

~~~
Incremental = ?1
~~~

The Incremental header field applies individually to each HTTP message. Thus,
setting the Incremental header field on an HTTP request affects only how the
request is forwarded. For responses to be delivered incrementally, servers
SHOULD set the Incremental header field on the responses they generate.


## The Prefer: incremental Header Field

In addition to the server-driven `Incremental` signal, clients may request
incremental delivery of responses by including the `incremental` preference
within the HTTP `Prefer` request header field ({{Section 2 of PREFER}}).

~~~
Prefer: incremental
~~~

This client-driven preference is particularly useful for responses whose
incremental usage may not be readily determinable by the server. It also
provides intermediaries an opportunity to immediately reject requests if they
are unable or unwilling to deliver responses incrementally.


# Intermediary Behavior

When forwarding HTTP messages marked for incremental delivery (either by clients
or servers), intermediaries SHOULD NOT buffer the entire message. Instead, they
SHOULD forward the header section downsteram promptly, followed by incremental
transmisson of the message body as bytes become available.

If incremental delivery is impossible, intermediaries SHOULD respond with a 503
Service Unavailable error. If generating such an error response is not possible,
intermediaries SHOULD reset the underlying stream. This allows clients to
quickly detect failure rather than waiting for a timeout.

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

TBD

--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
