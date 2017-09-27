---
title: Cookie Prefixes
docname: draft-ietf-httpbis-cookie-prefixes-00
date: 2017
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
  RFC2109:
  POWERFUL-FEATURES:
    target: https://www.chromium.org/Home/chromium-security/prefer-secure-origins-for-powerful-new-features
    title: "Prefer Secure Origins for Powerful New Features"
    date: 2015
    author:
      ins: C. Palmer
      name: Chris Palmer

  SECURE-CONTEXTS:
    target: https://w3c.github.io/webappsec-secure-contexts/
    title: "Secure Contexts"
    date: 2016
    author:
      ins: M. West
      name: Mike West

  DEPRECATING-HTTP:
    target: https://blog.mozilla.org/security/2015/04/30/deprecating-non-secure-http/
    title: "Deprecating Non-Secure HTTP"
    date: 2015-04-30
    author:
      ins: R. Barnes
      name: Richard Barnes

  Lawrence2015:
    target: http://textslashplain.com/2015/10/09/duct-tape-and-baling-wirecookie-prefixes/
    title: "Duct Tape and Baling Wire -- Cookie Prefixes"
    date: 2015-10-09
    author:
      ins: E. Lawrence
      name: Eric Lawrence

--- abstract

This document updates RFC6265 by adding a set of restrictions upon the names
which may be used for cookies with specific properties. These restrictions
enable user agents to smuggle cookie state to the server within the confines
of the existing `Cookie` request header syntax, and limits the ways in which
cookies may be abused in a conforming user agent.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list 
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source 
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/cookie-prefixes>.

--- middle

# Introduction

Section 8.5 and Section 8.6 of {{RFC6265}} spell out some of the drawbacks of
cookies' implementation: due to historical accident, it is impossible for a
server to have confidence that a cookie set in a secure way (e.g., as a
domain cookie with the `Secure` (and possibly `HttpOnly`) flags set) remains
intact and untouched by non-secure subdomains.

We can't alter the syntax of the `Cookie` request header, as that would likely
break a number of implementations. This rules out sending a cookie's flags along
with the cookie directly, but we can smuggle information along with the cookie
if we reserve certain name prefixes for cookies with certain properties.

This document describes such a scheme, which enables servers to set cookies
which conforming user agents will ensure are `Secure`, and locked to a domain.

# Terminology and notation

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in {{RFC2119}}.

The `scheme` component of a URI is defined in Section 3 of {{RFC3986}}.

# Prefixes

## The "__Secure-" prefix

If a cookie's name begins with "__Secure-", the cookie MUST be:

1.  Set with a `Secure` attribute

2.  Set from a URI whose `scheme` is considered "secure" by the user agent.

The following cookie would be rejected when set from any origin, as the `Secure`
flag is not set

    Set-Cookie: __Secure-SID=12345; Domain=example.com

While the following would be accepted if set from a secure origin (e.g.
`https://example.com/`), and rejected otherwise:

    Set-Cookie: __Secure-SID=12345; Secure; Domain=example.com

## The "__Host-" prefix

If a cookie's name begins with "__Host-", the cookie MUST be:

1.  Set with a `Secure` attribute

2.  Set from a URI whose `scheme` is considered "secure" by the user agent.

3.  Sent only to the host which set the cookie. That is, a cookie named
    "__Host-cookie1" set from `https://example.com` MUST NOT contain a `Domain`
    attribute (and will therefore be sent only to `example.com`, and not to
    `subdomain.example.com`).

4.  Sent to every request for a host. That is, a cookie named "__Host-cookie1"
    MUST contain a `Path` attribute with a value of "/".

The following cookies would always be rejected:

    Set-Cookie: __Host-SID=12345
    Set-Cookie: __Host-SID=12345; Secure
    Set-Cookie: __Host-SID=12345; Domain=example.com
    Set-Cookie: __Host-SID=12345; Domain=example.com; Path=/
    Set-Cookie: __Host-SID=12345; Secure; Domain=example.com; Path=/

While the following would be accepted if set from a secure origin (e.g.
`https://example.com/`), and rejected otherwise:

    Set-Cookie: __Host-SID=12345; Secure; Path=/

# User Agent Requirements

This document updates Section 5.3 of {{RFC6265}} as follows:

After step 10 of the current algorithm, the cookies flags are set. Insert the
following steps to perform the prefix checks this document specifies:

11.  If the `cookie-name` begins with the string "__Secure-" or "__Host-",
     abort these steps and ignore the cookie entirely unless both of the
     following conditions are true:

     *   The cookie's `secure-only-flag` is `true`

     *   `request-uri`'s `scheme` component denotes a "secure" protocol (as
         determined by the user agent)

12.  If the `cookie-name` begins with the string "__Host-", abort these
     steps and ignore the cookie entirely unless the following conditions are
     true:

     *   The cookie's `host-only-flag` is `true`

     *   The cookie's `path` is "/"

# Aesthetic Considerations

## Not pretty.

Prefixes are ugly. :(

## Why "__"?

We started with `$`, but ran into issues with servers that had implemented
{{RFC2109}}-style cookies. `__` is a prefix used for a number of well-known
cookies in the wild (notably Google Analytics's `__ut*` cookies, and
CloudFlare's `__cfduid`), and so is unlikely to produce such compatibility
issues, while being uncommon enough to mitigate the risk of collisions.

# Security Considerations

## Secure Origins Only

It would certainly be possible to extend this scheme to non-secure origins (and
an earlier draft of this document did exactly that). User agents, however, are
slowly moving towards a world where features with security implications are
available only over secure transport (see {{SECURE-CONTEXTS}},
{{POWERFUL-FEATURES}}, and {{DEPRECATING-HTTP}}). This document follows that
trend, limiting exciting new cookie properties to secure transport in order to
ensure that user agents can make claims which middlemen will have a hard time
violating.

To that end, note that the requirements listed above mean that prefixed cookies
will be rejected entirely if a non-secure origin attempts to set them.

## Limitations

This scheme gives no assurance to the server that the restrictions on cookie
names are enforced. Servers could certainly probe the user agent's functionality
to determine support, or sniff based on the `User-Agent` request header, if
such assurances were deemed necessary.

--- back

# Acknowledgements

Eric Lawrence had this idea a million years ago, and wrote about its genesis in
{{Lawrence2015}}. Devdatta Akhawe helped justify the potential impact of the
scheme on real-world websites. Thomas Broyer pointed out the issues with a
leading `$` in the prefixes, and Brian Smith provided valuable contributions to
the discussion around a replacement (ISO C indeed).
