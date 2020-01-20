---
title: HTTP Client Hints
abbrev:
docname: draft-ietf-httpbis-client-hints-08
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
 -
    ins: Y. Weiss
    name: Yoav Weiss
    organization: Google
    email: yoav@yoav.ws
    uri: https://blog.yoav.ws/

normative:
  RFC5234:
  RFC7230:
  RFC7231:
  RFC7234:
  RFC6454:
  HTML:
    target: https://html.spec.whatwg.org/
    title: HTML
    author:
    -
      ins: I. Hickson
      name: Ian Hickson
      organization: Google, Inc.
    -
      ins: S. Pieters
      name: Simon Pieters
      organization: Bocoup
    -
      ins: A. van Kesteren
      name: Anne van Kesteren
      organization: Mozilla
    -
      ins: P. Jägenstedt
      name: Philip Jägenstedt
      organization: Google, Inc.
    -
      ins: D. Denicola
      name: Domenic Denicola
      organization: Google, Inc.
  FETCH:
    target: https://fetch.spec.whatwg.org/
    title: Fetch
    author:
    -
      ins: A. van Kesteren
      name: Anne van Kesteren
      organization: Mozilla

informative:
  RFC6265:

--- abstract

HTTP defines proactive content negotiation to allow servers to select the appropriate response for a given request, based upon the user agent's characteristics, as expressed in request headers. In practice, clients are often unwilling to send those request headers, because it is not clear whether they will be used, and sending them impacts both performance and privacy.

This document defines an Accept-CH response header that servers can use to advertise their use of request headers for proactive content negotiation, along with a set of guidelines for the creation of such headers, colloquially known as "Client Hints."


--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/client-hints>.


--- middle

# Introduction

There are thousands of different devices accessing the web, each with different device capabilities and preference information. These device capabilities include hardware and software characteristics, as well as dynamic user and client preferences. Applications that want to allow the server to optimize content delivery and user experience based on such capabilities have, historically, had to rely on passive identification (e.g., by matching User-Agent (Section 5.5.3 of {{RFC7231}}) header field against an established database of client signatures), used HTTP cookies and URL parameters, or use some combination of these and similar mechanisms to enable ad hoc content negotiation.

Such techniques are expensive to setup and maintain, are not portable across both applications and servers, and make it hard to reason for both client and server about which data is required and is in use during the negotiation:

  - User agent detection cannot reliably identify all static variables, cannot infer dynamic client preferences, requires external device database, is not cache friendly, and is reliant on a passive fingerprinting surface.
  - Cookie based approaches are not portable across applications and servers, impose additional client-side latency by requiring JavaScript execution, and are not cache friendly.
  - URL parameters, similar to cookie based approaches, suffer from lack of portability, and are hard to deploy due to a requirement to encode content negotiation data inside of the URL of each resource.

Proactive content negotiation (Section 3.4.1 of {{RFC7231}}) offers an alternative approach; user agents use specified, well-defined request headers to advertise their capabilities and characteristics, so that servers can select (or formulate) an appropriate response.

However, proactive content negotiation requires clients to send these request headers prolifically. This causes performance concerns (because it creates "bloat" in requests), as well as privacy issues; passively providing such information allows servers to silently fingerprint the user agent.

This document defines a new response header, Accept-CH, that allows an origin server to explicitly ask that clients send these headers in requests. It also defines guidelines for content negotiation mechanisms that use it, colloquially referred to as Client Hints.

Client Hints mitigate the performance concerns by assuring that clients will only send the request headers when they're actually going to be used, and the privacy concerns of passive fingerprinting by requiring explicit opt-in and disclosure of required headers by the server through the use of the Accept-CH response header.

This document defines the Client Hints infrastructure, a framework that enables servers to opt-in to specific proactive content negotiation features, which will enable them to adapt their content accordingly. However, it does not define any specific features that will use that infrastructure. Those features will be defined in their respective specifications.

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

Further, depending on the hint used, the server can generate additional response header fields to convey related values to aid client processing.

# Advertising Server Support

Servers can advertise support for Client Hints using the mechnisms described below.

## The Accept-CH Response Header Field {#accept-ch}

The Accept-CH response header field or the equivalent HTML meta element with http-equiv attribute ({{HTML}}) indicate server support for particular hints indicated in its value.

Accept-CH is a Structured Header {{!I-D.ietf-httpbis-header-structure}}. Its value MUST be an sh-list (Section 3.1 of {{!I-D.ietf-httpbis-header-structure}}) whose members are tokens (Section 3.7 of {{!I-D.ietf-httpbis-header-structure}}). Its ABNF is:


~~~ abnf7230
  Accept-CH = sh-list
~~~

For example:

~~~ example
  Accept-CH: Sec-CH-Example, Sec-CH-Example-2
~~~

When a client receives an HTTP response advertising support for provided list of Clients Hints, it SHOULD process it as origin ({{RFC6454}}) opt-in to receive Client Hint header fields advertised in the field-value, for subsequent same-origin requests.

  - The opt-in MUST be delivered over a secure transport.
  - The opt-in SHOULD be persisted and bound to the origin to enable delivery of Client Hints on subsequent requests to the server's origin, and MUST NOT be persisted for an origin that isn't HTTPS.

~~~ example
  Accept-CH: Sec-CH-Example, Sec-CH-Example-2
  Accept-CH: Sec-CH-Example-3
~~~

For example, based on the Accept-CH example above, which is received in response to a user agent navigating to "https://example.com", and delivered over a secure transport: a user agent SHOULD persist an Accept-CH preference bound to "https://example.com" and use it for user agent navigations to "https://example.com" and any same-origin resource requests initiated by the page constructed from the navigation's response. This preference SHOULD NOT extend to resource requests initiated to "https://example.com" from other origins.

### Interaction with Caches

When selecting an optimized response based on one or more Client Hints, and if the resource is cacheable, the server needs to generate a Vary response header field ({{RFC7234}}) to indicate which hints can affect the selected response and whether the selected response is appropriate for a later request.

~~~ example
  Vary: Sec-CH-Example
~~~

Above example indicates that the cache key needs to include the Sec-CH-Example header field.

~~~ example
  Vary: Sec-CH-Example, Sec-CH-Example-2
~~~

Above example indicates that the cache key needs to include the Sec-CH-Example and Sec-CH-Example-2 header fields.


# Security Considerations

## Information Exposure
Request header fields used in features relying on this document expose information about the user's environment to enable proactive content negotiation. Such information may reveal new information about the user and implementers ought to consider the following considerations, recommendations, and best practices.

The underlying assumption is that exposing information about the user as a request header is equivalent to the capability of that request's origin to access that information by other means and transmit it to itself.

Therefore, features relying on this document to define Client Hint headers MUST NOT provide new information that is otherwise not available to the application via other means, such as existing request headers, HTML, CSS, or JavaScript.

Such features SHOULD take into account the following aspects of the information exposed: 

  - Entropy
    - Exposing highly granular data may help identify users across multiple requests to different origins. Reducing the set of field values that can be expressed, or restricting them to an enumerated range where the advertised value is close but is not an exact representation of the current value, can improve privacy and reduce risk of linkability by ensuring that the same value is sent by multiple users.
  - Sensitivity
    - The feature SHOULD NOT expose user sensitive information. To that end, information available to the application, but gated behind specific user actions (e.g. a permission prompt or user activation) SHOULD NOT be exposed as a Client Hint.
  - Change over time
    - The feature SHOULD NOT expose user information that changes over time, unless the state change itself is also exposed (e.g. through JavaScript callbacks).

Different features will be positioned in different points in the space between low-entropy, non-sensitive and static information (e.g. user agent information), and high-entropy, sensitive and dynamic information (e.g. geolocation). User agents SHOULD consider the value provided by a particular feature vs these considerations, and MAY have different policies regarding that tradeoff on a per-feature basis.

Implementers ought to consider both user and server controlled mechanisms and policies to control which Client Hints header fields are advertised:

  - Implementers SHOULD restrict delivery of some or all Client Hints header fields to the opt-in origin only, unless the opt-in origin has explicitly delegated permission to another origin to request Client Hints header fields.
  - Implementers MAY provide user choice mechanisms so that users may balance privacy concerns with bandwidth limitations. However, implementers should also be aware that explaining the privacy implications of passive fingerprinting to users may be challenging.
  - Implementations specific to certain use cases or threat models MAY avoid transmitting some or all of Client Hints header fields. For example, avoid transmission of header fields that can carry higher risks of linkability.

Implementers SHOULD support Client Hints opt-in mechanisms and MUST clear persisted opt-in preferences when any one of site data, browsing history, browsing cache, cookies, or similar, are cleared.

# Cost of Sending Hints

While HTTP header compression schemes reduce the cost of adding HTTP header fields, sending Client Hints to the server incurs an increase in request byte size.
Servers SHOULD take that into account when opting in to receive Client Hints, and SHOULD NOT opt-in to receive hints unless they are to be used for content adaptation purposes.

Due to request byte size increase, features relying on this document to define Client Hints MAY consider restricting sending those hints to certain request destinations {{FETCH}}, where they are more likely to be useful. 


## Deployment and Security Risks
Deployment of new request headers requires several considerations:

  - Potential conflicts due to existing use of field name
  - Properties of the data communicated in field value

Authors of new Client Hints are advised to carefully consider whether they should be able to be added by client-side content (e.g., scripts), or whether they should be exclusively set by the user agent. In the latter case, the Sec- prefix on the header field name has the effect of preventing scripts and other application content from setting them in user agents. 
Using the "Sec-" prefix signals to servers that the user agent - and not application content - generated the values. See {{FETCH}} for more information.

By convention, request headers that are client hints are encouraged to use a CH- prefix, to make them easier to identify as using this framework; for example, CH-Foo or, with a "Sec-" prefix, Sec-CH-Foo. Doing so makes them easier to identify programmatically (e.g., for stripping unrecognised hints from requests by privacy filters).


## Abuse Detection
A user agent that tracks access to active fingerprinting information SHOULD consider emission of Client Hints headers similarly to the way it would consider access to the equivalent API.

Research into abuse of Client Hints might look at how HTTP responses that contain Client Hints differ from those with different values, and from those without. This might be used to reveal which Client Hints are in use, allowing researchers to further analyze that use.



# IANA Considerations

This document defines the "Accept-CH" HTTP response field, and registers it in the Permanent Message Header Fields registry.

## Accept-CH {#iana-accept-ch}
- Header field name: Accept-CH
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{accept-ch}} of this document
- Related information: for Client Hints

--- back

# Interaction with Variants Response Header Field

Client Hints may be combined with Variants response header field {{?VARIANTS=I-D.ietf-httpbis-variants}} to enable fine-grained control of the cache key for improved cache efficiency.
Features that define Client Hints will need to specify the related variants algorithms as described in Section 6 of {{?VARIANTS}}.

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
* PR 775: Removed specific features to be defined in other specifications

## Since -07
* Issue 761: Clarified that the defined headers are response headers.
* Issue 730: Replaced Key reference with Variants. 
* Issue 700: Replaced ABNF with structured headers.
* PR 878: Removed Accept-CH-Lifetime based on feedback at IETF 105

## Since -08
* PR 985: Describe the bytesize cost of hints.
* PR 776: Add Sec- and CH- prefix considerations.
* PR 1001: Clear CH persistence when cookies are cleared.


# Acknowledgements
{:numbered="false"}
Thanks to Mark Nottingham, Julian Reschke, Chris Bentzel, Ben Greenstein, Tarun Bansal, Roy Fielding, Vasiliy Faronov, Ted Hardie, Jonas Sicking, Martin Thomson, and numerous other members of the IETF HTTP Working Group for invaluable help and feedback.
