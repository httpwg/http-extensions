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

This document defines an HTTP Proxy-Status Parameter that contains a list of aliases
received over DNS when establishing a connection to the next hop.

--- middle

# Introduction

The Proxy-Status HTTP response field {{!PROXY-STATUS=RFC9209}} allows proxies to convey
information about how a proxied request was handled in HTTP responses sent to clients.
It defines a set of parameters that provide information, such as the name of the next
hop.

{{!PROXY-STATUS=RFC9209}} defines a `next-hop` parameter, which can contain a hostname,
IP address, or alias of the next hop. This parameter can contain only one such item,
so it cannot be used to communicate a chain of aliases encountered during DNS resolution
when connecting to the next hop.

Knowing the full chain of aliases that were used during DNS resolution is particularly
useful for clients of forward proxies, in which the client is requesting to connect
to a specific target hostname using the CONNECT method {{!HTTP=RFC9110}} or
UDP proxying {{!CONNECT-UDP=RFC9298}}. DNS aliases can be used to "cloak" hosts that
perform tracking or malicious activity behind more innocuous hostnames, and clients
such as web browsers use the chain of DNS aliases to influence behavior like cookie
usage policies {{?COOKIES=RFC6265}} or blocking of malicious hosts.

This document allows clients to receive the chain of DNS aliases for the next hop
by including the list of names in a new `next-hop-aliases` Proxy-Status parameter.

## Requirements

{::boilerplate bcp14}

# next-hop-aliases Parameter {#parameter}

The `next-hop-aliases` parameter's value is a String that contains one or more DNS names in
a comma-separated list. The items in the list include all names received in CNAME
records {{!DNS=RFC1912}} during the course of resolving the next hop's hostname using DNS.
Since DNS names can include comma (`,`) characters in them, any commas that appear in a DNS
names MUST be represented using a percent-encoded `%2C` value instead. The aliases SHOULD
appear in the order in which they were received in DNS; that is, if a name has a CNAME record
with a first alias, which has a CNAME record for a second alias, the aliases should appear
in that order.

For example:

~~~ example
Proxy-Status: proxy.example.net; next-hop=2001:db8::1;
    next-hop-aliases="tracker.example.com.,service1.example-cdn.com."
~~~

indicates that proxy.example.net, which used the IP address "2001:db8::1" as the next hop
for this request, encountered the CNAMEs "tracker.example.com." and "service1.example-cdn.com"
in the DNS resolution chain. Note that while this example includes both the `next-hop` and
`next-hop-aliases` parameters, `next-hop-aliases` can be included without including `next-hop`.

The `next-hop-aliases` parameter only applies when DNS was used to resolve the next hop's name, and
does not apply in all situations. Clients can use the information in this parameter to determine
how to use the connection established through the proxy, but need to gracefully handle situations
in which this parameter is not present.

# Security Considerations {#sec-considerations}

The `next-hop-aliases` parameter does not include any DNSSEC information or imply that DNSSEC was used.
The information included in the parameter can only be trusted to be valid insofar as the client
trusts its proxy to provide accurate information. This information is intended to be used as
a hint, and SHOULD NOT be used for making security decisions about the identity of a resource accessed
through the proxy.

# IANA Considerations

This document registers the "next-hop-aliases" parameter
in the "HTTP Proxy-Status Parameters" registry
<[](https://www.iana.org/assignments/http-proxy-status)>.

Name:
: next-hop-aliases

Description:
: A string containing one or more DNS alises used to establish a proxied connection
to the next hop.

Reference:
: This document
