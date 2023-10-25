---
title: HTTP Proxy-Status Parameter for Next-Hop Aliases
abbrev: DNS Aliases Proxy-Status
docname: draft-ietf-httpbis-alias-proxy-status-latest
date: {DATE}
category: std
area: Applications and Real-Time
workgroup: HTTP

ipr: trust200902
keyword:
 - proxy status

stand_alone: yes
pi: [toc, sortrefs, symrefs]

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/alias-proxy-status
github-issue-label: alias-proxy-status

author:
 -
    ins: T. Pauly
    name: Tommy Pauly
    org: Apple, Inc.
    email: tpauly@apple.com

--- abstract

This document defines the `next-hop-aliases` HTTP Proxy-Status Parameter. This parameter carries
the list of aliases and canonical names an intermediary received during DNS resolution as part
of establishing a connection to the next hop.

--- middle

# Introduction

The Proxy-Status HTTP response field {{!PROXY-STATUS=RFC9209}} allows intermediaries to convey
information about how they handled the request in HTTP responses sent to clients.
It defines a set of parameters that provide information, such as the name of the next
hop.

{{!PROXY-STATUS=RFC9209}} defines a `next-hop` parameter, which can contain a hostname,
IP address, or alias of the next hop. This parameter can contain only one such item,
so it cannot be used to communicate a chain of aliases encountered during DNS resolution
when connecting to the next hop.

Knowing the full chain of names that were used during DNS resolution via CNAME records
{{!DNS=RFC1034}} is particularly useful for clients of forward proxies, in which the
client is requesting to connect to a specific target hostname using the CONNECT method
{{!HTTP=RFC9110}} or UDP proxying {{!CONNECT-UDP=RFC9298}}. CNAME records can be used to
"cloak" hosts that perform tracking or malicious activity behind more innocuous hostnames,
and clients such as web browsers use the chain of DNS names to influence behavior like cookie
usage policies {{?COOKIES=RFC6265}} or blocking of malicious hosts.

This document allows clients to receive the CNAME chain of DNS names for the next hop
by including the list of names in a new `next-hop-aliases` Proxy-Status parameter.

## Requirements

{::boilerplate bcp14}

# next-hop-aliases Parameter {#parameter}

The `next-hop-aliases` parameter's value is a String {{!STRUCTURED-FIELDS=RFC8941}} that contains
one or more DNS names in a comma-separated list. The items in the list include all alias names and
canonical names received in CNAME records {{DNS}} during the course of resolving the next hop's
hostname using DNS, and MAY include the original requested hostname itself. The names SHOULD
appear in the order in which they were received in DNS. If there are multiple CNAME records
in the chain, the first name in the `next-hop-aliases` list would be the value in the CNAME
record for the original hostname, and the final name in the `next-hop-aliases` list would
be the name that ultimately resolved to one or more addresses.

The list of DNS names in `next-hop-aliases` uses a comma (",") as a separator between names.
Note that if a comma is included in a name itself, the comma must be encoded as described in
{{encoding}}.

For example, consider a proxy "proxy.example.net" that receives the following records when
performing DNS resolution for the next hop "host.example.com":

~~~ dns-example
host.example.com.           CNAME   tracker.example.com.
tracker.example.com.        CNAME   service1.example.com.
service1.example.com.       AAAA    2001:db8::1
~~~

The proxy could include the following proxy status in its response:

~~~ http-message
Proxy-Status: proxy.example.net; next-hop="2001:db8::1";
    next-hop-aliases="tracker.example.com,service1.example.com"
~~~

This indicates that proxy.example.net, which used the IP address "2001:db8::1" as the next hop
for this request, encountered the names "tracker.example.com" and "service1.example.com"
in the DNS resolution chain. Note that while this example includes both the `next-hop` and
`next-hop-aliases` parameters, `next-hop-aliases` can be included without including `next-hop`.

The proxy can also include the name of the next hop as the first item in the list. This is
particularly useful for reverse proxies when clients would not otherwise know the name of the
next hop, and the `next-hop` header is used to convey an IP address.

For example, consider a proxy "reverseproxy.example.net" that receives the following records
when performing DNS resolution for the next hop "host.example.com":

~~~ dns-example
host2.example.com.          CNAME   service2.example.com.
service2.example.com.       AAAA    2001:db8::2
~~~

The proxy could include the following proxy status in its response:

~~~ http-message
Proxy-Status: reverseproxy.example.net; next-hop="2001:db8::2";
    next-hop-aliases="host2.example.com,service2.example.com"
~~~

The `next-hop-aliases` parameter only applies when DNS was used to resolve the next hop's name, and
does not apply in all situations. Clients can use the information in this parameter to determine
how to use the connection established through the proxy, but need to gracefully handle situations
in which this parameter is not present.

The proxy MAY send the empty string ("") as the value of `next-hop-aliases` to indicate that
no CNAME records were encountered when resolving the next hop's name.

## Encoding special characters {#encoding}

DNS names commonly just contain alphanumeric characters and hyphens ("-"), although they
are allowed to contain any character ({{?RFC1035, Section 3.1}}), including a comma. To
prevent commas or other special characters in names leading to incorrect parsing,
any characters that appear in names in this list that do not belong to the set of URI
Unreserved Characters ({{!RFC3986, Section 2.3}}) MUST be percent-encoded as
defined in {{!RFC3986, Section 2.1}}.

For example, consider the DNS name `comma,name.example.com`. This name would be encoded
within a `next-hop-aliases` parameter as follows:

~~~ http-message
Proxy-Status: proxy.example.net; next-hop="2001:db8::1";
    next-hop-aliases="comma%2Cname.example.com,service1.example.com"
~~~

It is also possible for a DNS name to include a period character (".") within a label,
instead of as a label separator. In this case, the period character MUST be first escaped
as "\\.". Since the "\\" character itself will be percent-encoded, the name
"dot\\.label.example.com" would be encoded within a `next-hop-aliases` parameter as follows:

~~~ http-message
Proxy-Status: proxy.example.net; next-hop="2001:db8::1";
    next-hop-aliases="dot%5C.label.example.com,service1.example.com"
~~~

Upon parsing this name, "dot%5C.label" MUST be treated as a single label.

Similarly the "\\" character in a label MUST be escaped as "\\\\" and then percent-encoded.
Other uses of "\\" MUST NOT appear in the label after percent-decoding. For example,
if there is a DNS name `backslash\\name.example.com`, it would first be escaped as
`backslash\\\\name.example.com`, and the percent-encoded as follows:

~~~ http-message
Proxy-Status: proxy.example.net; next-hop="2001:db8::1";
    next-hop-aliases="backslash%5C%5Cname.example.com,service1.example.com"
~~~

# Implementation Considerations

In order to include the `next-hop-aliases` parameter, a proxy needs to have access to the chain
of alias names and canonical names received in CNAME records.

Implementations ought to note that the full chain of names might not be available in common DNS
resolution APIs, such as `getaddrinfo`. `getaddrinfo` does have an option for `AI_CANONNAME`,
but this will only return the last name in the chain (the canonical name), not the alias
names.

An implementation MAY include incomplete information in the `next-hop-aliases` parameter to accommodate cases where it is unable to include the full chain, such as only including the canonical name if the implementation can only use `getaddrinfo` as described above.

# Security Considerations {#sec-considerations}

The `next-hop-aliases` parameter does not include any DNSSEC information or imply that DNSSEC was used.
The information included in the parameter can only be trusted to be valid insofar as the client
trusts the proxy to provide accurate information. This information is intended to be used as
a hint, and SHOULD NOT be used for making security decisions about the identity of a resource accessed
through the proxy.

Inspecting CNAME chains can be used to detect cloaking of trackers or malicious hosts. However, the
CNAME records could be omitted by a recursive or authoritative resolver that is trying to hide this form of cloaking.
In particular, recursive or authoritative resolvers can omit these records for both clients directly performing DNS name
resolution and proxies performing DNS name resolution on behalf of client. A malicious proxy could
also choose to not report these CNAME chains in order to hide the cloaking. In general, clients can
trust information included (or not included) in the `next-hop-aliases` parameter to the degree
that the proxy and any resolvers used by the proxy are trusted.

# IANA Considerations

This document registers the "next-hop-aliases" parameter
in the "HTTP Proxy-Status Parameters" registry
<[](https://www.iana.org/assignments/http-proxy-status)>.

Name:
: next-hop-aliases

Description:
: A string containing one or more DNS aliases or canonical names used to establish a
proxied connection to the next hop.

Reference:
: This document
