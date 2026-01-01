---
title: The No-Vary-Search HTTP Response Header Field
abbrev: No-Vary-Search
category: std

docname: draft-ietf-httpbis-no-vary-search-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: "Web and Internet Transport"
workgroup: "HyperText Transfer Protocol"
keyword:
 - http
 - caching
venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/no-vary-search
  latest: "https://httpwg.org/http-extensions/draft-ietf-httpbis-no-vary-search.html"
github-issue-label: no-vary-search

author:
 -
    fullname: Domenic Denicola
    organization: Google LLC
    email: d@domenic.me
 -
    fullname: Jeremy Roman
    organization: Google LLC
    email: jbroman@chromium.org

normative:
  URI: RFC3986
  HTTP: RFC9110
  HTTP-CACHING: RFC9111
  FETCH:
   target: https://fetch.spec.whatwg.org/
   title: Fetch Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG
  STRUCTURED-FIELDS: RFC8941
  WHATWG-ENCODING:
   target: https://encoding.spec.whatwg.org/
   title: Encoding Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG
  WHATWG-INFRA:
   target: https://infra.spec.whatwg.org/
   title: Infra Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
      -
         ins: D. Denicola
         name: Domenic Denicola
         org: Google LLC
   ann: WHATWG
  WHATWG-URL:
   target: https://url.spec.whatwg.org/
   title: URL Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG

informative:
  HTML:
   target: https://html.spec.whatwg.org/
   title: HTML Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG
  NAV-TRACKING-MITIGATIONS:
   target: https://privacycg.github.io/nav-tracking-mitigations/
   title: Navigational-Tracking Mitigations
   author:
      -
         ins: P. Snyder
         name: Pete Snyder
         org: Brave Software, Inc.
      -
         ins: J. Yasskin
         name: Jeffrey Yasskin
         org: Google LLC
   ann: W3C Privacy CG

--- abstract

This specification defines a proposed HTTP response header field for changing how URI query parameters impact caching.

--- middle

# Introduction

HTTP caching {{HTTP-CACHING}} is based on reusing resources which match across a number of cache keys. One of the most prominent is the presented target URI ({{Section 7.1 of HTTP}}). However, sometimes multiple URIs can represent the same resource. This leads to caches not always being as helpful as they could be: if the cache contains a response under one URI, but the resource is then requested under another, the cached version will be ignored.

The `No-Vary-Search` HTTP header field tackles a specific subset of this general problem, for when different URIs that only differ in
certain query parameters identify the same resource. It allows resources to declare that some or all parts of the query component do not semantically affect the served resource, and thus can be ignored for cache matching purposes. For example, if the order of the query parameters do not affect which resource is identified, this is indicated using

~~~~http-message
No-Vary-Search: key-order
~~~~

If the specific query parameters (e.g., ones indicating something for analytics) do not semantically affect the served resource, this is indicated using

~~~~http-message
No-Vary-Search: params=("utm_source" "utm_medium" "utm_campaign")
~~~~

And if the resource instead wants to take an allowlist-based approach, where only certain known query parameters semantically affect the served resource, they can use

~~~~http-message
No-Vary-Search: params, except=("productId")
~~~~

{{header-definition}} defines the header field, using the {{STRUCTURED-FIELDS}} framework. {{data-model}} and {{parsing}} illustrate the data model for how the field value can be represented in specifications, and the process for parsing the raw output from the structured field parser into that data model. {{comparing}} gives the key algorithm for comparing if two URLs are equivalent under the influence of the header field; notably, it leans on the decomposition of the query component into keys and values given by the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded) format specified in {{WHATWG-URL}}. (As such, this header field is not useful for URLs whose query component does not follow that format.) Finally, {{caching}} explains how to extend {{Section 4 of HTTP-CACHING}} to take this new equivalence into account.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

In this document, the terms "URI" and "URL" are used interchangeably, depending on context. "URI" is used in the context of {{URI}}, {{HTTP}}, and {{HTTP-CACHING}}, whereas "URL" is used in the context of the algorithms specified in {{WHATWG-URL}}.


This document also adopts some conventions and notation typical in WHATWG and W3C usage, especially as it relates to algorithms. See {{WHATWG-INFRA}}, and in particular:

* its definition of lists, including the list literal notation « 1, 2, 3 ».
* its definition of strings, including their representation as code units.

(Other concepts used are called out using inline references.)

# HTTP header field definition {#header-definition}

The `No-Vary-Search` HTTP header field is a structured field {{STRUCTURED-FIELDS}} whose value MUST be a dictionary ({{Section 3.2 of STRUCTURED-FIELDS}}).

It has the following authoring conformance requirements:

* If present, the `key-order` entry's value MUST be a boolean ({{Section 3.3.6 of STRUCTURED-FIELDS}}).
* If present, the `params` entry's value MUST be either a boolean ({{Section 3.3.6 of STRUCTURED-FIELDS}}) or an inner list ({{Section 3.1.1 of STRUCTURED-FIELDS}}).
* If present, the `except` entry's value MUST be an inner list ({{Section 3.1.1 of STRUCTURED-FIELDS}}).
* The `except` entry MUST only be present if the `params` entry is also present, and the `params` entry's value is the boolean value true.

The dictionary MAY contain entries whose keys are not one of `key-order`, `params`, and `except`, but their meaning is not defined by this specification. Implementations of this specification will ignore such entries (but future documents might assign meaning to such entries).

{:aside}
> As always, the authoring conformance requirements are not binding on implementations. Implementations instead need to implement the processing model given by the obtain a URL search variance algorithm ({{obtain-a-url-search-variance}}).

# Data model {#data-model}

A _URL search variance_ consists of the following:

{: vspace="0"}
no-vary params
: either the special value __wildcard__ or a list of strings

vary params
: either the special value __wildcard__ or a list of strings

vary on key order
: a boolean

(((!default URL search variance)))
The _default URL search variance_ is a URL search variance whose no-vary params is an empty list, vary params is __wildcard__, and vary on key order is true.

*[default URL search variance]:

The obtain a URL search variance algorithm ({{obtain-a-url-search-variance}}) ensures that all URL search variances obey the following constraints:

* vary params is a list if and only if the no-vary params is __wildcard__; and
* no-vary params is a list if and only if the vary params is __wildcard__.

# Parsing {#parsing}

## Parse a URL search variance {#parse-a-url-search-variance}

*[parse a URL search variance]: #parse-a-url-search-variance

(((!parse a URL search variance)))
To _parse a URL search variance_ given _value_:

1. If _value_ is null, then return the default URL search variance.
1. Let _result_ be a new URL search variance.
1. Set _result_'s vary on key order to true.
1. If _value_\["`key-order`"] exists:
    1. If _value_\["`key-order`"] is not a boolean, then return the default URL search variance.
    1. Set _result_'s vary on key order to the boolean negation of _value_\["`key-order`"].
1. If _value_\["`params`"] exists:
    1. If _value_\["`params`"] is a boolean:
        1. If _value_\["`params`"] is true, then:
            1. Set _result_'s no-vary params to __wildcard__.
            1. Set _result_'s vary params to the empty list.
        1. Otherwise:
            1. Set _result_'s no-vary params to the empty list.
            1. Set _result_'s vary params to __wildcard__.
    1. Otherwise, if _value_\["`params`"] is an array:
        1. If any item in _value_\["`params`"] is not a string, then return the default URL search variance.
        1. Set _result_'s no-vary params to the result of applying parse a key ({{parse-a-key}}) to each item in _value_\["`params`"].
        1. Set _result_'s vary params to __wildcard__.
    1. Otherwise, return the default URL search variance.
1. If _value_\["`except`"] exists:
    1. If _value_\["`params`"] is not true, then return the default URL search variance.
    1. If _value_\["`except`"] is not an array, then return the default URL search variance.
    1. If any item in _value_\["`except`"] is not a string, then return the default URL search variance.
    1. Set _result_'s vary params to the result of applying parse a key ({{parse-a-key}}) to each item in _value_\["`except`"].
1. Return _result_.

{:aside}
> In general, this algorithm is strict and tends to return the default URL search variance whenever it sees something it doesn't recognize. This is because the default URL search variance behavior will just cause fewer cache hits, which is an acceptable fallback behavior.
>
> However, unrecognized keys at the top level are ignored, to make it easier to extend this specification in the future. To avoid misbehavior with existing client software, such extensions will likely expand, rather than reduce, the set of requests that a cached response can match.

{:aside}
> The input to this algorithm is generally obtained by parsing a structured field ({{Section 4.2 of STRUCTURED-FIELDS}}) using field_type "dictionary".

## Obtain a URL search variance {#obtain-a-url-search-variance}

*[obtain a URL search variance]: #obtain-a-url-search-variance

(((!obtain a URL search variance)))
To _obtain a URL search variance_ given a [response](https://fetch.spec.whatwg.org/#concept-response) _response_:

1. Let _fieldValue_ be the result of [getting a structured field value](https://fetch.spec.whatwg.org/#concept-header-list-get-structured-header) {{FETCH}} given \``No-Vary-Search`\` and "`dictionary`" from _response_'s header list.
1. Return the result of parsing a URL search variance ({{parse-a-url-search-variance}}) given _fieldValue_. (((parse a URL search variance)))

### Examples

The following illustrates how various inputs are parsed, in terms of their impacting on the resulting no-vary params and vary params:

| Input                                  | Result                                                    |
|----------------------------------------+-----------------------------------------------------------|
| `No-Vary-Search: params`               | no-vary params: __wildcard__<br>vary params: (empty list) |
| `No-Vary-Search: params=("a")`         | no-vary params: « "`a`" »<br>vary params: __wildcard__    |
| `No-Vary-Search: params, except=("x")` | no-vary params: __wildcard__<br>vary params: « "`x`" »    |

The following inputs are all invalid and will cause the default URL search variance to be returned:

{:compact}
  * `No-Vary-Search: unknown-key`
  * `No-Vary-Search: key-order="not a boolean"`
  * `No-Vary-Search: params="not a boolean or inner list"`
  * `No-Vary-Search: params=(not-a-string)`
  * `No-Vary-Search: params=("a"), except=("x")`
  * `No-Vary-Search: params=(), except=()`
  * `No-Vary-Search: params=?0, except=("x")`
  * `No-Vary-Search: params, except=(not-a-string)`
  * `No-Vary-Search: params, except="not an inner list"`
  * `No-Vary-Search: params, except=?1`
  * `No-Vary-Search: except=("x")`
  * `No-Vary-Search: except=()`

  The following inputs are valid, but somewhat unconventional. They are shown alongside their more conventional form.

| Input                                             | Conventional form                                 |
|---------------------------------------------------+---------------------------------------------------|
| `No-Vary-Search: params=?1`                       | `No-Vary-Search: params`                          |
| `No-Vary-Search: key-order=?1`                    | `No-Vary-Search: key-order`                       |
| `No-Vary-Search: params, key-order, except=("x")` | `No-Vary-Search: key-order, params, except=("x")` |
| `No-Vary-Search: params=?0`                       | (omit the header field)                           |
| `No-Vary-Search: params=()`                       | (omit the header field)                           |
| `No-Vary-Search: key-order=?0`                    | (omit the header field)                           |

## Parse a key {#parse-a-key}

*[parse a key]: #parse-a-key

(((!parse a key)))
To _parse a key_ given an ASCII string _keyString_:

  1. Let _keyBytes_ be the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _keyString_.

  1. Replace any 0x2B (+) in _keyBytes_ with 0x20 (SP).

  1. Let _keyBytesDecoded_ be the [percent-decoding](https://url.spec.whatwg.org/#percent-decode) {{WHATWG-URL}} of _keyBytes_.

  1. Let _keyStringDecoded_ be the [UTF-8 decoding without BOM](https://encoding.spec.whatwg.org/#utf-8-decode-without-bom) {{WHATWG-ENCODING}} of _keyBytesDecoded_.

  1. Return _keyStringDecoded_.

### Examples

The parse a key algorithm allows encoding non-ASCII key strings in the ASCII structured header field format, similar to how the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded) format {{WHATWG-URL}} allows encoding an entire entry list of keys and values in URI (which is constricted to ASCII characters). For example,

~~~~http-message
No-Vary-Search: params=("%C3%A9+%E6%B0%97")
~~~~

will result in a URL search variance whose vary params are « "`é 気`" ». As explained in a later example, the canonicalization process during equivalence testing means this will treat as equivalent URIs such as:

<!-- link "a later example" and "equivalence testing" -->

* `https://example.com/?é 気=1`
* `https://example.com/?é+気=2`
* `https://example.com/?%C3%A9%20気=3`
* `https://example.com/?%C3%A9+%E6%B0%97=4`

and so on, since they all are [parsed](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} to having the same key "`é 気`".

# Comparing {#comparing}

(((!equivalent modulo search variance)))
Two [URLs](https://url.spec.whatwg.org/#concept-url) {{WHATWG-URL}} _urlA_ and _urlB_ are _equivalent modulo search variance_ given a URL search variance _searchVariance_ if the following algorithm returns true:

1. If the scheme, username, password, host, port, or path of _urlA_ and _urlB_ differ, then return false.

1. If _searchVariance_ is equivalent to the default URL search variance, then:

    1. If _urlA_'s query equals _urlB_'s query, then return true.

    1. Return false.

    In this case, even URL pairs that might appear the same after running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} on their queries, such as `https://example.com/a` and `https://example.com/a?`, or `https://example.com/foo?a=b&&&c` and `https://example.com/foo?a=b&c=`, will be treated as inequivalent.

1. Let _searchParamsA_ and _searchParamsB_ be empty lists.

1. If _urlA_'s query is not null, then set _searchParamsA_ to the result of running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} given the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _urlA_'s query.

1. If _urlB_'s query is not null, then set _searchParamsB_ to the result of running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} given the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _urlB_'s query.

1. If _searchVariance_'s no-vary params is a list, then:

    1. Set _searchParamsA_ to a list containing those items _pair_ in _searchParamsA_ where _searchVariance_'s no-vary params does not contain _pair_\[0].

    1. Set _searchParamsB_ to a list containing those items _pair_ in _searchParamsB_ where _searchVariance_'s no-vary params does not contain _pair_\[0].

1. Otherwise, if _searchVariance_'s vary params is a list, then:

    1. Set _searchParamsA_ to a list containing those items _pair_ in _searchParamsA_ where _searchVariance_'s vary params contains _pair_\[0].

    1. Set _searchParamsB_ to a list containing those items _pair_ in _searchParamsB_ where _searchVariance_'s vary params contains _pair_\[0].

1. If _searchVariance_'s vary on key order is false, then:

    1. Let _keyLessThan_ be an algorithm taking as inputs two pairs (_keyA_, _valueA_) and (_keyB_, _valueB_), which returns whether _keyA_ is [code unit less than](https://infra.spec.whatwg.org/#code-unit-less-than) {{WHATWG-INFRA}} _keyB_.

    1. Set _searchParamsA_ to the result of sorting _searchParamsA_ in ascending order with _keyLessThan_.

    1. Set _searchParamsB_ to the result of sorting _searchParamsB_ in ascending order with _keyLessThan_.

1. If _searchParamsA_'s size is not equal to _searchParamsB_'s size, then return false.

1. Let _i_ be 0.

1. While _i_ < _searchParamsA_'s size:

    1. If _searchParamsA_\[_i_]\[0] does not equal _searchParamsB_\[_i_]\[0], then return false.

    1. If _searchParamsA_\[_i_]\[1] does not equal _searchParamsB_\[_i_]\[1], then return false.

    1. Set _i_ to _i_ + 1.

1. Return true.

## Examples

Due to how the application/x-www-form-urlencoded parser canonicalizes query strings, there are some cases where query strings which do not appear obviously equivalent, will end up being treated as equivalent after parsing.

So, for example, given any non-default value for `No-Vary-Search`, such as `No-Vary-Search: key-order`, we will have the following equivalences:

{: newline="true"}
<dl>
  <dt>
    <tt>https://example.com</tt><br>
    <tt>https://example.com/?</tt>
  </dt>
  <dd>A null query is parsed the same as an empty string</dd>

  <dt>
    <tt>https://example.com/?a=x</tt><br>
    <tt>https://example.com/?%61=%78</tt>
  </dt>
  <dd>Parsing performs percent-decoding</dd>

  <dt>
    <tt>https://example.com/?a=é</tt><br>
    <tt>https://example.com/?a=%C3%A9</tt>
  </dt>
  <dd>Parsing performs percent-decoding</dd>

  <dt>
    <tt>https://example.com/?a=%f6</tt><br>
    <tt>https://example.com/?a=%ef%bf%bd</tt>
  </dt>
  <dd>Both values are parsed as U+FFFD (�)</dd>

  <dt>
    <tt>https://example.com/?a=x&&&&</tt><br>
    <tt>https://example.com/?a=x</tt>
  </dt>
  <dd>Parsing splits on <tt>&</tt> and discards empty strings</dd>

  <dt>
    <tt>https://example.com/?a=</tt><br>
    <tt>https://example.com/?a</tt>
  </dt>
  <dd>Both parse as having an empty string value for <tt>a</tt></dd>

  <dt>
    <tt>https://example.com/?a=%20</tt><br>
    <tt>https://example.com/?a=+</tt><br>
    <tt>https://example.com/?a= &</tt>
  </dt>
  <dd><tt>+</tt> and <tt>%20</tt> are both parsed as U+0020 SPACE</dd>
</dl>

# Caching {#caching}

If a cache {{HTTP-CACHING}} implements this specification, the presented target URI requirement in {{Section 4 of HTTP-CACHING}} is replaced with:

* one of the following:
  * the presented target URI ({{Section 7.1 of HTTP}}) and that of the stored response match, or
  * the presented target URI and that of the stored response are equivalent modulo search variance ({{comparing}}), given the variance obtained ({{obtain-a-url-search-variance}}) from the stored response.

Cache implementations MAY fail to reuse a stored response whose target URI matches _only_ modulo URL search variance, if the cache has more recently stored a response which:

* has a target URI which is equal to the presented target URI, excluding the query, and
* has a non-empty value for the `No-Vary-Search` field, and
* has a `No-Vary-Search` field value different from the stored response being considered for reuse.

{:aside}
> Caches aren't required to reuse stored responses, generally. However, the above expressly empowers caches to, if it is advantageous for performance or other reasons, search a smaller number of stored responses.
>
> That is, because caches might store more than one response for a given pathname, they need a way to efficiently look up the No-Vary-Search value without accessing all cached responses. Such a cache might take steps like the following to identify a stored response in a performant way, before checking the other conditions in {{Section 4 of HTTP-CACHING}}:
>
> 1. Let exactMatch be cache\[presentedTargetURI\]. If it is a stored response that can be reused, return it.
> 1. Let targetPath be presentedTargetURI, with query parameters removed.
> 1. Let lastNVS be mostRecentNVS\[targetPath\]. If it does not exist, return null.
> 1. Let simplifiedURL be the result of simplifying presentedTargetURI according to lastNVS (by removing query parameters which are not significant, and stable sorting parameters by key, if key order is to be be ignored).
> 1. Let nvsMatch be cache\[simplifiedURL\]. If it does not exist, return null. (It is assumed that this was written when storing in the cache, in addition to the exact URL.)
> 1. Let searchVariance be obtained ({{obtain-a-url-search-variance}}) from nvsMatch.
> 1. If nvsMatch's target URI and presentedTargetURI are not equivalent modulo search variance ({{comparing}}) given searchVariance, then return null.
> 1. If nvsMatch is a stored response that can be reused, return it. Otherwise, return null.

To aid cache implementation efficiency, servers SHOULD NOT send different non-empty values for the `No-Vary-Search` field in response to requests for a given pathname over time, unless there is a need to update how they handle the query component. Doing so would cause cache implementations that use a strategy like the above to miss some stored responses that could otherwise have been reused.

# Security Considerations

The main risk to be aware of is the impact of mismatched URLs. In particular, this could cause the user to see a response that was originally fetched from a URL different from the one displayed when they hovered a link, or the URL displayed in the URL bar.

However, since the impact is limited to query parameters, this does not cross the relevant security boundary, which is the [origin](https://html.spec.whatwg.org/multipage/browsers.html#concept-origin) {{HTML}}. (Or perhaps just the [host](https://url.spec.whatwg.org/#concept-url-host), from [the perspective of web browser security UI](https://url.spec.whatwg.org/#url-rendering-simplification). {{WHATWG-URL}}) Indeed, we have already given origins complete control over how they present the (URL, response body) pair, including on the client side via technology such as [history.replaceState()](https://html.spec.whatwg.org/multipage/nav-history-apis.html#dom-history-replacestate) or service workers.

# Privacy Considerations

This proposal is adjacent to the highly-privacy-relevant space of [navigational tracking](https://privacycg.github.io/nav-tracking-mitigations/#terminology), which often uses query parameters to pass along user identifiers. However, we believe this proposal itself does not have privacy impacts. It does not interfere with [existing navigational tracking mitigations](https://privacycg.github.io/nav-tracking-mitigations/#deployed-mitigations), or any known future ones being contemplated. Indeed, if a page were to encode user identifiers in its URI, the only ability this proposal gives is to *reduce* such user tracking by preventing server processing of such user IDs (since the server is bypassed in favor of the cache). {{NAV-TRACKING-MITIGATIONS}}

# IANA Considerations

IANA should do the following:

## HTTP Field Names

Enter the following into the Hypertext Transfer Protocol (HTTP) Field Name Registry:

Field Name
: `No-Vary-Search`

Status
: permanent

Structured Type
: Dictionary

Reference
: this document

Comments
: (none)

--- back

# Acknowledgments
{:numbered="false"}

This document benefited from valuable reviews and suggestions by:

* Adam Rice
* Julian Reschke
* Kevin McNee
* Liviu Tinta
* Mark Nottingham
* Martin Thomson
* Valentin Gosu
