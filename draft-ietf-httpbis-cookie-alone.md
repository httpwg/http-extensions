---
title: Deprecate modification of 'secure' cookies from non-secure origins
abbrev: Leave Secure Cookies Alone
docname: draft-ietf-httpbis-cookie-alone-00
date: 2016
category: std
updates: 6265

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft
keyword: Cookie

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, subcompact, comments, inline]

author:
-
  ins: M. West
  name: Mike West
  organization: Google, Inc
  email: mkwst@google.com
  uri: https://mikewest.org/

normative:
  RFC2119:
  RFC3986:
  RFC6265:

informative:
  COOKIE-INTEGRITY:
    target: https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/zheng
    title: "Cookies Lack Integrity: Real-World Implications"
    date: 2015-08
    author:
    -
      ins: X. Zheng
      name: Xiaofeng Zheng
      organization: Tsinghua University and Tsinghua National Laboratory for Information Science and Technology
    -
      ins: J. Jiang
      name: Jian Jiang
      organization: University of California, Berkeley
    -
      ins: J. Liang
      name: Jinjin Liang
      organization: Tsinghua University and Tsinghua National Laboratory for Information Science and Technology;
    -
      ins: H. Duan
      name: Haixin Duan
      organization: Tsinghua University, Tsinghua National Laboratory for Information Science and Technology, and International Computer Science Institute;
    -
      ins: S. Chen
      name: Shuo Chen
      organization: Microsoft Research Redmond;
    -
      ins: T. Wan
      name: Tao Wan
      organization: Huawei Canada
    -
      ins: N. Weaver
      name: Nicholas Weaver
      organization: International Computer Science Institute and University of California, Berkeley
  COOKIE-PREFIXES:
    target: https://tools.ietf.org/html/draft-ietf-httpbis-cookie-prefixes
    title: "Cookie Prefixes"
    date: 2016
    author:
    -
      ins: M. West
      name: Mike West
      organization: Google, Inc
  HSTS-PRELOADING:
    target: https://hstspreload.appspot.com/
    title: "HSTS Preload Submission"
  RFC6797:

--- abstract

This document updates RFC6265 by removing the ability for a non-secure origin
to set cookies with a 'secure' flag, and to overwrite cookies whose 'secure'
flag is set. This deprecation improves the isolation between HTTP and HTTPS
origins, and reduces the risk of malicious interference.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list 
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source 
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/cookie-alone>.

--- middle

# Introduction

Section 8.5 and Section 8.6 of {{RFC6265}} spell out some of the drawbacks of
cookies' implementation: due to historical accident, non-secure origins can set
cookies which will be delivered to secure origins in a manner indistinguishable
from cookies set by that origin itself. This enables a number of attacks, which
have been recently spelled out in some detail in {{COOKIE-INTEGRITY}}.

We can mitigate the risk of these attacks by making it more difficult for
non-secure origins to influence the state of secure origins. Accordingly, this
document recommends the deprecation and removal of non-secure origins' ability
to write cookies with a 'secure' flag, and their ability to overwrite cookies
whose 'secure' flag is set.

# Terminology and notation

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in {{RFC2119}}.

The `scheme` component of a URI is defined in Section 3 of {{RFC3986}}.

# Recommendations

This document updates Section 5.3 of {{RFC6265}} as follows:

1.  After step 8 of the current algorithm, which sets the cookie's
    `secure-only-flag`, execute the following step:

    9.  If the `scheme` component of the `request-uri` does not denote a
        "secure" protocol (as defined by the user agent), and the cookie's
        `secure-only-flag` is `true`, then abort these steps and ignore the
        newly created cookie entirely.

2.  Before step 11, execute the following step:

    11. If the newly created cookie's `secure-only-flag` is not set, and the
        `scheme` component of the `request-uri` does not denote a "secure"
        protocol, then abort these steps and ignore the newly created cookie
        entirely if the cookie store contains one or more cookies that meet all
        of the following criteria:

        1.  Their `name` matches the `name` of the newly created cookie.

        2.  Their `secure-only-flag` is set.

        3.  Their `domain` domain-matches the `domain` of the newly created
            cookie, or vice-versa.

        Note: This comparison intentionally ignores the `path` component. The
        intent is to allow the `secure` flag to supercede the `path`
        restrictions to protect sites against cookie fixing attacks.

        Note: This allows "secure" pages to override `secure` cookies with
        non-secure variants. Perhaps we should restrict that as well?

3.  In order to ensure that a non-secure site can never cause a `secure` cookie
    to be evisted, adjust the "remove excess cookies" priority order at the
    bottom of Section 5.3 to be the following:

    1.  Expired cookies.

    2.  Cookies whose `secure-only-flag` is not set and which share a
        `domain` field with more than a predetermined number of other cookies.

    3.  Cookies that share a `domain` field with more than a predetermined
        number of other cookies.

    4.  All cookies.

    Note that the eviction algorithm specified here is triggered only after
    insertion of a cookie which causes the user agent to exceed some
    predetermined upper bound. Conforming user agents MUST ensure that inserting
    a non-secure cookie does not cause a secure cookie to be removed.

# Security Considerations

This specification increases a site's confidence that secure cookies it sets
will remain unmodified by insecure pages on hosts which it domain-matches.
Ideally, sites would use HSTS as described in {{RFC6797}} to defend more
robustly against the dangers of non-secure transport in general, but until
adoption of that protection becomes ubiquitous, this deprecation this document
recommends will mitigate a number of risks.

The mitigations in this document do not, however, give complete confidence that
a given cookie was set securely. If an attacker is able to impersonate a
response from `http://example.com/` before a user visits `https://example.com/`,
the user agent will accept any cookie that the insecure origin sets, as the
"secure" cookie won't yet be present in the user agent's cookie store. An
active network attacker may still be able to use this ability to mount an attack
against `example.com`, even if that site uses HTTPS exclusively.

The proposal in {{COOKIE-PREFIXES}} could mitigate this risk, as could
"preloading" HSTS for `example.com` into the user agent {{HSTS-PRELOADING}}.

--- back

# Acknowledgements

Richard Barnes encouraged a formalization of the deprecation proposal.
{{COOKIE-INTEGRITY}} was a useful exploration of the issues {{RFC6265}}
described.
