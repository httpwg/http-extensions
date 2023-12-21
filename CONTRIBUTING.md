---
title: Contributing to HTTP
description: How to participate in the HTTP Working Group
---

Anyone can contribute to HTTP; you don't have to join the Working Group, because there is no "membership" -- anyone who participates in the work, as outlined below, is part of the HTTP Working Group.

Before doing so, it's a good idea to familiarize yourself with our [charter](https://datatracker.ietf.org/wg/httpbis/about/), and [home page](https://httpwg.org/). If you're new to the [IETF](https://www.ietf.org/), you may also want to read [an informal guide to the IETF process](https://www.ietf.org/standards/process/informal/) and the [Tao of the IETF](https://www.ietf.org/tao.html).

**Be aware that all contributions fall under the "NOTE WELL" terms outlined below.**

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Contributing to Work in Progress](#contributing-to-work-in-progress)
  - [Following Discussion](#following-discussion)
  - [Raising Issues](#raising-issues)
  - [Resolving Issues](#resolving-issues)
  - [Pull Requests](#pull-requests)
- [Proposing New Work](#proposing-new-work)
  - [Other Venues for HTTP Work](#other-venues-for-http-work)
  - [Bringing Work to the IETF](#bringing-work-to-the-ietf)
- [Code of Conduct](#code-of-conduct)
- [NOTE WELL](#note-well)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Contributing to Work in Progress

### Following Discussion

The HTTP Working Group has a few venues for discussion:

* We have a session at most [IETF meetings](https://www.ietf.org/meeting/), and sometimes in between (called an "interim" meeting). See our [meeting materials repository](https://httpwg.org/wg-materials), and the [official IETF proceedings](https://datatracker.ietf.org/wg/httpbis/meetings/) for details.

* Our [mailing list](https://lists.w3.org/Archives/Public/ietf-http-wg/) ([subscribe](mailto:ietf-http-wg-request@w3.org?subject=subscribe)) is used for notifications of meetings, adoption of documents, consensus calls, issue discussion, and other business. It's not mandatory to subscribe, but you're likely to miss important things if you don't; also, note that e-mail sent to this list will be manually moderated (and thus delayed) if you are not subscribed.

* We discuss most document issues on [GitHub](https://github.com/httpwg/).

You can participate in any or all of these places.


### Raising Issues

We use GitHub to track discussion items and their resolution. Before filing a new issue, please consider a few things:

* Issues should be just that: issues with our deliverables, **not proposals for new work, questions, or support requests**.

* There may be an existing duplicate issue, so please review the issues list first.

* If you're not sure how to phrase your issue, please ask on the [mailing list](#following-discussion).

Issues can also be raised on the [mailing list](#following-discussion) by clearly marking them as such (e.g., with `New issue` in the `Subject:` line).

Be aware that issues might be rephrased, changed in scope, or combined with others. If you feel that an important part of your original issue has been lost, please bring it up (on the issue or on the list).

Off-topic and duplicate issues will be closed without discussion. Note that commit comments will only be responded to with best effort, and may not be seen.


### Resolving Issues

As in all IETF Working Groups, final consensus of the Working Group is determined during Working Group Last Call; consensus established during issue discussion provides a limited precedent, to prevent revisiting topics unnecessarily. Our issues list provides a mechanism for tracking those discussions and their outcomes.

Some issues might be labeled as `editorial`; they can be dealt with by the editor(s) without consensus or notification, and discussion will take place on the issue itself. If you believe an `editorial` issue is not purely editorial, please say so on the issue; the Chair(s) will make a determination.

The remaining `open` issues in the issues list are those that need Working Group discussion.

Issues can be discussed on the mailing list or the issues list. The editors can also propose resolutions to issues for the group's consideration by incorporating them into the draft(s).

When an issue is `closed`, it implies that the issue's proposed resolution is reflected in the draft(s). When a new draft is published, the issues that have been closed since the last draft will be highlighted in the draft's change notes and/or on the mailing list, to aid reviewers.

Note that whether or not an issue is closed does not necessarily reflect consensus of the Working Group; an issue's `open`/`closed` state is only used to organise our discussions. If you have a question or problem with an issue in the `closed` state, please say so (either on the issue or the mailing list).

Some issues might require an explicit consensus call; if consensus is achieved in this manner, the issue will be labeled with `has-consensus`. Reopening issues with `has-consensus` requires new information (in the judgement of the Chairs).


### Pull Requests

We welcome pull requests, both for editorial suggestions and to resolve open issues. In the latter case, please identify the relevant issue.

Please do not use a pull request to open a new issue. Instead, file an issue and refer to it from the pull request.


## Proposing New Work

If you'd like to propose a new HTTP extension (e.g., method, header, status code, HTTP/2 or HTTP/3 SETTINGS), it's best to first describe your use case on the [mailing list](#following-discussion). Often, there's an existing HTTP feature that can be used.

If a new extension is necessary, we usually discuss them in Internet-Draft form. However, if you're unfamiliar with that format, write down your proposal precisely but succinctly and send it to the [mailing list](#following-discussion).

If there is interest in the proposal, the Chairs will issue a _Call for Adoption_, where Working Group participants comment on whether or not they support adoption, and whether or not they might implement it.

Upcoming proposals and calls for adoption are tracked by the Chairs in the [admin repository](https://github.com/httpwg/admin/labels/adoption).

If the Chairs determine that there is consensus to adopt the document, the Working Group will start discussing it.

Once a draft is adopted, the Chairs will assign one or more editors to the document. Although this will sometimes be the same person(s) that made the original proposal, it might not be, for various reasons; it could be that an experienced editor is needed for a tricky draft, or your contribution as a participant, rather than a neutral editor, is judged more valuable. In any case, the Chairs will discuss editor selection with you before making an announcement.

The Editor(s) first task will be to upload an initial draft into a Working Group repository. If you're selected as an editor, the Chairs will be in touch with more details.

### Other Venues for HTTP Work

There are other places inside and outside the IETF that are doing HTTP-related work. Depending on the nature of your proposal, you might consider taking your work to one of the following venues:

* The [HTTP APIs Working Group](https://datatracker.ietf.org/wg/httpapi/about/) focuses on API-related HTTP extensions and similar specifications
* The [DISPATCH Working Group](https://datatracker.ietf.org/wg/dispatch/about/) decides where it's most appropriate to take new work in the IETF's Applications and RealTime (ART) area. While you can come directly to the HTTP Working Group with a proposal, you can also take it there. Sometimes that can lead to starting a new Working Group (often for larger or more specialised work)
* The [WHATWG Fetch Specification](https://fetch.spec.whatwg.org/) defines the API for HTTP that browsers expose

### Bringing Work to the IETF

There are a few things that are important to know when you bring work to the IETF. 

First, when your draft is adopted by the Working Group _change control_ -- that is, who determines what's in the specification -- passes from you to the IETF. That means that some things that you don't agree with might happen to it, and it might be published with things that you wouldn't have included (or without things that you would have kept).

That's because the document's content is determined by consensus of the Working Group, and then the IETF overall. Even though you started it, the document needs to reflect the community's input, and that takes primacy.

As a result, whenever a document is adopted it's considered a _starting point_ -- i.e., nothing is "locked down". Of course, you will have ample opportunity to discuss any issues you have with proposed changes, and if you make a convincing argument, consensus should follow. However, it's important that you are able to accept that the document will change. If you just want it rubber-stamped, it's not appropriate to bring it to the IETF.

Why should you bring your document here, if you have to give up control? Not only will your work benefit from the broad review from many HTTP implementers and practitioners, but that community will also be more likely to implement and use an extension once it has gone through that process.


## Code of Conduct

The [IETF Guidelines for Conduct](https://www.rfc-editor.org/rfc/rfc7154.html) applies to all Working Group communications and meetings.


## NOTE WELL

This is a reminder of IETF policies in effect on various topics such as patents or code of conduct. It is only meant to point you in the right direction. Exceptions may apply. The IETF's patent policy and the definition of an IETF "contribution" and "participation" are set forth in BCP 79; please read it carefully.

As a reminder:

- By participating in the IETF, you agree to follow IETF processes and policies.
- If you are aware that any IETF contribution is covered by patents or patent applications that are owned or controlled by you or your sponsor, you must disclose that fact, or not participate in the discussion.
- As a participant in or attendee to any IETF activity you acknowledge that written, audio, video, and photographic records of meetings may be made public.
- Personal information that you provide to IETF will be handled in accordance with the IETF Privacy Statement.
- As a participant or attendee, you agree to work respectfully with other participants; please contact the [ombudsteam](https://www.ietf.org/contact/ombudsteam/) if you have questions or concerns about this.

Definitive information is in the documents listed below and other IETF BCPs. For advice, please talk to WG chairs or ADs:

- [BCP 9](https://www.rfc-editor.org/info/bcp9) (Internet Standards Process)
- [BCP 25](https://www.rfc-editor.org/info/bcp25) (Working Group processes)
- [BCP 25](https://www.rfc-editor.org/info/bcp25) (Anti-Harassment Procedures)
- [BCP 54](https://www.rfc-editor.org/info/bcp54) (Code of Conduct)
- [BCP 78](https://www.rfc-editor.org/info/bcp78) (Copyright)
- [BCP 79](https://www.rfc-editor.org/info/bcp79) (Patents, Participation)
- [https://www.ietf.org/privacy-policy/](https://www.ietf.org/privacy-policy/) (Privacy Policy)