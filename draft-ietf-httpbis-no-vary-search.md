---
title: No-Vary-Search
abbrev:
category: std

docname: draft-ietf-httpbis-no-vary-search-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: "Applications"
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

A proposed HTTP header field for changing how URL search parameters impact caching.

--- middle

# Conventions and Definitions

{::boilerplate bcp14-tagged}

This document also adopts some conventions and notation typical in WHATWG and W3C usage, especially as it relates to algorithms. See {{WHATWG-INFRA}}.

# HTTP header field definition

The `No-Vary-Search` HTTP header field is a structured field {{STRUCTURED-FIELDS}} whose value must be a dictionary ({{Section 3.2 of STRUCTURED-FIELDS}}).

<!--
TODO: probably give some more introductory non-normative text. Look at what other HTTP field defintions do.
-->

It has the following authoring conformance requirements:

* If present, the `key-order` entry's value must be a boolean ({{Section 3.3.6 of STRUCTURED-FIELDS}}).
* If present, the `params` entry's value must be either a boolean ({{Section 3.3.6 of STRUCTURED-FIELDS}}) or an inner list ({{Section 3.1.1 of STRUCTURED-FIELDS}}).
* If present, the `except` entry's value must be an inner list ({{Section 3.1.1 of STRUCTURED-FIELDS}}).
* The `except` entry must only be present if the `params` entry is also present, and the `params` entry's value is the boolean value true.

The dictionary may contain entries whose keys are not one of `key-order`, `params`, and `except`, but their meaning is not defined by this specification. Implementations of this specification will ignore such entries (but future documents may assign meaning to such entries).

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

# Parsing

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
| `No-Vary-Search: params=?0`                       | (omit the header)                                 |
| `No-Vary-Search: params=()`                       | (omit the header)                                 |
| `No-Vary-Search: key-order=?0`                    | (omit the header)                                 |

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

The parse a key algorithm allows encoding non-ASCII key strings in the ASCII structured header format, similar to how the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded) format {{WHATWG-URL}} allows encoding an entire entry list of keys and values in ASCII URL format. For example,

~~~~http-message
No-Vary-Search: params=("%C3%A9+%E6%B0%97")
~~~~

will result in a URL search variance whose vary params are « "`é 気`" ». As explained in a later example, the canonicalization process during equivalence testing means this will treat as equivalent URL strings such as:

<!-- link "a later example" and "equivalence testing" -->

* `https://example.com/?é 気=1`
* `https://example.com/?é+気=2`
* `https://example.com/?%C3%A9%20気=3`
* `https://example.com/?%C3%A9+%E6%B0%97=4`

and so on, since they all are [parsed](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} to having the same key "`é 気`".

# Comparing

(((!equivalent modulo search variance)))
Two [URLs](https://url.spec.whatwg.org/#concept-url) {{WHATWG-URL}} _urlA_ and _urlB_ are _equivalent modulo search variance_ given a URL search variance _searchVariance_ if the following algorithm returns true:

1. If the scheme, username, password, host, port, or path of _urlA_ and _urlB_ differ, then return false.

1. If _searchVariance_ is equivalent to the default URL search variance, then:

    1. If _urlA_'s query equals _urlB_'s query, then return true.

    1. Return false.

    In this case, even URL pairs that might appear the same after running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} on their queries, such as `https://example.com/a` and `https://example.com/a?`, or `https://example.com/foo?a=b&&&c` and `https://example.com/foo?a=b&c=`, will be treated as inequivalent.

1. Let _searchParamsA_ and _searchParamsB_ be empty lists.

1. If _wrlA_'s query is not null, then set _searchParamsA_ to the result of running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} given the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _urlA_'s query.

1. If _wrlB_'s query is not null, then set _searchParamsB_ to the result of running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} given the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _urlB_'s query.

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

# Security Considerations

The main risk to be aware of is the impact of mismatched URLs. In particular, this could cause the user to see a response that was originally fetched from a URL different from the one displayed when they hovered a link, or the URL displayed in the URL bar.

However, since the impact is limited to query parameters, this does not cross the relevant security boundary, which is the [origin](https://html.spec.whatwg.org/multipage/browsers.html#concept-origin) {{HTML}}. (Or perhaps just the [host](https://url.spec.whatwg.org/#concept-url-host), from [the perspective of web browser security UI](https://url.spec.whatwg.org/#url-rendering-simplification). {{WHATWG-URL}}) Indeed, we have already given origins complete control over how they present the (URL, reponse body) pair, including on the client side via technology such as [history.replaceState()](https://html.spec.whatwg.org/multipage/nav-history-apis.html#dom-history-replacestate) or service workers.

# Privacy Considerations

This proposal is adjacent to the highly-privacy-relevant space of [navigational tracking](https://privacycg.github.io/nav-tracking-mitigations/#terminology), which often uses query parameters to pass along user identifiers. However, we believe this proposal itself does not have privacy impacts. It does not interfere with [existing navigational tracking mitigations](https://privacycg.github.io/nav-tracking-mitigations/#deployed-mitigations), or any known future ones being contemplated. Indeed, if a page were to encode user identifiers in its URL, the only ability this proposal gives is to *reduce* such user tracking by preventing server processing of such user IDs (since the server is bypassed in favor of the cache). {{NAV-TRACKING-MITIGATIONS}}

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

TODO acknowledge.
