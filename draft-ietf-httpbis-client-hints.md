---
title: HTTP Client Hints
abbrev:
docname: draft-ietf-httpbis-client-hints-latest
date: {DATE}
category: exp

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft
keyword: client hints
keyword: conneg
keyword: Content Negotiation

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, subcompact, comments, inline]

author:
 -
    ins: I. Grigorik
    name: Ilya Grigorik
    organization: Google
    email: ilya@igvita.com
    uri: https://www.igvita.com/

normative:
  RFC5234:
  RFC7230:
  RFC7231:
  RFC7234:
  RFC6454:
  HTML5: W3C.REC-html5-20141028
  CSSVAL: W3C.CR-css-values-3-20160929
  CSS2:
    target: http://www.w3.org/TR/2011/REC-CSS2-20110607
    title: "Cascading Style Sheets Level 2 Revision 1 (CSS 2.1) Specification"
    date: 2011-06
    author:
    -
      ins: B. Bos
    -
      ins: T. Celic
    -
      ins: I. Hickson
    -
      ins: H. W. Lie
    seriesinfo:
      "W3C Recommendation": REC-CSS2-20110607

informative:
  RFC6265:
  KEY: I-D.ietf-httpbis-key

--- abstract

HTTP defines proactive content negotiation to allow servers to select the appropriate response for a given request, based upon the user agent's characteristics, as expressed in request headers. In practice, clients are often unwilling to send those request headers, because it is not clear whether they will be used, and sending them impacts both performance and privacy.

This document defines two response headers, Accept-CH and Accept-CH-Lifetime, that servers can use to advertise their use of request headers for proactive content negotiation, along with a set of guidelines for the creation of such headers, colloquially known as "Client Hints."

It also defines an initial set of Client Hints.


--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/client-hints>.


--- middle

# Introduction

There are thousands of different devices accessing the web, each with different device capabilities and preference information. These device capabilities include hardware and software characteristics, as well as dynamic user and client preferences.

One way to infer some of these capabilities is through User-Agent (Section 5.5.3 of {{RFC7231}}) header field detection against an established database of client signatures. However, this technique requires acquiring such a database, integrating it into the serving path, and keeping it up to date. However, even once this infrastructure is deployed, user agent sniffing has numerous limitations:

  - User agent detection cannot reliably identify all static variables
  - User agent detection cannot infer any dynamic client preferences
  - User agent detection requires an external device database
  - User agent detection is not cache friendly

A popular alternative strategy is to use HTTP cookies ({{RFC6265}}) to communicate some information about the user agent. However, this approach is also not cache friendly, bound by same origin policy, and often imposes additional client-side latency by requiring JavaScript execution to create and manage HTTP cookies.

Proactive content negotiation (Section 3.4.1 of {{RFC7231}}) offers an alternative approach; user agents use specified, well-defined request headers to advertise their capabilities and characteristics, so that servers can select (or formulate) an appropriate response.

However, proactive content negotiation requires clients to send these request headers prolifically. This causes performance concerns (because it creates "bloat" in requests), as well as privacy issues; passively providing such information allows servers to silently fingerprint the user agent.

This document defines a new response header, Accept-CH, that allows an origin server to explicitly ask that clients send these headers in requests, for a period of time bounded by the Accept-CH-Lifetime response header. It also defines guidelines for content negotiation mechanisms that use it, colloquially referred to as Client Hints.

Client Hints mitigate the performance concerns by assuring that clients will only send the request headers when they're actually going to be used, and the privacy concerns of passive fingerprinting by requiring explicit opt-in and disclosure of required headers by the server through the use of the Accept-CH response header.

This document also defines an initial set of Client Hints.

It does not supersede or replace the User-Agent header field. Existing device detection mechanisms can continue to use both mechanisms if necessary. By advertising user agent capabilities within a request header field, Client Hints allow for cache friendly and proactive content negotiation.

## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 {{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals, as shown here.

This document uses the Augmented Backus-Naur Form (ABNF) notation of {{RFC5234}} with the list rule extension defined in {{RFC7230}}, Appendix B. It includes by reference the DIGIT rule from {{RFC5234}} and the OWS and field-name rules from {{RFC7230}}.


# Client Hint Request Header Fields

A Client Hint request header field is a HTTP header field that is used by HTTP clients to indicate configuration data that can be used by the server to select an appropriate response. Each one conveys client preferences that the server can use to adapt and optimize the response.

## Sending Client Hints

Clients control which Client Hints are sent in requests, based on their default settings, user configuration, and server preferences. The client and server can use an opt-in mechanism outlined below to negotiate which fields should be sent to allow for efficient content adaption, and optionally use additional mechanisms to negotiate delegation policies that control access of third parties to same fields.

Implementers should be aware of the passive fingerprinting implications when implementing support for Client Hints, and follow the considerations outlined in "Security Considerations" section of this document.


## Server Processing of Client Hints

When presented with a request that contains one or more client hint header fields, servers can optimize the response based upon the information in them. When doing so, and if the resource is cacheable, the server MUST also generate a Vary response header field (Section 7.1.4 of {{RFC7231}}) to indicate which hints can affect the selected response and whether the selected response is appropriate for a later request.

Further, depending on the hint used, the server can generate additional response header fields to convey related values to aid client processing. For example, this document defines the "Content-DPR" response header field that needs to be returned by the server when the "DPR" hint is used to select the response.


### Advertising Support via Accept-CH Header Field {#accept-ch}

Servers can advertise support for Client Hints using the Accept-CH header field or an equivalent HTML meta element with http-equiv attribute ({{HTML5}}).

~~~ abnf7230
  Accept-CH = #field-name
~~~

For example:

~~~ example
  Accept-CH: DPR, Width, Viewport-Width
~~~

When a client receives an HTTP response advertising support for Client Hints, it should process it as origin ({{RFC6454}}) opt-in to receive Client Hint header fields advertised in the field-value. The opt-in MUST be delivered over a secure transport.

For example, based on Accept-CH example above, a user agent could append DPR, Width, and Viewport-Width header fields to all same-origin resource requests initiated by the page constructed from the response.


### The Accept-CH-Lifetime Header Field {#accept-ch-lifetime}

Servers can ask the client to remember the set of Client Hints that the server supports for a specified period of time, to enable delivery of Client Hints on subsequent requests to the server's origin ({{RFC6454}}).

~~~ abnf7230
  Accept-CH-Lifetime = #delta-seconds
~~~

When a client receives an HTTP response that contains Accept-CH-Lifetime header field, the field-value indicates that the Accept-CH preference SHOULD be persisted and bound to the origin, and be considered stale after response's age ({{RFC7234}}, section 4.2) is greater than the specified number of seconds.
The preference MUST be delivered over a secure transport, and MUST NOT be persisted for an origin that isn't HTTPS.

~~~ example
  Accept-CH: DPR, Width
  Accept-CH: Viewport-Width
  Accept-CH-Lifetime: 86400
~~~

For example, based on the Accept-CH and Accept-CH-Lifetime example above, which is received in response to a user agent navigating to "https://example.com", and delivered over a secure transport: a user agent SHOULD persist an Accept-CH preference bound to "https://example.com" for up to 86400 seconds (1 day), and use it for user agent navigations to "https://example.com" and any same-origin resource requests initiated by the page constructed from the navigation's response. This preference SHOULD NOT extend to resource requests initiated to "https://example.com" from other origins.

If Accept-CH-Lifetime occurs in a message more than once, the last value overrides all previous occurrences.


### Interaction with Caches

When selecting an optimized response based on one or more Client Hints, and if the resource is cacheable, the server needs to generate a Vary response header field ({{RFC7234}}) to indicate which hints can affect the selected response and whether the selected response is appropriate for a later request.

~~~ example
  Vary: DPR
~~~

Above example indicates that the cache key needs to include the DPR header field.

~~~ example
  Vary: DPR, Width
~~~

Above example indicates that the cache key needs to include the DPR and Width header fields.


# Client Hints

## The DPR Header Field {#dpr}

The "DPR" request header field is a number that indicates the client's current Device Pixel Ratio (DPR), which is the ratio of physical pixels over CSS px (Section 5.2 of {{CSSVAL}}) of the layout viewport (Section 9.1.1 of [CSS2]) on the device.

~~~ abnf7230
  DPR = 1*DIGIT [ "." 1*DIGIT ]
~~~

If DPR occurs in a message more than once, the last value overrides all previous occurrences.


### Confirming Selected DPR {#content-dpr}

The "Content-DPR" response header field is a number that indicates the ratio between physical pixels over CSS px of the selected image response.

~~~ abnf7230
  Content-DPR = 1*DIGIT [ "." 1*DIGIT ]
~~~

DPR ratio affects the calculation of intrinsic size of image resources on the client - i.e. typically, the client automatically scales the natural size of the image by the DPR ratio to derive its display dimensions. As a result, the server MUST explicitly indicate the DPR of the selected image response whenever the DPR hint is used, and the client MUST use the DPR value returned by the server to perform its calculations. In case the server returned Content-DPR value contradicts previous client-side DPR indication, the server returned value MUST take precedence.

Note that DPR confirmation is only required for image responses, and the server does not need to confirm the resource width as this value can be derived from the resource itself once it is decoded by the client.

If Content-DPR occurs in a message more than once, the last value overrides all previous occurrences.


## The Width Header Field {#width}

The "Width" request header field is a number that indicates the desired resource width in physical px (i.e. intrinsic size of an image). The provided physical px value is a number rounded to the smallest following integer (i.e. ceiling value).

~~~ abnf7230
  Width = 1*DIGIT
~~~

If the desired resource width is not known at the time of the request or the resource does not have a display width, the Width header field can be omitted. If Width occurs in a message more than once, the last value overrides all previous occurrences.


## The Viewport-Width Header Field {#viewport-width}

The "Viewport-Width" request header field is a number that indicates the layout viewport width in CSS px. The provided CSS px value is a number rounded to the smallest following integer (i.e. ceiling value).

~~~ abnf7230
  Viewport-Width = 1*DIGIT
~~~

If Viewport-Width occurs in a message more than once, the last value overrides all previous occurrences.


# Examples

For example, given the following request header fields:

~~~ example
  DPR: 2.0
  Width: 320
  Viewport-Width: 320
~~~

The server knows that the device pixel ratio is 2.0, that the intended display width of the requested resource is 160 CSS px (320 physical pixels at 2x resolution), and that the viewport width is 320 CSS px.

If the server uses above hints to perform resource selection for an image asset, it must confirm its selection via the Content-DPR response header to allow the client to calculate the appropriate intrinsic size of the image response. The server does not need to confirm resource width, only the ratio between physical pixels and CSS px of the selected image resource:

~~~ example
  Content-DPR: 1.0
~~~

The Content-DPR response header field indicates to the client that the server has selected resource with DPR ratio of 1.0. The client can use this information to perform additional processing on the resource - for example, calculate the appropriate intrinsic size of the image resource such that it is displayed at the correct resolution.


# Security Considerations

The request header fields defined in this document, and those that extend it, expose information about the user's environment to enable proactive content negotiation. Such information may reveal new information about the user and implementers ought to consider the following considerations, recommendations, and best practices.

Transmitted Client Hints header fields SHOULD NOT provide new information that is otherwise not available to the application via other means, such as using HTML, CSS, or JavaScript. Further, sending highly granular data, such as image and viewport width may help identify users across multiple requests. Reducing the set of field values that can be expressed, or restricting them to an enumerated range where the advertised value is close but is not an exact representation of the current value, can improve privacy and reduce risk of linkability by ensuring that the same value is sent by multiple users. However, such precautions can still be insufficient for some types of data, especially data that can change over time.

Implementers ought to consider both user and server controlled mechanisms and policies to control which Client Hints header fields are advertised:

  - Implementers SHOULD restrict delivery of some or all Client Hints header fields to the opt-in origin only, unless the opt-in origin has explicitly delegated permission to another origin to request Client Hints header fields.
  - Implementers MAY provide user choice mechanisms so that users may balance privacy concerns with bandwidth limitations. However, implementers should also be aware that explaining the privacy implications of passive fingerprinting to users may be challenging.
  - Implementations specific to certain use cases or threat models MAY avoid transmitting some or all of Client Hints header fields. For example, avoid transmission of header fields that can carry higher risks of linkability.

Implementers SHOULD support Client Hints opt-in mechanisms and MUST clear persisted opt-in preferences when any one of site data, browsing history, browsing cache, or similar, are cleared.


# IANA Considerations

This document defines the "Accept-CH", "DPR", "Viewport-Width", and "Width" HTTP request fields, "Accept-CH", "Accept-CH-Lifetime", and "Content-DPR" HTTP response field, and registers them in the Permanent Message Header Fields registry.

## Accept-CH {#iana-accept-ch}
- Header field name: Accept-CH
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{accept-ch}} of this document
- Related information: for Client Hints

## Accept-CH-Lifetime {#iana-accept-ch-lifetime}
- Header field name: Accept-CH-Lifetime
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{accept-ch-lifetime}} of this document
- Related information: for Client Hints

## Content-DPR {#iana-content-dpr}
- Header field name: Content-DPR
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{content-dpr}} of this document
- Related information: for Client Hints

## DPR {#iana-dpr}
- Header field name: DPR
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{dpr}} of this document
- Related information: for Client Hints

## Viewport-Width {#iana-viewport-width}
- Header field name: Viewport-Width
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{viewport-width}} of this document
- Related information: for Client Hints

## Width {#iana-width}
- Header field name: Width
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{width}} of this document
- Related information: for Client Hints


--- back

# Interaction with Key Response Header Field

Client Hints may be combined with Key response header field ({{KEY}}) to enable fine-grained control of the cache key for improved cache efficiency. For example, the server can return the following set of instructions:

~~~ example
  Key: DPR;partition=1.5:2.5:4.0
~~~

Above example indicates that the cache key needs to include the value of the DPR header field with three segments: less than 1.5, 1.5 to less than 2.5, and 4.0 or greater.

~~~ example
  Key: Width;div=320
~~~

Above example indicates that the cache key needs to include the value of the Width header field and be partitioned into groups of 320: 0-320, 320-640, and so on.


# Changes

## Since -00
* Issue 168 (make Save-Data extensible) updated ABNF.
* Issue 163 (CH review feedback) editorial feedback from httpwg list.
* Issue 153 (NetInfo API citation) added normative reference.

## Since -01
* Issue 200: Moved Key reference to informative.
* Issue 215: Extended passive fingerprinting and mitigation considerations.
* Changed document status to experimental.

## Since -02
* Issue 239: Updated reference to CR-css-values-3
* Issue 240: Updated reference for Network Information API
* Issue 241: Consistency in IANA considerations
* Issue 250: Clarified Accept-CH

## Since -03
* Issue 284: Extended guidance for Accept-CH
* Issue 308: Editorial cleanup
* Issue 306: Define Accept-CH-Lifetime

## Since -04
* Issue 361: Removed Downlink
* Issue 361: Moved Key to appendix, plus other editorial feedback

## Since -05
* Issue 372: Scoped CH opt-in and delivery to secure transports
* Issue 373: Bind CH opt-in to origin

## Since -06
* Issue 524: Save-Data is now defined by NetInfo spec, dropping

# Acknowledgements
{:numbered="false"}
Thanks to Mark Nottingham, Julian Reschke, Chris Bentzel, Yoav Weiss, Ben Greenstein, Tarun Bansal, Roy Fielding, Vasiliy Faronov, Ted Hardie, Jonas Sicking, and numerous other members of the IETF HTTP Working Group for invaluable help and feedback.
