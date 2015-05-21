## Draft HTTP Extension Specifications

This is the working area for the [IETF HTTP Working Group](https://httpwg.github.io/) draft extensions. Currently, this includes:

### Alternative Services
* [Editors' Draft](https://httpwg.github.io/http-extensions/alt-svc.html) ([plain text](https://httpwg.github.io/http-extensions/alt-svc.txt))
* [Working Group Draft](https://tools.ietf.org/html/draft-ietf-httpbis-alt-svc) (less recent, more official)
* [Open Issues](https://github.com/httpwg/http-extensions/issues?q=is%3Aopen+is%3Aissue+label%3Aalt-svc) / [Document Status](https://datatracker.ietf.org/doc/draft-ietf-httpbis-alt-svc/)

### HTTP Opportunistic Security
* [Editors' Draft](https://httpwg.github.io/http-extensions/encryption.html) ([plain text](https://httpwg.github.io/http-extensions/encryption.txt))
* [Working Group Draft](https://tools.ietf.org/html/draft-ietf-httpbis-http2-encryption) (less recent, more official)
* [Open Issues](https://github.com/httpwg/http-extensions/issues?q=is%3Aopen+is%3Aissue+label%3Aopp-sec) / [Document Status](https://datatracker.ietf.org/doc/draft-ietf-httpbis-http2-encryption/)

### Tunnel Protocol for CONNECT

**IETF Last Call ends 3 Jun 2015.**

* [Editors' Draft](https://httpwg.github.io/http-extensions/tunnel-protocol.html) ([plain text](https://httpwg.github.io/http-extensions/tunnel-protocol.txt))
* [Working Group Draft](https://tools.ietf.org/html/draft-ietf-httpbis-tunnel-protocol) (less recent, more official)
* [Open Issues](https://github.com/httpwg/http-extensions/issues?q=is%3Aopen+is%3Aissue+label%3Atunnel-proto) / [Document Status](https://datatracker.ietf.org/doc/draft-ietf-httpbis-tunnel-protocol/)

### HTTP Authentication-Info Header Field

**in [RFC Editor queue](http://www.rfc-editor.org/queue2.html#draft-ietf-httpbis-auth-info)**

* [Editors' Draft](https://httpwg.github.io/http-extensions/draft-ietf-httpbis-auth-info.html) ([plain text](https://httpwg.github.io/http-extensions/draft-ietf-httpbis-auth-info.txt))
* [Working Group Draft](https://tools.ietf.org/html/draft-ietf-httpbis-auth-info) (less recent, more official)
* [Open Issues](https://github.com/httpwg/http-extensions/issues?q=is%3Aopen+is%3Aissue+label%3Aauth-info) / [Document Status](https://datatracker.ietf.org/doc/draft-ietf-httpbis-auth-info/)

### HTTP Client-Initiated Content-Encoding

* [Editors' Draft](https://httpwg.github.io/http-extensions/draft-ietf-httpbis-cice.html)
* [Working Group Draft](https://tools.ietf.org/html/draft-ietf-httpbis-cice) (less recent, more official)
* [Open Issues](https://github.com/httpwg/http-extensions/issues?q=is%3Aopen+is%3Aissue+label%3Acice) / [Document Status](https://datatracker.ietf.org/doc/draft-ietf-httpbis-cice/)

### HTTP Legally Restricted Status Code

* [Editors' Draft](https://httpwg.github.io/http-extensions/draft-ietf-httpbis-legally-restricted-status.html)
* [Working Group Draft](https://tools.ietf.org/html/draft-ietf-httpbis-legally-restricted-status) (less recent, more official)
* [Open Issues](https://github.com/httpwg/http-extensions/issues?q=is%3Aopen+is%3Aissue+label%3A451) / [Document Status](https://datatracker.ietf.org/doc/draft-ietf-httpbis-legall-restricted-status/)

## Contributing

See [our contribution guidelines](CONTRIBUTING.md) for information about how to
participate.

**Be aware that all contributions to the specification fall under the "NOTE WELL" terms below.**


## Working with the Drafts

If you're an editor, or forking a copy of the draft, a few things to know:

* Pushing to the master branch will automatically generate the HTML on the
  gh-pages branch.
* You'll need xml2rfc, Java and Saxon-HE available. You can override the
  default locations in the environment.  On a Mac with
  [Homebrew](http://brew.sh/), "saxon-b" is the right package.
* For some drafts, you will need [kramdown-rfc2629](https://github.com/cabo/kramdown-rfc2629)
* Some of the make targets require GNU Make 4.0
* Making the txt and html for the latest drafts is done with "make".


## NOTE WELL

Any submission to the [IETF](https://www.ietf.org/) intended by the Contributor
for publication as all or part of an IETF Internet-Draft or RFC and any
statement made within the context of an IETF activity is considered an "IETF
Contribution". Such statements include oral statements in IETF sessions, as
well as written and electronic communications made at any time or place, which
are addressed to:

 * The IETF plenary session
 * The IESG, or any member thereof on behalf of the IESG
 * Any IETF mailing list, including the IETF list itself, any working group
   or design team list, or any other list functioning under IETF auspices
 * Any IETF working group or portion thereof
 * Any Birds of a Feather (BOF) session
 * The IAB or any member thereof on behalf of the IAB
 * The RFC Editor or the Internet-Drafts function
 * All IETF Contributions are subject to the rules of
   [RFC 5378](https://tools.ietf.org/html/rfc5378) and
   [RFC 3979](https://tools.ietf.org/html/rfc3979)
   (updated by [RFC 4879](https://tools.ietf.org/html/rfc4879)).

Statements made outside of an IETF session, mailing list or other function,
that are clearly not intended to be input to an IETF activity, group or
function, are not IETF Contributions in the context of this notice.

Please consult [RFC 5378](https://tools.ietf.org/html/rfc5378) and [RFC
3979](https://tools.ietf.org/html/rfc3979) for details.

A participant in any IETF activity is deemed to accept all IETF rules of
process, as documented in Best Current Practices RFCs and IESG Statements.

A participant in any IETF activity acknowledges that written, audio and video
records of meetings may be made and may be available to the public.
