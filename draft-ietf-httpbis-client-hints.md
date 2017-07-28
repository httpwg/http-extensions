---
title: HTTP Client Hints
abbrev:
docname: draft-ietf-httpbis-client-hints-latest
date: 2017
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
  RFC2119:
  RFC5234:
  RFC7230:
  RFC7231:
  RFC7234:
  RFC6454:
  HTML5: W3C.REC-html5-20141028
  SECURE-CONTEXTS: W3C.CR-secure-contexts-20160915
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

An increasing diversity of Web-connected devices and software capabilities has created a need to deliver optimized content for each device.

This specification defines an extensible and configurable set of HTTP request header fields, colloquially known as Client Hints, to address this. They are intended to be used as input to proactive content negotiation; just as the Accept header field allows user agents to indicate what formats they prefer, Client Hints allow user agents to indicate device and agent specific preferences.


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

A popular alternative strategy is to use HTTP cookies ({{RFC6265}}) to communicate some information about the user agent. However, this approach is also not cache friendly, bound by same origin policy, and imposes additional client-side latency by requiring JavaScript execution to create and manage HTTP cookies.

This document defines a set of new request header fields that allow user agent to perform proactive content negotiation (Section 3.4.1 of {{RFC7231}}) by indicating device and agent specific preferences, through a mechanism similar to the Accept header field which is used to indicate preferred response formats.

Client Hints does not supersede or replace the User-Agent header field. Existing device detection mechanisms can continue to use both mechanisms if necessary. By advertising its capabilities within a request header field, Client Hints allows for cache friendly and proactive content negotiation.

## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals, as shown here.

This document uses the Augmented Backus-Naur Form (ABNF) notation of {{RFC5234}} with the list rule extension defined in {{RFC7230}}, Appendix B. It includes by reference the DIGIT rule from {{RFC5234}} and the OWS and field-name rules from {{RFC7230}}.


# Client Hint Request Header Fields

A Client Hint request header field is a HTTP header field that is used by HTTP clients to indicate configuration data that can be used by the server to select an appropriate response. Each one conveys client preferences that the server can use to adapt and optimize the response.

## Sending Client Hints

Clients control which Client Hints are sent in requests, based on their default settings, user configuration and/or preferences. The client and server, or an intermediate proxy, can use an opt-in mechanism outlined below to negotiate which fields should be sent to allow for efficient content adaption.

Implementers should be be aware of the passive fingerprinting and network information disclosure implications when implementing support for Client Hints, and follow the considerations outlined in "Security Considerations" section of this document.


## Server Processing of Client Hints

When presented with a request that contains one or more client hint header fields, servers can optimize the response based upon the information in them. When doing so, and if the resource is cacheable, the server MUST also generate a Vary response header field (Section 7.1.4 of {{RFC7231}}) to indicate which hints can affect the selected response and whether the selected response is appropriate for a later request.

Further, depending on the hint used, the server can generate additional response header fields to convey related values to aid client processing. For example, this specification defines the "Content-DPR" response header field that needs to be returned by the server when the "DPR" hint is used to select the response.


### Advertising Support via Accept-CH Header Field {#accept-ch}

Servers can advertise support for Client Hints using the Accept-CH header field or an equivalent HTML meta element with http-equiv attribute ({{HTML5}}).

~~~ abnf7230
  Accept-CH = #field-name
~~~

For example:

~~~ example
  Accept-CH: DPR, Width, Viewport-Width
~~~

When a client receives Accept-CH from a potentially trustworthy origin ({{SECURE-CONTEXTS}}), or if it is capable of processing the HTML response and finds an equivalent HTML meta element, it can treat it as a signal that the origin ({{RFC6454}}) is interested in receiving specified request header fields that match the advertised field-values; same-origin resource requests initiated as a result of processing the response from the server that includes the Accept-CH opt-in can include the request header fields that match the advertised field-values.

For example, based on Accept-CH example above, a user agent could append DPR, Width, and Viewport-Width header fields to all same-origin resource requests initiated by the page constructed from the response.


### The Accept-CH-Lifetime Header Field {#accept-ch-lifetime}

Servers can ask the client to remember sent Accept-CH preference for a specified period of time, to enable delivery of Client Hints on subsequent requests to the server's origin ({{RFC6454}}).

~~~ abnf7230
  Accept-CH-Lifetime = #delta-seconds
~~~

When a client receives Accept-CH-Lifetime from a potentially trustworthy origin ("opt-in origin"), the field-value indicates that the Accept-CH preference SHOULD be considered stale after its age is greater than the specified number of seconds, and if applicable, persisted as a double-keyed preference that combines the values of the opt-in origin and the potentially trustworthy origin of the resource that initiated the request that received the opt-in preference.

~~~ example
  Accept-CH: DPR, Width
  Accept-CH: Viewport-Width
  Accept-CH-Lifetime: 86400
~~~

For example, based on the Accept-CH and Accept-CH-Lifetime example above, which is received from bar.com in response to a resource request initiated by foo.com, both of which are potentially trustworthy origins: a user agent could persist a double-keyed Accept-CH preference, for requests initiated to bar.com from foo.com, for up to 86400 seconds (1 day). Then, if a request is initiated to bar.com from foo.com before the preference is stale the client could append the requested header fields (DPR, Width, and Viewport-Width in this example) to all requests matching that origin. Alternatively, if the same Accept-CH-Lifetime preference was advertised by bar.com, then same Client Hints header fields can be advertised on a navigation to the origin, and any requests to same origin initiated as a result of processing a response from bar.com.

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


## The Save-Data Header Field {#save-data}

The "Save-Data" request header field consists of one or more tokens that indicate client's preference for reduced data usage, due to high transfer costs, slow connection speeds, or other reasons.

~~~ abnf7230
  Save-Data = sd-token *( OWS ";" OWS [sd-token] )
  sd-token = token
~~~

This document defines the "on" sd-token value, which is used as a signal indicating explicit user opt-in into a reduced data usage mode on the client, and when communicated to origins allows them to deliver alternate content honoring such preference - e.g. smaller image and video resources, alternate markup, and so on. New token and extension token values can be defined by updates to this specification.

If Save-Data occurs in a message more than once, the last value overrides all previous occurrences.


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

The request header fields defined in this specification, and those that extend it, expose information about the user's environment to enable proactive content negotiation. Such information may reveal new information about the user and implementers ought to consider the following considerations, recommendations, and best practices.

Transmitted Client Hints header fields should not provide new information that is otherwise not available to the application via HTML, CSS, or JavaScript.  Further, sending highly granular data, such as image and viewport width may help identify users across multiple requests. Restricting such field values to an enumerated range, where the advertised value is close but is not an exact representation of the current value, can help mitigate the risk of such fingerprinting as well as reduce possibility of unnecessary cache fragmentation.

Implementers should consider both user and server controlled mechanisms and policies to control which Client Hints header fields are advertised:

  - Implementers may provide user choice mechanisms so that users may balance privacy concerns with bandwidth limitations. However, implementers should also be aware that explaining the privacy implications of passive fingerprinting or network information disclosure to users may be challenging.
  - Implementers should support double-keyed Client Hints opt-in requested by potentially trustworthy origins via Accept-CH and Accept-CH-Lifetime header fields, and clear remembered opt-in when site data, browsing history, browsing cache, or similar, are cleared.
  - Implementations specific to certain use cases or threat models may avoid transmitting Client Hints header fields altogether or limit them to authenticated sessions only that already carry identifying information, such as cookies or referer data.

Following the above recommendations should significantly reduce the risks of linkability and passive fingerprinting.


# IANA Considerations

This document defines the "Accept-CH", "DPR", "Save-Data", "Viewport-Width", and "Width" HTTP request fields, "Accept-CH", "Accept-CH-Lifetime", and "Content-DPR" HTTP response field, and registers them in the Permanent Message Header Fields registry.

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

## Save-Data {#iana-save-data}
- Header field name: Save-Data
- Applicable protocol: HTTP
- Status: standard
- Author/Change controller: IETF
- Specification document(s): {{save-data}} of this document
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

# Acknowledgements

Thanks to Mark Nottingham, Julian Reschke, Chris Bentzel, Yoav Weiss, Ben Greenstein, Tarun Bansal, Roy Fielding, Vasiliy Faronov, Ted Hardie, Jonas Sicking, and numerous other members of the IETF HTTP Working Group for invaluable help and feedback.


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
* Issue 361: Moved Key to appendix, plus other editorial feedback.

## Since -05
* None
