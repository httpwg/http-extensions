# Document Shepherd Write-Up for Group Documents

*This version is dated 4 July 2022.*

Thank you for your service as a document shepherd. Among the responsibilities is
answering the questions in this write-up to give helpful context to Last Call
and Internet Engineering Steering Group ([IESG][1]) reviewers, and your
diligence in completing it is appreciated. The full role of the shepherd is
further described in [RFC 4858][2]. You will need the cooperation of the authors
and editors to complete these checks.

Note that some numbered items contain multiple related questions; please be sure
to answer all of them.

## Document History

1. Does the working group (WG) consensus represent the strong concurrence of a
   few individuals, with others being silent, or did it reach broad agreement?

_Fairly broad agreement._

2. Was there controversy about particular points, or were there decisions where
   the consensus was particularly rough?

_There was some discussion of how many compression algorithms to include. Although there were diverse opinions, we converged on the approach taken in the draft._

3. Has anyone threatened an appeal or otherwise indicated extreme discontent? If
   so, please summarize the areas of conflict in separate email messages to the
   responsible Area Director. (It should be in a separate email because this
   questionnaire is publicly available.)

_No._

4. For protocol documents, are there existing implementations of the contents of
   the document? Have a significant number of potential implementers indicated
   plans to implement? Are any existing implementations reported somewhere,
   either in the document itself (as [RFC 7942][3] recommends) or elsewhere
   (where)?

_Yes; Chrome has implemented on the client side, and several parties have indicated interest and/or intent to implement on the server side._

## Additional Reviews

5. Do the contents of this document closely interact with technologies in other
   IETF working groups or external organizations, and would it therefore benefit
   from their review? Have those reviews occurred? If yes, describe which
   reviews took place.

_Yes; there are browser-specific implementation considerations that have been coordinated with the W3C and WHATWG._

6. Describe how the document meets any required formal expert review criteria,
   such as the MIB Doctor, YANG Doctor, media type, and URI type reviews.

*Routine HTTP-related registry reviews need to happen as part of IETF LC; no issues anticipated.*

7. If the document contains a YANG module, has the final version of the module
   been checked with any of the [recommended validation tools][4] for syntax and
   formatting validation? If there are any resulting errors or warnings, what is
   the justification for not fixing them at this time? Does the YANG module
   comply with the Network Management Datastore Architecture (NMDA) as specified
   in [RFC 8342][5]?

_No YANG here._

8. Describe reviews and automated checks performed to validate sections of the
   final version of the document written in a formal language, such as XML code,
   BNF rules, MIB definitions, CBOR's CDDL, etc.

*HTTP structured fields syntax have been checked with a linter.*


## Document Shepherd Checks

9. Based on the shepherd's review of the document, is it their opinion that this
   document is needed, clearly written, complete, correctly designed, and ready
   to be handed off to the responsible Area Director?

_Yes._

10. Several IETF Areas have assembled [lists of common issues that their
    reviewers encounter][6]. For which areas have such issues been identified
    and addressed? For which does this still need to happen in subsequent
    reviews?

_N/A._

11. What type of RFC publication is being requested on the IETF stream ([Best
    Current Practice][12], [Proposed Standard, Internet Standard][13],
    [Informational, Experimental or Historic][14])? Why is this the proper type
    of RFC? Do all Datatracker state attributes correctly reflect this intent?

_Proposed Standard. This is appropriate for a new protocol specification with some implementation._

12. Have reasonable efforts been made to remind all authors of the intellectual
    property rights (IPR) disclosure obligations described in [BCP 79][7]? To
    the best of your knowledge, have all required disclosures been filed? If
    not, explain why. If yes, summarize any relevant discussion, including links
    to publicly-available messages when applicable.

_Yes; they have been reminded._

13. Has each author, editor, and contributor shown their willingness to be
    listed as such? If the total number of authors and editors on the front page
    is greater than five, please provide a justification.

_Yes._

14. Document any remaining I-D nits in this document. Simply running the [idnits
    tool][8] is not enough; please review the ["Content Guidelines" on
    authors.ietf.org][15]. (Also note that the current idnits tool generates
    some incorrect warnings; a rewrite is underway.)

See discussion of downreferences.

15. Should any informative references be normative or vice-versa? See the [IESG
    Statement on Normative and Informative References][16].

RFC5861 can be made informative.

16. List any normative references that are not freely available to anyone. Did
    the community have sufficient access to review any such normative
    references?

_N/A._

17. Are there any normative downward references (see [RFC 3967][9] and [BCP
    97][10]) that are not already listed in the [DOWNREF registry][17]? If so,
    list them.

RFC5861 is a downwards reference, but can be made informative.

18. Are there normative references to documents that are not ready to be
    submitted to the IESG for publication or are otherwise in an unclear state?
    If so, what is the plan for their completion?

_No._

19. Will publication of this document change the status of any existing RFCs? If
    so, does the Datatracker metadata correctly reflect this and are those RFCs
    listed on the title page, in the abstract, and discussed in the
    introduction? If not, explain why and point to the part of the document
    where the relationship of this document to these other RFCs is discussed.

_No._

20. Describe the document shepherd's review of the IANA considerations section,
    especially with regard to its consistency with the body of the document.
    Confirm that all aspects of the document requiring IANA assignments are
    associated with the appropriate reservations in IANA registries. Confirm
    that any referenced IANA registries have been clearly identified. Confirm
    that each newly created IANA registry specifies its initial contents,
    allocations procedures, and a reasonable name (see [RFC 8126][11]).

_The requests appear to be correct._

21. List any new IANA registries that require Designated Expert Review for
    future allocations. Are the instructions to the Designated Expert clear?
    Please include suggestions of designated experts, if appropriate.

_N/A._


[1]: https://www.ietf.org/about/groups/iesg/
[2]: https://www.rfc-editor.org/rfc/rfc4858.html
[3]: https://www.rfc-editor.org/rfc/rfc7942.html
[4]: https://wiki.ietf.org/group/ops/yang-review-tools
[5]: https://www.rfc-editor.org/rfc/rfc8342.html
[6]: https://wiki.ietf.org/group/iesg/ExpertTopics
[7]: https://www.rfc-editor.org/info/bcp79
[8]: https://www.ietf.org/tools/idnits/
[9]: https://www.rfc-editor.org/rfc/rfc3967.html
[10]: https://www.rfc-editor.org/info/bcp97
[11]: https://www.rfc-editor.org/rfc/rfc8126.html
[12]: https://www.rfc-editor.org/rfc/rfc2026.html#section-5
[13]: https://www.rfc-editor.org/rfc/rfc2026.html#section-4.1
[14]: https://www.rfc-editor.org/rfc/rfc2026.html#section-4.2
[15]: https://authors.ietf.org/en/content-guidelines-overview
[16]: https://www.ietf.org/about/groups/iesg/statements/normative-informative-references/
[17]: https://datatracker.ietf.org/doc/downref/

